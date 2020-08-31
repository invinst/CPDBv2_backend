import pytz
import datetime
from decimal import Decimal

from django.test.testcases import TestCase
from django.contrib.gis.geos import Point
from django.conf import settings

from robber.expect import expect
from mock import patch, Mock

from lawsuit.models import Lawsuit, LawsuitPlaintiff, Payment
from data.models import AttachmentFile
from lawsuit.importers import LawsuitImporter
from data.factories import AttachmentFileFactory
from lawsuit.factories import LawsuitFactory, LawsuitPlaintiffFactory, PaymentFactory


class LawsuitImporterTestCase(TestCase):
    @patch('lawsuit.importers.lawsuit_importer.Airtable')
    def test_update_data(self, airtable_cls_mock):
        updated_airtable_lawsuit_data_1 = {
            'id': 'rec05P3viy3ILqTT2',
            'fields': {
                'id': 750,
                'case_no': '11-CV-4549',
                'incident_date': '2009-08-03',
                'lat': 41.6761627,
                'lon': -87.6251221,
                'address': '12000 S. Perry Ave.',
                'city': 'Chicago',
                'state': 'IL',
                'interaction': ['Stop and frisk'],
                'Officer Tags': ['On duty'],
                'Location Description': 'Isaac Thomas Jr. residence',
                'narrative': 'Simmons was visiting his neighbor and one of her sons when Officers Couch and ',
                'complaint_url': 'https://s3.amazonaws.com/internal.chicagoreporter.com/complaints/11-CV-4549.pdf',
                'misconduct type': ['Threats/intimidation', 'Excessive force', 'False arrest or report'],
                'weapons': ['Physical force'],
                'Incident Outcome': ['Resisting or obstructing arrest charges'],
                'Payments': ['recPEuAfrUZd3GCcD', 'rec00AHp30i0xV0Tz'],
                'Plaintiffs': ['recZyu7ztEVPMqvI2'],
                'Added Date': '2020-07-06T07:45:18.000Z',
                'Last Modified Time': '2020-07-22T21:20:29.000Z'
            },
            'createdTime': '2020-07-06T07:45:18.000Z'
        }
        updated_airtable_lawsuit_data_2 = {
            'id': 'rec0yl7j1eZ54r9FM',
            'fields': {
                'id': 751,
                'case_no': '13-CV-2020',
                'incident_date': '2012-03-31',
                'lat': 41.756176,
                'lon': -87.5572968,
                'address': '7600 S. Exchange Ave.',
                'city': 'Chicago',
                'state': 'IL',
                'interaction': ['Stop and frisk'],
                'Officer Tags': ['Plainclothes'],
                'Location Description': 'Mobil Exxon Gas Station',
                'narrative': 'Dorsey was at a gas station when Officers Brown and Stacker',
                'complaint_url': '',
                'misconduct type': ['Excessive force'],
                'weapons': [],
                'Incident Outcome': ['Hospitalized'],
                'Payments': [],
                'Plaintiffs': [],
                'Added Date': '2020-07-06T07:38:31.000Z',
                'Last Modified Time': '2020-07-21T21:27:24.000Z'
            },
            'createdTime': '2020-07-06T07:45:18.000Z'
        }
        duplicated_airtable_lawsuit_data = {
            'id': 'rec0zFlSvnxmPrCWL',
            'fields': {
                'id': 752,
                'case_no': '11-CV-4549',
                'Added Date': '2020-07-06T07:45:18.000Z',
                'Last Modified Time': '2020-07-22T21:20:29.000Z'
            },
            'createdTime': '2020-07-06T07:45:18.000Z'
        }
        invalid_airtable_lawsuit_data = {
            'id': 'rec0zFlSvnxmPrCWL',
            'fields': {
                'id': 758,
                'Added Date': '2020-07-06T07:45:18.000Z',
                'Last Modified Time': '2020-07-22T21:20:29.000Z'
            },
            'createdTime': '2020-07-06T07:45:18.000Z'
        }
        kept_airtable_lawsuit_data = {
            'id': 'rec0FFhCY1MsmZbCC',
            'fields': {
                'id': 750,
                'case_no': '14-CV-3849',
                'Last Modified Time': '2020-08-21T21:27:35.000Z'
            },
            'createdTime': '2020-08-06T07:45:42.000Z'
        }
        new_airtable_lawsuit_data = {
            'id': 'rec06Sa7ZhcwNJMN4',
            'fields': {
                'id': 760,
                'case_no': '15-CV-11878',
                'incident_date': '2015-05-06',
                'address': '8700 S. Racine Ave.',
                'city': 'Chicago',
                'state': 'IL',
                'narrative': 'Redmond was robbed and called the police to report the incident.',
                'lat': 41.7353516,
                'lon': -87.6534119,
                'neighborhood': 'Gresham',
                'complaint_url': 'https://s3.amazonaws.com/internal.chicagoreporter.com/complaints/15-CV-11878.pdf',
                'Officer Tags': ['On duty'],
                'misconduct type': ['False arrest or report'],
                'Incident Outcome': ['Other charges filed'],
                'Payments': ['recyFPPNQVNEVdnK2'],
                'Plaintiffs': ['recJNqXp86N3j9rok'],
                'Added Date': '2020-07-06T07:45:59.000Z',
                'Last Modified Time': '2020-07-21T21:27:24.000Z'
            },
            'createdTime': '2020-07-06T07:45:59.000Z'
        }
        airtable_lawsuits_data = [
            updated_airtable_lawsuit_data_1,
            updated_airtable_lawsuit_data_2,
            duplicated_airtable_lawsuit_data,
            invalid_airtable_lawsuit_data,
            kept_airtable_lawsuit_data,
            new_airtable_lawsuit_data
        ]

        updated_airtable_payment_data = {
            'id': 'recyFPPNQVNEVdnK2',
            'fields': {
                'payment': 1713.19,
                'payee': 'ALLSTATE A/S/O ORI, SAM',
                'fees_costs': 0,
                'date_paid': '2019-01-28',
                'case': ['rec0FFhCY1MsmZbCC'],
                'primary_cause_edited': 'MVA/CITY VEHICLE',
                'Last Modified Time': '2020-07-16T09:27:15.000Z'
            },
            'createdTime': '2020-07-16T09:27:15.000Z'
        }
        kept_airtable_payment_data = {
            'id': 'rec09ET56dA7U3LVw',
            'fields': {
                'case': ['rec05P3viy3ILqTT2'],
                'primary_cause_edited': 'ILLEGAL SEARCH/SEIZURE',
                'Last Modified Time': '2020-08-03T19:03:21.000Z'
            },
            'createdTime': '2020-07-06T08:17:54.000Z'
        }
        new_airtable_payment_data_1 = {
            'id': 'rec00AHp30i0xV0Tz',
            'fields': {
                'payment': 3000,
                'payee': 'MURPHY-HOPPER, SHEILA',
                'fees_costs': 0,
                'date_paid': '2019-07-25',
                'case': ['rec06Sa7ZhcwNJMN4'],
                'primary_cause_edited': 'FIRETRUCK COLLISION',
                'Last Modified Time': '2020-07-16T09:27:36.000Z'
            },
            'createdTime': '2020-07-16T09:27:36.000Z'
        }
        new_airtable_payment_data_2 = {
            'id': 'recPEuAfrUZd3GCcD',
            'fields': {
                'payment': 0,
                'payee': 'KNOX, ALI',
                'fees_costs': 21000,
                'date_paid': '2019-03-20',
                'case': ['rec06Sa7ZhcwNJMN4'],
                'primary_cause_edited': 'FIRETRUCK COLLISION',
                'Last Modified Time': '2020-07-16T09:29:56.000Z'
            },
            'createdTime': '2020-07-16T09:28:46.000Z'
        }
        invalid_airtable_payment_data = {
            'id': 'rec09dNgxjGk88RY8',
            'fields': {
                'payment': 682,
                'payee': 'FEDERATED MUTUAL INSURANCE COMPANY & OLTMAN LAW GROUP',
                'fees_costs': 0,
                'date_paid': '2019-11-21',
                'primary_cause_edited': 'MVA / CITY VEHICLE ',
                'Last Modified Time': '2020-07-16T09:27:59.000Z'
            },
            'createdTime': '2020-07-16T09:27:59.000Z'
        }

        airtable_payments_data = [
            updated_airtable_payment_data,
            new_airtable_payment_data_1,
            new_airtable_payment_data_2,
            kept_airtable_payment_data,
            invalid_airtable_payment_data
        ]

        airtable_plaintiffs_data = [
            {
                'id': 'rec00xDFq3qwq2KOE',
                'fields': {
                    'name': 'Eric Scheidler',
                    'case': ['rec05P3viy3ILqTT2'],
                    'Last Modified Time': '2020-08-04T19:40:13.000Z'
                },
                'createdTime': '2020-08-04T19:40:13.000Z'
            },
            {
                'id': 'rec034jkq0co8PJkR',
                'fields': {
                    'name': 'Mary Sims',
                    'case': ['rec06Sa7ZhcwNJMN4'],
                    'Last Modified Time': '2020-07-16T08:37:08.000Z'
                },
                'createdTime': '2020-07-06T08:23:08.000Z'
            },
            {
                'id': 'rec04KPXLakSKPHkA',
                'fields': {
                    'name': 'Orlando Edwards',
                    'case': ['rec06Sa7ZhcwNJMN4'],
                    'Last Modified Time': '2020-07-16T08:37:08.000Z'
                },
                'createdTime': '2020-07-06T08:21:26.000Z'
            },
            {
                'id': 'rec0alTlGQjrzjq7B',
                'fields': {
                    'name': 'Wilfredo Rodriguez',
                    'case': ['rec0FFhCY1MsmZbCC'],
                    'Last Modified Time': '2020-08-04T19:40:13.000Z'
                },
                'createdTime': '2020-08-04T19:40:13.000Z'
            },
            {
                'id': 'rec0ywQxzoOB3eMGr',
                'fields': {
                    'name': 'Steven Wilson',
                    'Last Modified Time': '2020-08-04T19:40:13.000Z'
                },
                'createdTime': '2020-08-04T19:40:13.000Z'
            }
        ]

        airtable_tables = {
            'Case': airtable_lawsuits_data,
            'Victims': airtable_plaintiffs_data,
            'Payments': airtable_payments_data,
        }

        def side_effect(airtable_probject_key, airtable_table_name):
            data = []
            if airtable_probject_key == settings.AIRTABLE_LAWSUITS_PROJECT_KEY:
                data = airtable_tables[airtable_table_name]
            return Mock(get_all=Mock(return_value=data))

        airtable_cls_mock.side_effect = side_effect

        updated_lawsuit_1 = LawsuitFactory(
            airtable_id='rec05P3viy3ILqTT2',
            airtable_updated_at='2020-07-21T21:27:24.000Z',
            case_no='11-CV-4549',
            primary_cause='FIRETRUCK COLLISION old',
            summary='Old summary',
            point=None,
            incident_date=datetime.datetime(2009, 7, 2, tzinfo=pytz.utc),
            location='Old location',
            add1='Old add1',
            add2='Old add2',
            city='Old city',
            outcomes=['old outcome'],
            misconducts=['old misconduct'],
            violences=['old violence'],
            interactions=['old interaction'],
            services=['old service'],
        )

        updated_lawsuit_2 = LawsuitFactory(
            airtable_id='rec0yl7j1eZ54r9FM',
            airtable_updated_at='2020-07-21T20:26:24.000Z',
            case_no='13-CV-2020',
            primary_cause='Primary cause old',
            summary='Old summary',
            point=None,
            incident_date=None,
            location='Old location',
            add1='Old add1',
            add2='Old add2',
            city='Old city',
            outcomes=['old outcome'],
            misconducts=['old misconduct'],
            violences=['old violence'],
            interactions=['old interaction'],
            services=['old service'],
        )

        kept_lawsuit = LawsuitFactory(
            airtable_id='rec0FFhCY1MsmZbCC',
            airtable_updated_at='2020-08-21T21:27:35.000Z',
            case_no='14-CV-3849',
            primary_cause='PROPERTY DAMAGE / CABLE',
            summary='Dorsey was at a gas station when Officers Brown and Stacker, who were in plaincothes,',
            point=Point(-87.5572968, 41.756176),
            incident_date=datetime.datetime(2012, 3, 21, tzinfo=pytz.utc),
            location='Mobil Exxon Gas Station',
            add1='7600',
            add2='S. Exchange Ave.',
            city='Chicago IL',
            interactions=['Protest'],
            outcomes=['Killed by officer'],
            services=['On Duty', 'Plainclothes'],
            violences=['Physical Force'],
            misconducts=['Excessive force', 'Racial epithets'],
        )

        deleted_lawsuit = LawsuitFactory(
            airtable_id='rec0R3EVYxpnHqr4b',
            airtable_updated_at='2020-08-21T21:27:35.000Z',
            case_no='15-CV-11359',
        )

        updated_attachment = AttachmentFileFactory(url='old_url.pdf', owner=updated_lawsuit_1)
        deleted_attachment = AttachmentFileFactory(owner=updated_lawsuit_2)

        LawsuitPlaintiffFactory(lawsuit=updated_lawsuit_1, name='Old plaintiff', airtable_id='rec00xDFq3qwq2KOE')
        LawsuitPlaintiffFactory(lawsuit=updated_lawsuit_1, name='Deleted plaintiff', airtable_id='rec0v3gZJ1SLE411A')
        LawsuitPlaintiffFactory(lawsuit=deleted_lawsuit, name='Austin Walker', airtable_id='rec0wjSEP3ZilZDUR')

        updated_payment = PaymentFactory(
            payee='Old payee',
            settlement=1,
            legal_fees=1,
            lawsuit=kept_lawsuit,
            paid_date=None,
            airtable_id='recyFPPNQVNEVdnK2',
            airtable_updated_at='2020-07-16T09:15:15.000Z'
        )
        kept_payment = PaymentFactory(
            payee='MOSES, TATIANNA',
            settlement=15000,
            legal_fees=0,
            lawsuit=updated_lawsuit_1,
            paid_date=datetime.datetime(2015, 10, 15, tzinfo=pytz.utc),
            airtable_id='rec09ET56dA7U3LVw',
            airtable_updated_at='2020-08-03T19:03:21.000Z'
        )
        deleted_payment = PaymentFactory(
            lawsuit=updated_lawsuit_1,
            airtable_id='rec0Ddb530ElSuWDa',
            airtable_updated_at='2020-08-21T21:27:35.000Z',
        )

        expect(Lawsuit.objects.count()).to.eq(4)
        expect(AttachmentFile.objects.count()).to.eq(2)
        expect(LawsuitPlaintiff.objects.count()).to.eq(3)
        expect(Payment.objects.count()).to.eq(3)

        LawsuitImporter().update_data()

        expected_updated_lawsuit_data_1 = {
            'airtable_id': 'rec05P3viy3ILqTT2',
            'airtable_updated_at': '2020-07-22T21:20:29.000Z',
            'case_no': '11-CV-4549',
            'primary_cause': 'ILLEGAL SEARCH/SEIZURE',
            'summary': 'Simmons was visiting his neighbor and one of her sons when Officers Couch and ',
            'point': Point(-87.6251221, 41.6761627),
            'incident_date': datetime.datetime(2009, 8, 3, tzinfo=pytz.utc),
            'location': 'Isaac Thomas Jr. residence',
            'add1': '12000',
            'add2': 'S. Perry Ave.',
            'city': 'Chicago IL',
            'outcomes': ['Resisting or obstructing arrest charges'],
            'misconducts': ['Threats/intimidation', 'Excessive force', 'False arrest or report'],
            'violences': ['Physical force'],
            'interactions': ['Stop and frisk'],
            'services': ['On duty'],
        }
        expected_updated_lawsuit_data_2 = {
            'airtable_id': 'rec0yl7j1eZ54r9FM',
            'airtable_updated_at': '2020-07-21T21:27:24.000Z',
            'case_no': '13-CV-2020',
            'primary_cause': None,
            'summary': 'Dorsey was at a gas station when Officers Brown and Stacker',
            'point': Point(-87.5572968, 41.756176),
            'incident_date': datetime.datetime(2012, 3, 31, tzinfo=pytz.utc),
            'location': 'Mobil Exxon Gas Station',
            'add1': '7600',
            'add2': 'S. Exchange Ave.',
            'city': 'Chicago IL',
            'outcomes': ['Hospitalized'],
            'misconducts': ['Excessive force'],
            'violences': [],
            'interactions': ['Stop and frisk'],
            'services': ['Plainclothes'],
        }
        expected_kept_lawsuit_data = {
            'airtable_id': 'rec0FFhCY1MsmZbCC',
            'airtable_updated_at': '2020-08-21T21:27:35.000Z',
            'case_no': '14-CV-3849',
            'primary_cause': 'MVA/CITY VEHICLE',
            'summary': 'Dorsey was at a gas station when Officers Brown and Stacker, who were in plaincothes,',
            'point': Point(-87.5572968, 41.756176),
            'incident_date': datetime.datetime(2012, 3, 21, tzinfo=pytz.utc),
            'location': 'Mobil Exxon Gas Station',
            'add1': '7600',
            'add2': 'S. Exchange Ave.',
            'city': 'Chicago IL',
            'outcomes': ['Killed by officer'],
            'misconducts': ['Excessive force', 'Racial epithets'],
            'violences': ['Physical Force'],
            'interactions': ['Protest'],
            'services': ['On Duty', 'Plainclothes'],
        }
        expected_created_lawsuit_data = {
            'airtable_id': 'rec06Sa7ZhcwNJMN4',
            'airtable_updated_at': '2020-07-21T21:27:24.000Z',
            'case_no': '15-CV-11878',
            'primary_cause': 'FIRETRUCK COLLISION',
            'summary': 'Redmond was robbed and called the police to report the incident.',
            'point': Point(-87.6534119, 41.7353516),
            'incident_date': datetime.datetime(2015, 5, 6, tzinfo=pytz.utc),
            'location': '',
            'add1': '8700',
            'add2': 'S. Racine Ave.',
            'city': 'Chicago IL',
            'outcomes': ['Other charges filed'],
            'misconducts': ['False arrest or report'],
            'violences': [],
            'interactions': [],
            'services': ['On duty'],
        }

        expect(Lawsuit.objects.count()).to.eq(4)
        expect(Lawsuit.objects.filter(airtable_id=kept_lawsuit.airtable_id).exists()).to.be.true()
        expect(Lawsuit.objects.filter(airtable_id=updated_lawsuit_1.airtable_id).exists()).to.be.true()
        expect(Lawsuit.objects.filter(airtable_id=updated_lawsuit_2.airtable_id).exists()).to.be.true()
        expect(Lawsuit.objects.filter(airtable_id=deleted_lawsuit.airtable_id).exists()).to.be.false()
        updated_lawsuit_1.refresh_from_db()
        updated_lawsuit_2.refresh_from_db()
        kept_lawsuit.refresh_from_db()
        created_lawsuit = Lawsuit.objects.filter(airtable_id='rec06Sa7ZhcwNJMN4').first()

        expected_lawsuits_data = {
            updated_lawsuit_1: expected_updated_lawsuit_data_1,
            updated_lawsuit_2: expected_updated_lawsuit_data_2,
            kept_lawsuit: expected_kept_lawsuit_data,
            created_lawsuit: expected_created_lawsuit_data
        }

        for lawsuit, expected_lawsuit_data in expected_lawsuits_data.items():
            for attr, value in expected_lawsuit_data.items():
                if attr == 'point':
                    point = getattr(lawsuit, attr)
                    expect(point.x).to.eq(value.x)
                    expect(point.y).to.eq(value.y)
                else:
                    expect(getattr(lawsuit, attr)).to.eq(value)

        expect(AttachmentFile.objects.count()).to.eq(2)
        expect(AttachmentFile.objects.filter(id=updated_attachment.id).exists()).to.be.true()
        expect(AttachmentFile.objects.filter(id=deleted_attachment.id).exists()).to.be.false()
        updated_attachment.refresh_from_db()
        created_attachment = AttachmentFile.objects.filter(
            url='https://s3.amazonaws.com/internal.chicagoreporter.com/complaints/15-CV-11878.pdf'
        ).first()
        expect(updated_attachment.owner).to.eq(updated_lawsuit_1)
        expect(updated_attachment.url).to.eq(
            'https://s3.amazonaws.com/internal.chicagoreporter.com/complaints/11-CV-4549.pdf'
        )
        expect(created_attachment.owner).to.eq(created_lawsuit)

        expected_lawsuit_plaintiffs_data = {
            updated_lawsuit_1: ['Eric Scheidler'],
            updated_lawsuit_2: [],
            kept_lawsuit: ['Wilfredo Rodriguez'],
            created_lawsuit: ['Mary Sims', 'Orlando Edwards']
        }
        expect(LawsuitPlaintiff.objects.count()).to.eq(4)
        for lawsuit, expected_plaintiff_names in expected_lawsuit_plaintiffs_data.items():
            plaintiff_names = list(lawsuit.plaintiffs.order_by('name').values_list('name', flat=True))
            expect(plaintiff_names).to.eq(expected_plaintiff_names)

        expected_updated_payment_data = {
            'payee': 'ALLSTATE A/S/O ORI, SAM',
            'settlement': Decimal('1713.19'),
            'legal_fees': 0,
            'lawsuit': kept_lawsuit,
            'paid_date': datetime.datetime(2019, 1, 28, tzinfo=pytz.utc),
            'airtable_id': 'recyFPPNQVNEVdnK2',
            'airtable_updated_at': '2020-07-16T09:27:15.000Z'
        }
        expected_kept_payment_data = {
            'payee': 'MOSES, TATIANNA',
            'settlement': Decimal('15000'),
            'legal_fees': 0,
            'lawsuit': updated_lawsuit_1,
            'paid_date': datetime.datetime(2015, 10, 15, tzinfo=pytz.utc),
            'airtable_id': 'rec09ET56dA7U3LVw',
            'airtable_updated_at': '2020-08-03T19:03:21.000Z'
        }
        expected_created_payment_data_1 = {
            'payee': 'MURPHY-HOPPER, SHEILA',
            'settlement': Decimal('3000'),
            'legal_fees': 0,
            'lawsuit': created_lawsuit,
            'paid_date': datetime.datetime(2019, 7, 25, tzinfo=pytz.utc),
            'airtable_id': 'rec00AHp30i0xV0Tz',
            'airtable_updated_at': '2020-07-16T09:27:36.000Z'
        }
        expected_created_payment_data_2 = {
            'payee': 'KNOX, ALI',
            'settlement': 0,
            'legal_fees': Decimal('21000'),
            'lawsuit': created_lawsuit,
            'paid_date': datetime.datetime(2019, 3, 20, tzinfo=pytz.utc),
            'airtable_id': 'recPEuAfrUZd3GCcD',
            'airtable_updated_at': '2020-07-16T09:29:56.000Z'
        }

        expect(Payment.objects.count()).to.eq(4)
        expect(Payment.objects.filter(airtable_id=updated_payment.airtable_id).exists()).to.be.true()
        expect(Payment.objects.filter(airtable_id=kept_payment.airtable_id).exists()).to.be.true()
        expect(Payment.objects.filter(airtable_id=deleted_payment.airtable_id).exists()).to.be.false()
        updated_payment.refresh_from_db()
        kept_payment.refresh_from_db()
        created_payment_1 = Payment.objects.filter(airtable_id='rec00AHp30i0xV0Tz').first()
        created_payment_2 = Payment.objects.filter(airtable_id='recPEuAfrUZd3GCcD').first()

        expected_payments_data = {
            updated_payment: expected_updated_payment_data,
            kept_payment: expected_kept_payment_data,
            created_payment_1: expected_created_payment_data_1,
            created_payment_2: expected_created_payment_data_2,
        }

        for payment, expected_payment_data in expected_payments_data.items():
            for attr, value in expected_payment_data.items():
                expect(getattr(payment, attr)).to.eq(value)

    def test_update_data_with_force_update(self):
        pass
