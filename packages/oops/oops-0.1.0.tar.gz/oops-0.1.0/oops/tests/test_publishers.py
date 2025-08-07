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

"""Tests for the publishers module."""


from hashlib import md5
from pprint import pformat

# We need a StringIO-like object that accepts native strings, since that's
# what pprint.pformat produces.
if bytes is str:
    from io import BytesIO as native_StringIO
else:
    from io import StringIO as native_StringIO

import testtools

from oops import (
    convert_result_to_list,
    pprint_to_stream,
    publish_new_only,
    publish_to_many,
    publish_with_fallback,
)


class TestPublisherNewOnly(testtools.TestCase):

    def test_publish_new_only_id_in_report(self):
        def pub_fail(report):
            self.fail("publication called")

        publisher = publish_new_only(pub_fail)
        publisher({"id": "foo"})

    def test_publish_new_only_no_id_in_report(self):
        calls = []
        publisher = publish_new_only(calls.append)
        publisher({"foo": "bar"})
        self.assertEqual([{"foo": "bar"}], calls)


class TestPublishToMany(testtools.TestCase):

    def test_publishes_to_one(self):
        calls = []

        def capture(report):
            calls.append(report)
            return []

        publisher = publish_to_many(capture)
        publisher(dict(foo="bar"))
        self.assertEqual([dict(foo="bar")], calls)

    def test_publishes_to_two(self):
        calls1 = []
        calls2 = []

        def capture1(report):
            calls1.append(report)
            return []

        def capture2(report):
            calls2.append(report)
            return []

        publisher = publish_to_many(capture1, capture2)
        publisher(dict(foo="bar"))
        self.assertEqual([dict(foo="bar")], calls1)
        self.assertEqual([dict(foo="bar")], calls2)

    def test_returns_empty_list_with_no_publishers(self):
        publisher = publish_to_many()
        self.assertEqual([], publisher({}))

    def test_adds_ids_from_publishers(self):
        first_ids = ["a", "b"]

        def first_success(report):
            return first_ids

        second_ids = ["c", "d"]

        def second_success(report):
            return second_ids

        publisher = publish_to_many(first_success, second_success)
        self.assertEqual(first_ids + second_ids, publisher({}))

    def test_puts_id_in_report(self):
        the_id = "b"

        def first(report):
            return ["a", the_id]

        def second(report):
            self.assertEqual(the_id, report["id"])
            return []

        publisher = publish_to_many(first, second)
        publisher({})

    def test_puts_nothing_in_report_for_unpublished(self):
        def first(report):
            return []

        def second(report):
            if "id" in report:
                self.fail(
                    "id set to %s when previous publisher "
                    "didn't publish" % report["id"]
                )
            return []

        publisher = publish_to_many(first, second)
        publisher({})


class TestPublishWithFallback(testtools.TestCase):

    def test_publishes_to_one(self):
        calls = []

        def capture(report):
            calls.append(report)
            return []

        publisher = publish_with_fallback(capture)
        publisher(dict(foo="bar"))
        self.assertEqual([dict(foo="bar")], calls)

    def test_publishes_to_two(self):
        calls1 = []
        calls2 = []

        def capture1(report):
            calls1.append(report)
            return []

        def capture2(report):
            calls2.append(report)
            return []

        publisher = publish_with_fallback(capture1, capture2)
        publisher(dict(foo="bar"))
        self.assertEqual([dict(foo="bar")], calls1)
        self.assertEqual([dict(foo="bar")], calls2)

    def test_returns_ids_from_publisher(self):
        ids = ["a", "b"]

        def success(report):
            return ids

        publisher = publish_with_fallback(success)
        self.assertEqual(ids, publisher({}))

    def test_publishes_new(self):
        def failure(report):
            return []

        calls = []

        def capture(report):
            calls.append(report)
            return []

        publisher = publish_with_fallback(failure, capture)
        self.assertEqual([], publisher({}))
        self.assertEqual(1, len(calls))

    def test_publish_stops_when_a_publisher_succeeds(self):
        def success(report):
            return ["the id"]

        def fail(report):
            self.fail("Called fallback when primary succeeded.")

        publisher = publish_with_fallback(success, fail)
        self.assertEqual(["the id"], publisher({}))


class ConvertResultToListTests(testtools.TestCase):

    def test_converts_False_to_empty_list(self):
        # A false-ish value gets turned in to an empty list
        def falseish(report):
            return False

        self.assertEqual([], convert_result_to_list(falseish)({}))

    def test_converts_True_to_list(self):
        # A true-ish value gets turned in to an empty list
        def trueish(report):
            return "aaa"

        self.assertEqual(["aaa"], convert_result_to_list(trueish)({}))


class TestPPrintToStream(testtools.TestCase):

    def test_inherits_id_when_set(self):
        output = native_StringIO()
        publisher = pprint_to_stream(output)
        published = publisher({"foo": "bar", "id": "quux"})
        self.assertEqual(["quux"], published)

    def test_returns_pprint_hash(self):
        output = native_StringIO()
        publisher = pprint_to_stream(output)
        published = publisher({"foo": "bar"})
        pprint_value = pformat({"foo": "bar"})

        test_hash = [md5(pprint_value.encode("UTF-8")).hexdigest()]
        self.assertEqual(test_hash, published)

    def test_outputs_pprint(self):
        output = native_StringIO()
        publisher = pprint_to_stream(output)
        publisher({"foo": "bar"})
        self.assertEqual(
            "{'foo': 'bar', 'id': 'dd63dafcbd4d5b28badfcaf86fb6fcdb'}\n",
            output.getvalue(),
        )
