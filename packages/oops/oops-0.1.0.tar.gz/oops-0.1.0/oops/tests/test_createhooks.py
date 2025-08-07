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

"""Tests for the oops config module."""


import datetime
import socket
import sys

import testtools

from oops.createhooks import (
    attach_date,
    attach_exc_info,
    attach_hostname,
    copy_reporter,
    copy_topic,
    copy_url,
    default_hooks,
)


class TestCreateHooks(testtools.TestCase):

    def test_attach_exc_info_missing(self):
        report = {}
        attach_exc_info(report, {})
        self.assertEqual({}, report)

    def test_attach_exc_info_actual_exception(self):
        report = {}
        try:
            raise ValueError("foo bar")
        except ValueError:
            attach_exc_info(report, {"exc_info": sys.exc_info()})
        self.assertEqual("ValueError", report["type"])
        self.assertEqual("foo bar", report["value"])
        self.assertIsInstance(report["tb_text"], str)

    def test_attach_date(self):
        report = {}
        attach_date(report, {})
        self.assertIsInstance(report["time"], datetime.datetime)

    def test_attach_exc_info_strings(self):
        report = {}
        exc_info = {"exc_info": ("ValueError", "foo bar", "my traceback")}
        attach_exc_info(report, exc_info)
        self.assertEqual("ValueError", report["type"])
        self.assertEqual("foo bar", report["value"])
        self.assertEqual("my traceback", report["tb_text"])

    def test_attach_exc_info_broken_exception(self):
        class UnprintableException(Exception):
            def __str__(self):
                raise RuntimeError("arrgh")

            __repr__ = __str__

        report = {}
        try:
            raise UnprintableException("foo bar")
        except UnprintableException:
            attach_exc_info(report, {"exc_info": sys.exc_info()})

        error_msg = "<unprintable UnprintableException object>"
        self.assertEqual(error_msg, report["value"])
        self.assertIsInstance(report["tb_text"], str)

    def test_defaults(self):
        self.assertEqual(
            [
                attach_exc_info,
                attach_date,
                copy_reporter,
                copy_topic,
                copy_url,
                attach_hostname,
            ],
            default_hooks,
        )

    def test_reporter(self):
        report = {}
        copy_reporter(report, {})
        self.assertEqual({}, report)
        copy_reporter(report, {"reporter": "foo"})
        self.assertEqual({"reporter": "foo"}, report)

    def test_topic(self):
        report = {}
        copy_topic(report, {})
        self.assertEqual({}, report)
        copy_topic(report, {"topic": "foo"})
        self.assertEqual({"topic": "foo"}, report)

    def test_url(self):
        report = {}
        copy_url(report, {})
        self.assertEqual({}, report)
        copy_url(report, {"url": "foo"})
        self.assertEqual({"url": "foo"}, report)

    def test_hostname(self):
        report = {}
        attach_hostname(report, {})
        expected_hostname = socket.gethostname()
        self.assertEqual({"hostname": expected_hostname}, report)
