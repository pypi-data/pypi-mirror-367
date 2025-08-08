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

"""Tests for the generic serialization support."""


import bz2
import datetime
from io import BytesIO

import testtools
from pytz import utc

from oops_datedir_repo.serializer import read
from oops_datedir_repo.serializer_bson import dumps
from oops_datedir_repo.serializer_rfc822 import write


class TestParsing(testtools.TestCase):

    source_dict = {
        "id": "OOPS-A0001",
        "type": "NotFound",
        "value": "error message",
        "time": datetime.datetime(2005, 4, 1, tzinfo=utc),
        "topic": "IFoo:+foo-template",
        "tb_text": "traceback\ntext\n",
        "username": "Sample User",
        "url": "http://localhost:9000/foo",
        "duration": 42.0,
        "req_vars": {
            "HTTP_USER_AGENT": "Mozilla/5.0",
            "HTTP_REFERER": "http://localhost:9000/",
            "name=foo": "hello\nworld",
        },
        "timeline": [
            [1, 5, "store_a", "SELECT 1"],
            [5, 10, "store_b", "SELECT 2"],
        ],
    }
    expected_dict = dict(source_dict)
    # Unsupplied but filled on read
    expected_dict["branch_nick"] = None
    expected_dict["revno"] = None

    def test_read_detect_rfc822(self):
        source_file = BytesIO()
        write(dict(self.source_dict), source_file)
        source_file.seek(0)
        self.assertEqual(self.expected_dict, read(source_file))

    def test_read_detect_bson(self):
        source_file = BytesIO()
        source_file.write(dumps(dict(self.source_dict)))
        source_file.seek(0)
        self.assertEqual(self.expected_dict, read(source_file))

    def test_read_detect_bz2(self):
        source_file = BytesIO()
        source_file.write(bz2.compress(dumps(dict(self.source_dict))))
        source_file.seek(0)
        self.assertEqual(self.expected_dict, read(source_file))

    def test_ioerror_on_empty_oops(self):
        source_file = BytesIO()
        self.assertRaises(IOError, read, source_file)
