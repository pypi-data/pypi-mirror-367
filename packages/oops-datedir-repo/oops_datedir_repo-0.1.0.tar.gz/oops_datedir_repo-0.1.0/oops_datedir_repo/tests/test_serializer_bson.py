# Copyright (c) 2011, Canonical Ltd
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


"""Tests for bson based serialization."""


import datetime
from io import BytesIO

import testtools
from pytz import utc

from oops_datedir_repo import anybson as bson
from oops_datedir_repo.serializer_bson import dumps, read


class TestParsing(testtools.TestCase):

    def test_read(self):
        source_dict = {
            "id": "OOPS-A0001",
            "type": "NotFound",
            "value": "error message",
            "time": datetime.datetime(2005, 4, 1, tzinfo=utc),
            "topic": "IFoo:+foo-template",
            "tb_text": "traceback\ntext\n",
            "username": "Sample User",
            "url": "http://localhost:9000/foo",
            "duration": 42,
            "req_vars": [
                ["HTTP_USER_AGENT", "Mozilla/5.0"],
                ["HTTP_REFERER", "http://localhost:9000/"],
                ["name=foo", "hello\nworld"],
            ],
            "timeline": [
                [1, 5, "store_a", "SELECT 1"],
                [5, 10, "store_b", "SELECT 2"],
            ],
        }
        source_file = BytesIO(bson.dumps(source_dict))
        expected_dict = dict(source_dict)
        # Unsupplied but filled on read
        expected_dict["branch_nick"] = None
        expected_dict["revno"] = None
        report = read(source_file)
        self.assertEqual(expected_dict, report)

    def test_minimal_oops(self):
        # If we get a crazy-small oops, we can read it sensibly.  Because there
        # is existing legacy code, all keys are filled in with None, [] rather
        # than being empty.
        source_dict = {
            "id": "OOPS-A0001",
        }
        source_file = BytesIO(bson.dumps(source_dict))
        report = read(source_file)
        self.assertEqual(report["id"], "OOPS-A0001")
        self.assertEqual(report["type"], None)
        self.assertEqual(report["value"], None)
        self.assertEqual(report["time"], None)
        self.assertEqual(report["topic"], None)
        self.assertEqual(report["tb_text"], "")
        self.assertEqual(report["username"], None)
        self.assertEqual(report["url"], None)
        self.assertEqual(report["duration"], -1)
        self.assertEqual(len(report["req_vars"]), 0)
        self.assertEqual(len(report["timeline"]), 0)
        self.assertEqual(report["branch_nick"], None)
        self.assertEqual(report["revno"], None)


class TestSerializing(testtools.TestCase):

    def test_dumps(self):
        report = {
            "id": "OOPS-A0001",
            "type": "NotFound",
            "value": "error message",
            "time": datetime.datetime(2005, 4, 1, 0, 0, 0, tzinfo=utc),
            "topic": "IFoo:+foo-template",
            "tb_text": "traceback-text",
            "username": "Sample User",
            "url": "http://localhost:9000/foo",
            "duration": 42,
            "req_vars": [
                ("HTTP_USER_AGENT", "Mozilla/5.0"),
                ("HTTP_REFERER", "http://localhost:9000/"),
                ("name=foo", "hello\nworld"),
            ],
            "timeline": [
                (1, 5, "store_a", "SELECT 1"),
                (5, 10, "store_b", "SELECT\n2"),
            ],
            "informational": False,
            "branch_nick": "mybranch",
            "revno": "45",
        }
        self.assertEqual(dumps(report), bson.dumps(report))

    def test_minimal_oops(self):
        # An oops with just an id, though arguably crazy, is written
        # sensibly.
        report = {"id": "OOPS-1234"}
        self.assertEqual(dumps(report), bson.dumps(report))

    def test_bad_strings(self):
        report = {"id": "\xeafoo"}
        self.assertEqual(dumps(report), bson.dumps(report))
