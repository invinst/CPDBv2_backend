from collections import Counter
from time import sleep

from django.test import TestCase
from robber import expect

from pinboard.factories import PinboardFactory, ExamplePinboardFactory
from pinboard.models import ExamplePinboard


class ExamplePinboardTestCase(TestCase):
    def test_str(self):
        pinboard = PinboardFactory(
            title='Example pinboard 1',
            description='Example pinboard 1',
        )
        example_pinboard = ExamplePinboardFactory(pinboard=pinboard)

        expect(str(example_pinboard)).to.eq(str(pinboard))

    # def test_random(self):
    #   example_pinboards = ExamplePinboardFactory.create_batch(50)

    #    randoms = []
    #    for i in range(5):
    #        randoms.append(ExamplePinboard.random(2))
    #        sleep(0.1)

    #    for random in randoms:
    #        expect(example_pinboards).to.contain(random[0], random[1])

    #    expect(list(
    #        {tuple(example_pinboard.pinboard_id for example_pinboard in random) for random in randoms}
    #    )).to.have.length(5)

    def test_random_when_there_are_not_enough_example_pinboards(self):
        example_pinboards = ExamplePinboardFactory.create_batch(3)
        randoms = ExamplePinboard.random(4)

        expect(randoms).to.have.length(3)
        expect(Counter(randoms)).to.eq(Counter(example_pinboards))
