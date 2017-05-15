
from django.db.models import Case, Value, When, CharField
from django.test.testcases import SimpleTestCase

from robber import expect

from data.utils.aggregation import get_num_range_case


class AggregationUtilsTestCase(SimpleTestCase):
    def test_get_num_range_case(self):
        result = get_num_range_case('a', [1, 5])
        expect([
            (
                "<Case: CASE WHEN <Q: (AND: ('a__gte', 1), ('a__lte', 5))> THEN Value(1-5), "
                "WHEN <Q: (AND: ('a__gte', 6))> THEN Value(6+), ELSE Value(Unknown)>"),
            (
                "<Case: CASE WHEN <Q: (AND: ('a__lte', 5), ('a__gte', 1))> THEN Value(1-5), "
                "WHEN <Q: (AND: ('a__gte', 6))> THEN Value(6+), ELSE Value(Unknown)>")
        ]).to.contain(repr(result))

    def test_get_num_range_case_single_value(self):
        num_range = [1]
        expect_result = Case(
            When(a__gte=1, then=Value('1+')),
            default=Value('Unknown'),
            output_field=CharField()
            )
        actual_result = get_num_range_case('a', num_range)

        expect(repr(expect_result)).to.eq(repr(actual_result))

    def test_get_num_range_case_empty_array(self):
        num_range = []
        expect_result = Case(
            default=Value('Unknown'),
            output_field=CharField()
            )
        actual_result = get_num_range_case('a', num_range)

        expect(repr(expect_result)).to.eq(repr(actual_result))

    def test_get_num_range_case_begin_with_zero(self):
        result = get_num_range_case('a', [0, 3, 5])
        expect([
            (
                "<Case: CASE WHEN <Q: (AND: ('a__lte', 3))> THEN Value(<3), "
                "WHEN <Q: (AND: ('a__gte', 4), ('a__lte', 5))> "
                "THEN Value(4-5), WHEN <Q: (AND: ('a__gte', 6))> THEN Value(6+), ELSE Value(Unknown)>"),
            (
                "<Case: CASE WHEN <Q: (AND: ('a__lte', 3))> THEN Value(<3), "
                "WHEN <Q: (AND: ('a__lte', 5), ('a__gte', 4))> "
                "THEN Value(4-5), WHEN <Q: (AND: ('a__gte', 6))> THEN Value(6+), ELSE Value(Unknown)>")
        ]).to.contain(repr(result))
