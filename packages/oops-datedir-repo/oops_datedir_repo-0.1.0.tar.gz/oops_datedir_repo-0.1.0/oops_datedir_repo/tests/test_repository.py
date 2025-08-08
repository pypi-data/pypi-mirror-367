# Copyright (c) 2010, 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU Lesser General Public License version 3 (see the file LICENSE).

"""Tests for the date-directory based repository."""


import datetime
import os.path
import stat
from hashlib import md5

import testtools
from fixtures import Fixture, MonkeyPatch, TempDir
from pytz import utc
from testtools.matchers import Equals, raises

from oops_datedir_repo import DateDirRepo, anybson, serializer_bson


class HasUnixPermissions:

    def __init__(self, wanted_permission):
        self.wanted_permission = wanted_permission

    def match(self, path):
        st = os.stat(path)
        # Get only the permission bits from this mode.
        file_permission = stat.S_IMODE(st.st_mode)
        return Equals(self.wanted_permission).match(file_permission)

    def __str__(self):
        # TODO: might be nice to split out the bits in future, format nicely
        # etc. Should also move this into testtools.
        return "HasUnixPermissions(0%o)" % self.wanted_permission


class UMaskFixture(Fixture):
    """Set a umask temporarily."""

    def __init__(self, mask):
        super().__init__()
        self.umask_permission = mask

    def setUp(self):
        super().setUp()
        old_umask = os.umask(self.umask_permission)
        self.addCleanup(os.umask, old_umask)


class TestDateDirRepo(testtools.TestCase):

    def test_publish_permissions_hashnames(self):
        repo = DateDirRepo(self.useFixture(TempDir()).path, stash_path=True)
        report = {"id": "OOPS-91T1"}
        now = datetime.datetime(2006, 4, 1, 0, 30, 0, tzinfo=utc)

        # Set up default file creation mode to rwx------ as some restrictive
        # servers do.
        self.useFixture(UMaskFixture(stat.S_IRWXG | stat.S_IRWXO))
        repo.publish(report, now)
        # Check errorfile and directory are set with the correct permission:
        # rw-r--r--
        file_perms = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
        has_file_permission = HasUnixPermissions(file_perms)
        has_dir_permission = HasUnixPermissions(
            file_perms | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )
        self.assertThat(report["datedir_repo_filepath"], has_file_permission)
        self.assertThat(repo.root + "/2006-04-01", has_dir_permission)

    def test_default_serializer_bson(self):
        repo = DateDirRepo(self.useFixture(TempDir()).path)
        self.assertEqual(serializer_bson, repo.serializer)

    def test_settable_serializer(self):
        an_object = object()
        repo = DateDirRepo(self.useFixture(TempDir()).path, an_object)
        self.assertEqual(an_object, repo.serializer)

    def test_publish_via_hash(self):
        repo = DateDirRepo(self.useFixture(TempDir()).path)
        now = datetime.datetime(2006, 4, 1, 0, 30, 0, tzinfo=utc)
        # Note the presence of 'id' in the report: this is included in the hash
        # calculation (because there is no reason not to - we don't promise
        # that reports only differing by id will be assigned the same id even
        # when publishing by hash: the hashing is a way to get meaningfully
        # unique ids, not a way to optimise similar reports [as all reports
        # should have unique timestamps anyway...]
        report = {"id": "ignored", "time": now}
        # NB: bson output depends on dict order, so the resulting hash can be
        # machine specific. This is fine because its merely a strategy to get
        # unique ids, and after creating the id it is preserved in what is
        # written to disk: we don't need it to be deterministic across
        # machines / instances.
        expected_md5 = md5(serializer_bson.dumps(report)).hexdigest()
        expected_id = "OOPS-%s" % expected_md5
        self.assertEqual([expected_id], repo.publish(report, now))
        # The file on disk should match the given id.
        with open(repo.root + "/2006-04-01/" + expected_id, "rb") as fp:
            # And the content serialized should include the id.
            self.assertEqual(
                {"id": expected_id, "time": now}, anybson.loads(fp.read())
            )

    def test_multiple_hash_publications(self):
        # The initial datedir hash code could only publish one oops a day.
        repo = DateDirRepo(self.useFixture(TempDir()).path)
        now = datetime.datetime(2006, 4, 1, 0, 30, 0, tzinfo=utc)
        report = {"time": now}
        repo.publish(report, now)
        report2 = {"time": now, "foo": "bar"}
        repo.publish(report2, now)

    def test_publish_existing_id(self):
        # oops_amqp wants to publish to a DateDirRepo but already has an id
        # that the user has been told about.
        repo = DateDirRepo(self.useFixture(TempDir()).path, inherit_id=True)
        now = datetime.datetime(2006, 4, 1, 0, 30, 0, tzinfo=utc)
        report = {"time": now, "id": "45"}
        self.assertEqual(["45"], repo.publish(dict(report), now))
        # And to be sure, check the file on disk.
        dir = repo.root + "/2006-04-01/"
        files = os.listdir(dir)
        with open(dir + files[0], "rb") as fp:
            self.assertEqual(report, anybson.loads(fp.read()))

    def test_publish_existing_id_lognamer(self):
        # The id reuse and file allocation strategies should be separate.
        repo = DateDirRepo(
            self.useFixture(TempDir()).path, inherit_id=True, stash_path=True
        )
        now = datetime.datetime(2006, 4, 1, 0, 30, 0, tzinfo=utc)
        report = {"time": now, "id": "45"}
        published_report = dict(report)
        self.assertEqual(["45"], repo.publish(published_report, now))
        #  The file on disk should have the supplied id.
        with open(published_report["datedir_repo_filepath"], "rb") as fp:
            self.assertEqual(report, anybson.loads(fp.read()))

    def test_publish_add_path(self):
        # oops_tools wants to publish to both disk (via DateDirRepo) and a
        # database; the database wants the path of the OOPS report on disk.
        # Putting it in the (original) report allows the database publisher to
        # read that out. This is a little ugly, but there are many worse ways
        # to do it, and no known better ones that don't make the core protocol
        # too tightly bound to disk publishing.
        repo = DateDirRepo(
            self.useFixture(TempDir()).path, stash_path=True, inherit_id=True
        )
        now = datetime.datetime(2006, 4, 1, 0, 30, 0, tzinfo=utc)
        report = {"time": now, "id": "45"}
        expected_disk_report = dict(report)
        self.assertEqual(["45"], repo.publish(report, now))
        dir = repo.root + "/2006-04-01/"
        files = os.listdir(dir)
        expected_path = dir + files[0]
        self.assertEqual(expected_path, report["datedir_repo_filepath"])
        with open(expected_path, "rb") as fp:
            self.assertEqual(expected_disk_report, anybson.loads(fp.read()))

    def test_republish_not_published(self):
        # If an OOPS being republished is not republished, it is preserved on
        # disk.
        repo = DateDirRepo(self.useFixture(TempDir()).path)
        now = datetime.datetime(2006, 4, 1, 0, 30, 0, tzinfo=utc)
        report = {"time": now}
        repo.publish(report, now)
        dir = repo.root + "/2006-04-01/"
        files = os.listdir(dir)
        expected_path = dir + files[0]
        oopses = []
        # append() returns None
        publisher = oopses.append
        repo.republish(publisher)
        self.assertTrue(os.path.isfile(expected_path))
        self.assertEqual(1, len(oopses))

    def test_republish_ignores_current_dot_tmp_files(self):
        # .tmp files are in-progress writes and not to be touched.
        repo = DateDirRepo(self.useFixture(TempDir()).path, stash_path=True)
        report = {}
        repo.publish(report)
        finished_path = report["datedir_repo_filepath"]
        inprogress_path = finished_path + ".tmp"
        # Move the file to a temp path, simulating an in-progress write.
        os.rename(finished_path, inprogress_path)
        oopses = []
        publisher = oopses.append
        repo.republish(publisher)
        self.assertTrue(os.path.isfile(inprogress_path))
        self.assertEqual([], oopses)

    def test_republish_ignores_empty_files(self):
        # 0 length files are generated by old versions of oops libraries or
        # third party implementations that don't use .tmp staging, and we
        # should skip over them..
        repo = DateDirRepo(self.useFixture(TempDir()).path, stash_path=True)
        report = {}
        repo.publish(report)
        finished_path = report["datedir_repo_filepath"]
        # Make the file zero-length.
        with open(finished_path, "wb") as report_file:
            os.ftruncate(report_file.fileno(), 0)
        oopses = []
        publisher = oopses.append
        repo.republish(publisher)
        self.assertTrue(os.path.isfile(finished_path))
        self.assertEqual([], oopses)

    def test_republish_republishes_and_removes(self):
        # When a report is republished it is then removed from disk.
        repo = DateDirRepo(self.useFixture(TempDir()).path, stash_path=True)
        report = {}
        repo.publish(report)
        finished_path = report["datedir_repo_filepath"]
        oopses = []

        def publish(report):
            oopses.append(report)
            return [report["id"]]

        repo.republish(publish)
        self.assertFalse(os.path.isfile(finished_path))
        self.assertEqual(1, len(oopses))

    def test_republish_cleans_empty_old_directories(self):
        # An empty old datedir directory cannot get new reports in it, so gets
        # cleaned up to keep the worker efficient.
        repo = DateDirRepo(self.useFixture(TempDir()).path)
        os.mkdir(repo.root + "/2006-04-12")
        repo.republish([].append)
        self.assertFalse(os.path.exists(repo.root + "/2006-04-12"))

    def test_republish_removes_old_dot_tmp_files(self):
        # A .tmp file more than 24 hours old is probably never going to get
        # renamed into place, so we just unlink it.
        repo = DateDirRepo(self.useFixture(TempDir()).path)
        now = datetime.datetime(2006, 4, 1, 0, 30, 0, tzinfo=utc)
        report = {"time": now}
        repo.publish(report, now)
        dir = repo.root + "/2006-04-01/"
        files = os.listdir(dir)
        finished_path = dir + files[0]
        inprogress_path = finished_path + ".tmp"
        os.rename(finished_path, inprogress_path)
        oopses = []
        publisher = oopses.append
        repo.republish(publisher)
        self.assertFalse(os.path.isfile(inprogress_path))
        self.assertEqual([], oopses)

    def test_republish_removes_old_empty_files(self):
        # 0 length files are generated by old versions of oops libraries or
        # third party implementations that don't use .tmp staging, and they
        # are unlikely to ever get fleshed out when more than 24 hours old,
        # so we prune them.
        repo = DateDirRepo(self.useFixture(TempDir()).path)
        now = datetime.datetime(2006, 4, 1, 0, 30, 0, tzinfo=utc)
        report = {"time": now}
        repo.publish(report, now)
        dir = repo.root + "/2006-04-01/"
        files = os.listdir(dir)
        finished_path = dir + files[0]
        # Make the file zero-length.
        with open(finished_path, "wb") as report_file:
            os.ftruncate(report_file.fileno(), 0)
        oopses = []
        publisher = oopses.append
        repo.republish(publisher)
        self.assertFalse(os.path.isfile(finished_path))
        self.assertEqual([], oopses)

    def test_republish_no_error_non_datedir(self):
        # The present of a non datedir directory in a datedir repo doesn't
        # break things.
        repo = DateDirRepo(self.useFixture(TempDir()).path)
        os.mkdir(repo.root + "/foo")
        repo.republish([].append)

    def test_republish_ignores_metadata_dir(self):
        # The metadata directory is never pruned
        repo = DateDirRepo(self.useFixture(TempDir()).path)
        os.mkdir(repo.root + "/metadata")
        repo.republish([].append)
        self.assertTrue(os.path.exists(repo.root + "/metadata"))

    def test_get_config_value(self):
        # Config values can be asked for from the repository.
        repo = DateDirRepo(self.useFixture(TempDir()).path)
        pruned = datetime.datetime(2006, 4, 1, 0, 30, 0, tzinfo=utc)
        repo.set_config("pruned-until", pruned)
        # Fresh instance, no memory tricks.
        repo = DateDirRepo(repo.root)
        self.assertEqual(pruned, repo.get_config("pruned-until"))

    def test_set_config_value(self):
        # Config values are just keys in a bson document.
        repo = DateDirRepo(self.useFixture(TempDir()).path)
        pruned = datetime.datetime(2006, 4, 1, 0, 30, 0, tzinfo=utc)
        repo.set_config("pruned-until", pruned)
        with open(repo.root + "/metadata/config.bson", "rb") as config_file:
            from_bson = anybson.loads(config_file.read())
        self.assertEqual({"pruned-until": pruned}, from_bson)

    def test_set_config_preserves_other_values(self):
        # E.g. setting 'a' does not affect 'b'
        repo = DateDirRepo(self.useFixture(TempDir()).path)
        repo.set_config("b", "b-value")
        repo = DateDirRepo(repo.root)
        repo.set_config("a", "a-value")
        with open(repo.root + "/metadata/config.bson", "rb") as config_file:
            from_bson = anybson.loads(config_file.read())
        self.assertEqual({"a": "a-value", "b": "b-value"}, from_bson)

    def test_oldest_date_no_contents(self):
        repo = DateDirRepo(self.useFixture(TempDir()).path)
        self.assertThat(
            lambda: repo.oldest_date(),
            raises(ValueError("No OOPSes in repository.")),
        )

    def test_oldest_date_is_oldest(self):
        repo = DateDirRepo(self.useFixture(TempDir()).path)
        os.mkdir(repo.root + "/2006-04-12")
        os.mkdir(repo.root + "/2006-04-13")
        self.assertEqual(datetime.date(2006, 4, 12), repo.oldest_date())

    def test_prune_unreferenced_no_oopses(self):
        # This shouldn't crash.
        repo = DateDirRepo(self.useFixture(TempDir()).path, inherit_id=True)
        now = datetime.datetime(2006, 4, 1, 0, 30, 0, tzinfo=utc)
        old = now - datetime.timedelta(weeks=1)
        repo.prune_unreferenced(old, now, [])

    def test_prune_unreferenced_no_references(self):
        # When there are no references, everything specified is zerged.
        repo = DateDirRepo(self.useFixture(TempDir()).path, inherit_id=True)
        now = datetime.datetime(2006, 4, 1, 0, 30, 0, tzinfo=utc)
        old = now - datetime.timedelta(weeks=1)
        report = {"time": now - datetime.timedelta(hours=5)}
        repo.publish(report, report["time"])
        repo.prune_unreferenced(old, now, [])
        self.assertThat(lambda: repo.oldest_date(), raises(ValueError))

    def test_prune_unreferenced_outside_dates_kept(self):
        # Pruning only affects stuff in the datedirs selected by the dates.
        repo = DateDirRepo(
            self.useFixture(TempDir()).path, inherit_id=True, stash_path=True
        )
        now = datetime.datetime(2006, 4, 1, 0, 30, 0, tzinfo=utc)
        old = now - datetime.timedelta(weeks=1)
        before = {"time": old - datetime.timedelta(minutes=1)}
        after = {"time": now + datetime.timedelta(minutes=1)}
        repo.publish(before, before["time"])
        repo.publish(after, after["time"])
        repo.prune_unreferenced(old, now, [])
        self.assertTrue(os.path.isfile(before["datedir_repo_filepath"]))
        self.assertTrue(os.path.isfile(after["datedir_repo_filepath"]))

    def test_prune_referenced_inside_dates_kept(self):
        repo = DateDirRepo(
            self.useFixture(TempDir()).path, inherit_id=True, stash_path=True
        )
        now = datetime.datetime(2006, 4, 1, 0, 30, 0, tzinfo=utc)
        old = now - datetime.timedelta(weeks=1)
        report = {"id": "foo", "time": now - datetime.timedelta(minutes=1)}
        repo.publish(report, report["time"])
        repo.prune_unreferenced(old, now, ["foo"])
        self.assertTrue(os.path.isfile(report["datedir_repo_filepath"]))

    def test_prune_report_midnight_gets_invalid_timed_reports(self):
        # If a report has a wonky or missing time, pruning treats it as being
        # timed on midnight of the datedir day it is on.
        repo = DateDirRepo(self.useFixture(TempDir()).path, stash_path=True)
        now = datetime.datetime(2006, 4, 1, 0, 1, 0, tzinfo=utc)
        old = now - datetime.timedelta(minutes=2)
        badtime = {"time": now - datetime.timedelta(weeks=2)}
        missingtime = {}
        strtime = {"time": "some-time"}
        repo.publish(badtime, now)
        repo.publish(missingtime, now)
        repo.publish(strtime, now)
        repo.prune_unreferenced(old, now, [])
        self.assertThat(lambda: repo.oldest_date(), raises(ValueError))

    def test_concurrent_dir_creation(self):
        # Simulate isdir/makedirs race condition where concurrent processes
        # test and see no existing dir, all try to create it, and first process
        # wins causing others to fail.
        def fake_isdir(path):
            return False

        self.useFixture(MonkeyPatch("os.path.isdir", fake_isdir))
        repo = DateDirRepo(self.useFixture(TempDir()).path)
        repo.publish({"id": "1"})
        repo.publish({"id": "2"})

    def test_oops_tmp_is_closed(self):

        # Collect opened OOPS-*.tmp files.
        oops_tmp = []
        open_real = open

        def open_intercept(path, *a, **k):
            f = open_real(path, *a, **k)
            name = os.path.basename(path)
            if name.startswith("OOPS-") and name.endswith(".tmp"):
                oops_tmp.append(f)
            return f

        open_name = "builtins.open"
        self.useFixture(MonkeyPatch(open_name, open_intercept))

        repo = DateDirRepo(self.useFixture(TempDir()).path)
        repo.publish({"id": "1"})
        self.assertEqual(1, len(oops_tmp))
        self.assertTrue(oops_tmp[0].closed)
