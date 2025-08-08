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

"""Tests for the legacy rfc822 based [de]serializer."""


import datetime
from io import BytesIO
from textwrap import dedent

import testtools
from pytz import utc

from oops_datedir_repo.serializer_rfc822 import read, to_chunks, write


class TestParsing(testtools.TestCase):

    def test_read(self):
        """Test ErrorReport.read()."""
        fp = BytesIO(
            dedent(
                """\
            Oops-Id: OOPS-A0001
            Exception-Type: NotFound
            Exception-Value: error message
            Date: 2005-04-01T00:00:00+00:00
            Topic: IFoo:+foo-template
            User: Sample User
            URL: http://localhost:9000/foo
            Duration: 42

            HTTP_USER_AGENT=Mozilla/5.0
            HTTP_REFERER=http://localhost:9000/
            name%3Dfoo=hello%0Aworld

            00001-00005@store_a SELECT 1
            00005-00010@store_b SELECT 2

            traceback-text"""
            ).encode("UTF-8")
        )
        report = read(fp)
        self.assertEqual(report["id"], "OOPS-A0001")
        self.assertEqual(report["type"], "NotFound")
        self.assertEqual(report["value"], "error message")
        self.assertEqual(
            report["time"], datetime.datetime(2005, 4, 1, tzinfo=utc)
        )
        self.assertEqual(report["topic"], "IFoo:+foo-template")
        self.assertEqual(report["tb_text"], "traceback-text")
        self.assertEqual(report["username"], "Sample User")
        self.assertEqual(report["url"], "http://localhost:9000/foo")
        self.assertEqual(report["duration"], 42)
        self.assertEqual(
            {
                "HTTP_USER_AGENT": "Mozilla/5.0",
                "HTTP_REFERER": "http://localhost:9000/",
                "name=foo": "hello\nworld",
            },
            report["req_vars"],
        )
        self.assertEqual(len(report["timeline"]), 2)
        self.assertEqual(report["timeline"][0], [1, 5, "store_a", "SELECT 1"])
        self.assertEqual(report["timeline"][1], [5, 10, "store_b", "SELECT 2"])

    def test_read_blankline_req_vars(self):
        """Test ErrorReport.read() for old logs with a blankline between
        reqvars."""
        fp = BytesIO(
            dedent(
                """\
            Oops-Id: OOPS-A0001
            Exception-Type: NotFound
            Exception-Value: error message
            Date: 2005-04-01T00:00:00+00:00
            Topic: IFoo:+foo-template
            User: Sample User
            URL: http://localhost:9000/foo
            Duration: 42

            HTTP_USER_AGENT=Mozilla/5.0

            HTTP_REFERER=http://localhost:9000/
            name%3Dfoo=hello%0Aworld

            00001-00005@store_a SELECT 1 = 2
            00005-00010@store_b SELECT 2

            traceback-text
                foo/bar"""
            ).encode("UTF-8")
        )
        report = read(fp)
        self.assertEqual(report["id"], "OOPS-A0001")
        self.assertEqual(
            {
                "HTTP_USER_AGENT": "Mozilla/5.0",
                "HTTP_REFERER": "http://localhost:9000/",
                "name=foo": "hello\nworld",
            },
            report["req_vars"],
        )
        self.assertEqual(len(report["timeline"]), 2)
        self.assertEqual(
            report["timeline"][0], [1, 5, "store_a", "SELECT 1 = 2"]
        )
        self.assertEqual(report["timeline"][1], [5, 10, "store_b", "SELECT 2"])
        self.assertEqual(report["tb_text"], "traceback-text\n    foo/bar")

    def test_read_no_store_id(self):
        """Test ErrorReport.read() for old logs with no store_id."""
        fp = BytesIO(
            dedent(
                """\
            Oops-Id: OOPS-A0001
            Exception-Type: NotFound
            Exception-Value: error message
            Date: 2005-04-01T00:00:00+00:00
            Topic: IFoo:+foo-template
            User: Sample User
            URL: http://localhost:9000/foo
            Duration: 42

            HTTP_USER_AGENT=Mozilla/5.0
            HTTP_REFERER=http://localhost:9000/
            name%3Dfoo=hello%0Aworld

            00001-00005 SELECT 1
            00005-00010 SELECT 2

            traceback-text"""
            ).encode("UTF-8")
        )
        report = read(fp)
        self.assertEqual(report["id"], "OOPS-A0001")
        self.assertEqual(report["type"], "NotFound")
        self.assertEqual(report["value"], "error message")
        self.assertEqual(
            report["time"], datetime.datetime(2005, 4, 1, tzinfo=utc)
        )
        self.assertEqual(report["topic"], "IFoo:+foo-template")
        self.assertEqual(report["tb_text"], "traceback-text")
        self.assertEqual(report["username"], "Sample User")
        self.assertEqual(report["url"], "http://localhost:9000/foo")
        self.assertEqual(report["duration"], 42)
        self.assertEqual(
            {
                "HTTP_USER_AGENT": "Mozilla/5.0",
                "HTTP_REFERER": "http://localhost:9000/",
                "name=foo": "hello\nworld",
            },
            report["req_vars"],
        )
        self.assertEqual(len(report["timeline"]), 2)
        self.assertEqual(report["timeline"][0], [1, 5, None, "SELECT 1"])
        self.assertEqual(report["timeline"][1], [5, 10, None, "SELECT 2"])

    def test_read_branch_nick_revno(self):
        """Test ErrorReport.read()."""
        fp = BytesIO(
            dedent(
                """\
            Oops-Id: OOPS-A0001
            Exception-Type: NotFound
            Exception-Value: error message
            Date: 2005-04-01T00:00:00+00:00
            User: Sample User
            URL: http://localhost:9000/foo
            Duration: 42
            Branch: mybranch
            Revision: 45

            HTTP_USER_AGENT=Mozilla/5.0
            HTTP_REFERER=http://localhost:9000/
            name%3Dfoo=hello%0Aworld

            00001-00005@store_a SELECT 1
            00005-00010@store_b SELECT 2

            traceback-text"""
            ).encode("UTF-8")
        )
        report = read(fp)
        self.assertEqual(report["branch_nick"], "mybranch")
        self.assertEqual(report["revno"], "45")

    def test_read_duration_as_string(self):
        """Test ErrorReport.read()."""
        fp = BytesIO(
            dedent(
                """\
            Oops-Id: OOPS-A0001
            Duration: foo/bar

            """
            ).encode("UTF-8")
        )
        report = read(fp)
        self.assertEqual(report["duration"], -1)

    def test_read_reporter(self):
        """Test ErrorReport.read()."""
        fp = BytesIO(
            dedent(
                """\
            Oops-Id: OOPS-A0001
            Oops-Reporter: foo/bar

            """
            ).encode("UTF-8")
        )
        report = read(fp)
        self.assertEqual(report["reporter"], "foo/bar")

    def test_read_pageid_to_topic(self):
        """Test ErrorReport.read()."""
        fp = BytesIO(
            dedent(
                """\
            Oops-Id: OOPS-A0001
            Page-Id: IFoo:+foo-template

            """
            ).encode("UTF-8")
        )
        report = read(fp)
        self.assertEqual(report["topic"], "IFoo:+foo-template")

    def test_read_informational_read(self):
        """Test ErrorReport.read()."""
        fp = BytesIO(
            dedent(
                """\
            Oops-Id: OOPS-A0001
            Informational: True

            """
            ).encode("UTF-8")
        )
        report = read(fp)
        self.assertEqual("True", report["informational"])

    def test_read_no_informational_no_key(self):
        """Test ErrorReport.read()."""
        fp = BytesIO(
            dedent(
                """\
            Oops-Id: OOPS-A0001

            """
            ).encode("UTF-8")
        )
        report = read(fp)
        self.assertFalse("informational" in report)

    def test_minimal_oops(self):
        # If we get a crazy-small oops, we can read it sensibly.  Because there
        # is existing legacy code, all keys are filled in with None, [] or {}
        # rather than being empty.
        fp = BytesIO(
            dedent(
                """\
            Oops-Id: OOPS-A0001
            """
            ).encode("UTF-8")
        )
        report = read(fp)
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

    def test_write_file(self):
        output = BytesIO()
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
        write(report, output)
        self.assertEqual(
            output.getvalue().decode("UTF-8"),
            dedent(
                """\
            Oops-Id: OOPS-A0001
            Exception-Type: NotFound
            Exception-Value: error message
            Date: 2005-04-01T00:00:00+00:00
            Page-Id: IFoo:+foo-template
            Branch: mybranch
            Revision: 45
            User: Sample User
            URL: http://localhost:9000/foo
            Duration: 42
            Informational: False

            HTTP_USER_AGENT=Mozilla/5.0
            HTTP_REFERER=http://localhost:9000/
            name%3Dfoo=hello%0Aworld

            00001-00005@store_a SELECT 1
            00005-00010@store_b SELECT 2

            traceback-text"""
            ),
        )

    def test_to_chunks(self):
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
        self.assertEqual(
            [
                b"Oops-Id: OOPS-A0001\n",
                b"Exception-Type: NotFound\n",
                b"Exception-Value: error message\n",
                b"Date: 2005-04-01T00:00:00+00:00\n",
                b"Page-Id: IFoo:+foo-template\n",
                b"Branch: mybranch\n",
                b"Revision: 45\n",
                b"User: Sample User\n",
                b"URL: http://localhost:9000/foo\n",
                b"Duration: 42\n",
                b"Informational: False\n",
                b"\n",
                b"HTTP_USER_AGENT=Mozilla/5.0\n",
                b"HTTP_REFERER=http://localhost:9000/\n",
                b"name%3Dfoo=hello%0Aworld\n",
                b"\n",
                b"00001-00005@store_a SELECT 1\n",
                b"00005-00010@store_b SELECT 2\n",
                b"\n",
                b"traceback-text",
            ],
            to_chunks(report),
        )

    def test_minimal_oops(self):
        # An oops with just an id, though arguably crazy, is written
        # sensibly.
        report = {"id": "OOPS-1234"}
        self.assertEqual([b"Oops-Id: OOPS-1234\n", b"\n"], to_chunks(report))

    def test_reporter(self):
        report = {"reporter": "foo", "id": "bar"}
        self.assertEqual(
            [
                b"Oops-Id: bar\n",
                b"Oops-Reporter: foo\n",
                b"\n",
            ],
            to_chunks(report),
        )

    def test_bad_strings(self):
        # Because of the rfc822 limitations, not all strings can be supported
        # in this format - particularly in headers... so all header strings are
        # passed through an escape process.
        report = {"id": "\xeafoo"}
        self.assertEqual(
            [
                b"Oops-Id: \\xeafoo\n",
                b"\n",
            ],
            to_chunks(report),
        )
        report = {"id": "\xeafoo"}
        self.assertEqual(
            [
                b"Oops-Id: \\xeafoo\n",
                b"\n",
            ],
            to_chunks(report),
        )

    def test_write_reqvars_dict(self):
        report = {
            "req_vars": {
                "HTTP_USER_AGENT": "Mozilla/5.0",
                "HTTP_REFERER": "http://localhost:9000/",
                "name=foo": "hello\nworld",
            },
            "id": "OOPS-1234",
        }
        self.assertEqual(
            [
                b"Oops-Id: OOPS-1234\n",
                b"\n",
                b"HTTP_REFERER=http://localhost:9000/\n",
                b"HTTP_USER_AGENT=Mozilla/5.0\n",
                b"name%3Dfoo=hello%0Aworld\n",
                b"\n",
            ],
            to_chunks(report),
        )

    def test_to_chunks_enhanced_timeline(self):
        # New timeline will have 5-tuples with a backtrace. The rfc822 format
        # doesn't have anywhere to put this, so its ignored, but the rest is
        # saved.
        report = {
            "id": "OOPS-1234",
            "timeline": [
                (0, 1, "foo", "bar", "quux"),
            ],
        }
        self.assertEqual(
            [
                b"Oops-Id: OOPS-1234\n",
                b"\n",
                b"00000-00001@foo bar\n",
                b"\n",
            ],
            to_chunks(report),
        )
