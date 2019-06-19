from collections import Counter
from time import sleep

from django.test import TestCase
from robber import expect

from pinboard.factories import PinboardFactory, ExamplePinboardFactory
from pinboard.models import ExamplePinboard
from pinboard.utils import is_all_unique


class ExamplePinboardTestCase(TestCase):
    def test_str(self):
        pinboard = PinboardFactory(
            title='Example pinboard 1',
            description='Example pinboard 1',
        )
        example_pinboard = ExamplePinboardFactory(pinboard=pinboard)

        expect(str(example_pinboard)).to.eq(str(pinboard))

    def test_random(self):
        example_pinboards = ExamplePinboardFactory.create_batch(50)

        randoms = []
        for i in range(5):
            randoms.append(ExamplePinboard.random(2))
            sleep(0.1)

        for i in range(5):
            expect(example_pinboards).to.contain(randoms[i][0], randoms[i][1])

        expect(is_all_unique(randoms)).to.be.true()

    def test_random_when_there_are_not_enough_example_pinboards(self):
        example_pinboards = ExamplePinboardFactory.create_batch(3)
        randoms = ExamplePinboard.random(4)

        expect(randoms).to.have.length(3)
        expect(Counter(randoms)).to.eq(Counter(example_pinboards))
