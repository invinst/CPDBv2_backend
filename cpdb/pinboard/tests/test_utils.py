from django.test import SimpleTestCase

from robber import expect

from pinboard.utils import (
    generate_hex_from_uuid,
    int_to_zero_padded_hex,
    zero_padded_hex_to_int
)


class PinboardUtilsTestCase(SimpleTestCase):
    def test_int_to_zero_padded_hex(self):
        expect(int_to_zero_padded_hex(4000000000, 8)).to.eq('ee6b2800')
        expect(int_to_zero_padded_hex(0, 1)).to.eq('0')
        expect(int_to_zero_padded_hex(15, 2)).to.eq('0f')
        expect(int_to_zero_padded_hex(35345, 7)).to.eq('0008a11')
        expect(lambda: int_to_zero_padded_hex(35345, 3)).to.throw(ValueError)

    def test_zero_padded_hex_to_int(self):
        expect(zero_padded_hex_to_int('0')).to.eq(0)
        expect(zero_padded_hex_to_int('ee6b2800')).to.eq(4000000000)
        expect(zero_padded_hex_to_int('Ee6B2800')).to.eq(4000000000)

    def test_generate_hex_from_uuid(self):
        length = 2
        hex_str = generate_hex_from_uuid(length)
        expect(hex_str).to.be.an.string()
        expect(hex_str).to.have.length(length)
        expect(hex_str).to.match(r'^[a-f0-9]+$')
        expect(lambda: generate_hex_from_uuid(3)).to.throw(ValueError)
