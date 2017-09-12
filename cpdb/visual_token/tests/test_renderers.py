import json

from django.test import TestCase

from robber import expect

from visual_token.renderers import OfficerSocialGraphVisualTokenRenderer
from cpdb.data.factories import OfficerFactory, AllegationFactory, OfficerAllegationFactory


class OfficerSocialGraphVisualTokenRendererTestCase(TestCase):
    def setUp(self):
        self.renderer = OfficerSocialGraphVisualTokenRenderer()
        self.officer1 = OfficerFactory(id=1, first_name='Steve', last_name='Jobs')
        self.officer2 = OfficerFactory(id=2, first_name='Bill', last_name='Gates')
        allegation = AllegationFactory()
        OfficerAllegationFactory(officer=self.officer1, allegation=allegation)
        OfficerAllegationFactory(officer=self.officer2, allegation=allegation)

    def test_blob_name(self):
        expect(self.renderer.blob_name(self.officer1)).to.eq('officer_1')

    def test_coaccusals_between_two_officers(self):
        coaccusals = self.renderer.coaccusals_between_two_officers(self.officer1, self.officer2)

        expect(coaccusals).to.eq(1)

    def test_serialize(self):
        result = json.loads(self.renderer.serialize(self.officer1))

        expect(result['focusedId']).to.eq(1)
        expect(result['nodes']).to.contain({
                'salary': 0,
                'crs': 1,
                'id': 1,
                'name': 'Steve Jobs',
                'trrs': 0
            })
        expect(result['nodes']).to.contain({
                'salary': 0,
                'crs': 1,
                'id': 2,
                'name': 'Bill Gates',
                'trrs': 0
            })
        expect(any([
            x in result['links'] for x in [{
                'source': 1,
                'target': 2,
                'crs': 1
            }, {
                'source': 2,
                'target': 1,
                'crs': 1
            }
            ]
        ])).to.be.true()
