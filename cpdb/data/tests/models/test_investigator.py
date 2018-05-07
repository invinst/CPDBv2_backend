from django.test.testcases import TestCase

from robber import expect

from data.factories import InvestigatorFactory, InvestigatorAllegationFactory


class InvestigatorTestCase(TestCase):
    def test_abbr_name(self):
        investigator = InvestigatorFactory(first_name='John', last_name='Doe')
        expect(investigator.abbr_name).to.eq('J. Doe')

    def test_full_name(self):
        investigator = InvestigatorFactory(first_name='John', last_name='Doe')
        expect(investigator.full_name).to.eq('John Doe')

    def test_num_cases(self):
        investigator = InvestigatorFactory()
        InvestigatorAllegationFactory(investigator=investigator)
        expect(investigator.num_cases).to.eq(1)
