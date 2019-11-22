from unittest.mock import Mock, patch

from django.test import TestCase

from robber import expect

from pinboard.fields import HexField, HexFieldTooManyCollisionError
from .models import HexModel


class HexFieldTestCase(TestCase):
    def test_deconstruct(self):
        field = HexField(hex_length=10, auto_gen_add=False, collision_retry=5)
        expect(field.deconstruct()[-1]).to.eq({
            'hex_length': 10,
            'auto_gen_add': False,
            'collision_retry': 5
        })

    def test_from_db_value(self):
        field = HexField()
        expect(field.from_db_value(None, Mock(), Mock())).to.be.none()
        expect(field.from_db_value(3994100275, Mock(), Mock())).to.eq('ee112233')

    def test_to_python(self):
        field = HexField()
        expect(field.to_python(None)).to.be.none()
        expect(field.to_python('aaddff22')).to.eq('aaddff22')
        expect(field.to_python(306048837)).to.eq('123def45')

    def test_get_prep_value(self):
        field = HexField()
        expect(field.get_prep_value('4321fedc')).to.eq(1126301404)

    def test_pre_save(self):
        inst = HexModel()
        inst.save()
        expect(inst.id).to.have.length(8)
        current_id = inst.id
        inst.nonauto_hex = '11223344'
        inst.save()
        expect(HexModel.objects.get(id=current_id).nonauto_hex).to.eq('11223344')

    @patch('pinboard.fields.generate_hex_from_uuid', return_value='1234abcd')
    def test_regen_hex(self, mock_gen):
        inst = HexModel()
        inst.save()
        inst2 = HexModel()
        expect(lambda: inst2.save()).to.throw(HexFieldTooManyCollisionError)
        expect(mock_gen.call_count).to.eq(12)

    def test_auto_gen_add_false(self):
        inst = HexModel()
        inst.save()
        expect(inst.nonauto_hex).to.be.none()
        inst.nonauto_hex = '12abcd34'
        inst.save()
        expect(inst.nonauto_hex).to.eq('12abcd34')
