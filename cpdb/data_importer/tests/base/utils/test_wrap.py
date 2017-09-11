import numpy as np
from robber import expect

from django.test import SimpleTestCase

from data_importer.base.utils.wrap import wrap


class WrapTestCase(SimpleTestCase):
    def test_wrap(self):
        expect(wrap(None)).to.be.eq([])
        expect(wrap(np.nan)).to.be.eq([])
        expect(wrap(1)).to.be.eq([1])
        expect(wrap([1])).to.be.eq([1])
