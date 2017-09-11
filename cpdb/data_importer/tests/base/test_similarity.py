from robber import expect

from django.test import SimpleTestCase

from data_importer.base.similarity import Equal, EitherNone, Intersected, Any, All, SimilarityComputer, Similar


class EqualTestCase(SimpleTestCase):
    def test_apply(self):
        expect(Equal.apply(0, 1)).to.be.false()
        expect(Equal.apply(1, 1)).to.be.true()


class EitherNoneTestCase(SimpleTestCase):
    def test_apply(self):
        expect(EitherNone.apply(1, None)).to.be.true()
        expect(EitherNone.apply(None, 1)).to.be.true()
        expect(EitherNone.apply(1, 2)).to.be.false()


class IntersectedTestCase(SimpleTestCase):
    def test_apply(self):
        expect(Intersected.apply(1, 1)).to.be.true()
        expect(Intersected.apply([1], [1])).to.be.true()
        expect(Intersected.apply(1, 2)).to.be.false()
        expect(Intersected.apply([1], [2])).to.be.false()


class AnyTestCase(SimpleTestCase):
    def test_apply(self):
        expect(Any(EitherNone, Equal).apply(1, None)).to.be.true()
        expect(Any(EitherNone, Equal).apply(1, 1)).to.be.true()
        expect(Any(EitherNone, Equal).apply(1, 2)).to.be.false()


class AllTestCase(SimpleTestCase):
    def test_apply(self):
        expect(All(EitherNone, Equal).apply(None, None)).to.be.true()
        expect(All(EitherNone, Equal).apply(None, 1)).to.be.false()
        expect(All(EitherNone, Equal).apply(1, 1)).to.be.false()


class SimilarTestCase(SimpleTestCase):
    def test_apply(self):
        expect(Similar(threshold=.8).apply('Foo', 'Foo')).to.be.true()
        expect(Similar(threshold=.8).apply('Bar', 'Baz')).to.be.false()


class SimilarityComputerTestCase(SimpleTestCase):
    def test_compute_similarity(self):
        weights = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        excludes = {'d'}
        profile = {'a': 'a', 'b': 'b', 'c': 'c'}
        candidate = {'a': 'a', 'b': None, 'c': 'd'}
        similarity_computer = SimilarityComputer(weights=weights, instructions=[], excludes=excludes)
        expect(similarity_computer.compute(profile, candidate)).to.be.eq(([('c', 'c', 'd')], 0.5))
