from robber import expect

from django.test import SimpleTestCase

from data_importer.base.merger import SimpleRule, SetRule, Merger


class SimpleRuleTestCase(SimpleTestCase):
    def test_apply(self):
        expect(SimpleRule.apply(None, 1)).to.be.eq((True, 1))
        expect(SimpleRule.apply(1, None)).to.be.eq((True, 1))
        expect(SimpleRule.apply(None, None)).to.be.eq((True, None))
        expect(SimpleRule.apply(1, 1)).to.be.eq((True, 1))
        expect(SimpleRule.apply(1, 2)).to.be.eq((False, None))

    def test_resolve(self):
        expect(SimpleRule.resolve(None, None, None)).to.be.eq(None)
        expect(SimpleRule.resolve(None, 1, 1)).to.be.eq(None)
        expect(SimpleRule.resolve(None, 1, 2)).to.be.eq(2)


class SetRuleTestCase(SimpleTestCase):
    def test_apply(self):
        expect(SetRule.apply([1, 2], 2)).to.be.eq((True, [1, 2]))

    def test_resolve(self):
        expect(SetRule.resolve([1], [2], [1, 2])).to.be.eq([1])
        expect(SetRule.resolve([1], [1], [1])).to.be.eq(None)


class MergerTestCase(SimpleTestCase):
    def setUp(self):
        self.schema = {
            'first_name': SimpleRule,
            'last_name': SimpleRule
        }

    def test_check_mergeable(self):
        merger = Merger(self.schema)
        profile = {'first_name': 'Foo', 'last_name': 'Bar'}
        candidate = {'first_name': None, 'last_name': 'Baz'}
        expect(merger.check_mergeable(profile, candidate)).to.be.eq((
            {'first_name': 'Foo'},
            [('last_name', 'Bar', 'Baz')],
        ))

    def test_is_mergeable_true(self):
        merger = Merger(self.schema)
        profile = {'first_name': 'Foo', 'last_name': 'Bar'}
        candidate = {'first_name': None, 'last_name': 'Bar'}
        expect(merger.is_mergeable(profile, candidate)).to.be.true()

    def test_is_mergeable_false(self):
        merger = Merger(self.schema)
        profile = {'first_name': 'Foo', 'last_name': 'Bar'}
        candidate = {'first_name': None, 'last_name': 'Baz'}
        expect(merger.is_mergeable(profile, candidate)).to.be.false()
