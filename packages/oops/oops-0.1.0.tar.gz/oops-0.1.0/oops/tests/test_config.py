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


from functools import partial

import testtools
from testtools.matchers import Is

from oops.config import Config
from oops.createhooks import default_hooks


class TestConfig(testtools.TestCase):

    def test_init(self):
        config = Config()
        self.assertEqual(default_hooks, config.on_create)
        self.assertEqual([], config.publishers)
        self.assertEqual({}, config.template)

    def test_on_create_called(self):
        calls = []

        def capture(id, report, context):
            calls.append((id, report, context))

        config = Config()
        config.on_create = []
        config.on_create.append(partial(capture, "1"))
        config.on_create.append(partial(capture, "2"))
        report = config.create(dict(foo="2"))
        self.assertThat(report, Is(calls[0][1]))
        self.assertThat(report, Is(calls[1][1]))

        test_calls = [("1", {}, {"foo": "2"}), ("2", {}, {"foo": "2"})]
        self.assertEqual(test_calls, calls)

    def test_on_create_no_context(self):
        calls = []

        def capture(report, context):
            calls.append((report, context))

        config = Config()
        config.on_create = []
        config.on_create.append(capture)
        report = config.create()  # noqa: F841
        self.assertEqual([({}, {})], calls)

    def test_create_template(self):
        config = Config()
        config.on_create = []
        config.template["base"] = True
        config.template["list"] = []
        report = config.create()
        self.assertEqual({"base": True, "list": []}, report)
        self.assertIsNot(report["list"], config.template["list"])

    def test_publish_calls_publishers(self):
        calls = []  # noqa: F841

        def pub_1(report):
            return "1"

        def pub_2(report):
            return "2"

        config = Config()
        config.publishers.append(pub_1)
        config.publishers.append(pub_2)
        report = {}
        self.assertEqual(["1", "2"], config.publish(report))

    def test_publish_filters_first(self):
        calls = []

        def filter_ok(report):
            calls.append("ok")

        def filter_block(report):
            calls.append("block")
            return True

        def pub(report):
            calls.append("pub")
            return "1"

        config = Config()
        config.filters.append(filter_ok)
        config.filters.append(filter_block)
        config.filters.append(filter_ok)
        config.publishers.append(pub)
        report = {}
        self.assertEqual(None, config.publish(report))
        self.assertEqual(["ok", "block"], calls)

    def test_publishers_returning_not_published_no_change_to_report(self):
        # If a publisher returns False (indicating it did not publish) no
        # change is made to the report - this permits chaining publishers as a
        # primary and fallback: The fallback can choose to do nothing if there
        # is an id already assigned (and returns None to signal what it did);
        # the caller Sees the actual assigned id in the report
        def pub_succeed(report):
            return "1"

        def pub_noop(report):
            return ""

        config = Config()
        config.publishers.append(pub_succeed)
        config.publishers.append(pub_noop)
        report = {}
        self.assertEqual(["1"], config.publish(report))

    def test_publish_to_publisher(self):
        calls = []
        config = Config()

        def succeed(report):
            calls.append(report.copy())
            return ["a"]

        config.publisher = succeed
        report = dict(foo="bar")
        config.publish(report)
        self.assertEqual([dict(foo="bar")], calls)

    def test_returns_return_value_of_publisher(self):
        ids = ["a", "b"]

        def succeed(report):
            return ids

        config = Config()
        config.publisher = succeed
        report = dict(foo="bar")
        self.assertEqual(ids, config.publish(report))

    def test_publisher_and_publishers_used_together(self):
        calls = []

        def nopublish(report):
            calls.append(report)
            return []

        config = Config()
        config.publisher = nopublish
        config.publishers.append(nopublish)
        config.publish({})
        self.assertEqual(2, len(calls))

    def test_puts_id_in_report(self):
        the_id = "b"

        def succeed(report):
            return ["a", the_id]

        config = Config()
        config.publisher = succeed
        report = dict(foo="bar")
        config.publish(report)
        self.assertEqual(the_id, report["id"])
