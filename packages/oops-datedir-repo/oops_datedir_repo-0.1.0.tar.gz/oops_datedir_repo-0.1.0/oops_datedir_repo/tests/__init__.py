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

"""Tests for oops_datedir_repo."""


from unittest import TestLoader


def test_suite():
    test_mod_names = [
        "repository",
        "serializer",
        "serializer_bson",
        "serializer_rfc822",
    ]
    return TestLoader().loadTestsFromNames(
        ["oops_datedir_repo.tests.test_" + name for name in test_mod_names]
    )
