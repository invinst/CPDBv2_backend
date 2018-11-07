from django.test.testcases import TestCase

from robber import expect

from data.factories import InvestigatorFactory, InvestigatorAllegationFactory, OfficerFactory


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

    def test_badge(self):
        investigator_1 = InvestigatorFactory(first_name='Jerome', last_name='Finnigan')
        expect(investigator_1.badge).to.eq('')

        officer = OfficerFactory(first_name='John', last_name='Sena')
        investigator_2 = InvestigatorFactory(first_name='Jerome', last_name='Finnigan', officer=officer)
        expect(investigator_2.badge).to.eq('CPD')
