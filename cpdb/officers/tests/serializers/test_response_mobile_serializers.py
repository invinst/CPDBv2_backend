from datetime import date, datetime

from django.test import TestCase
from django.contrib.gis.geos import Point

import pytz
from robber import expect

from officers.serializers.response_mobile_serializers import (
    OfficerInfoMobileSerializer,
    PoliceUnitMobileSerializer,
    BaseTimelineMobileSerializer,
    RankChangeNewTimelineMobileSerializer,
    JoinedNewTimelineMobileSerializer,
    UnitChangeNewTimelineMobileSerializer,
    CRNewTimelineMobileSerializer,
    AwardNewTimelineMobileSerializer,
    TRRNewTimelineMobileSerializer,
    CoaccusalCardMobileSerializer,
    OfficerCardMobileSerializer
)
from data.factories import (
    OfficerFactory, PoliceUnitFactory, OfficerBadgeNumberFactory,
    OfficerHistoryFactory, OfficerYearlyPercentileFactory, SalaryFactory,
    AllegationFactory, OfficerAllegationFactory, AllegationCategoryFactory,
    AttachmentFileFactory, VictimFactory, AwardFactory
)
from trr.factories import TRRFactory


class PoliceUnitMobileSerializerTestCase(TestCase):
    def test_serialization(self):
        unit_with_name = PoliceUnitFactory(
            id=123,
            unit_name='004',
            description='District 004',
        )

        expect(PoliceUnitMobileSerializer(unit_with_name).data).to.eq({
            'unit_id': 123,
            'unit_name': '004',
            'description': 'District 004',
        })


class OfficerInfoMobileSerializerTestCase(TestCase):
    def test_serialization(self):
        unit = PoliceUnitFactory(
            id=4,
            unit_name='004',
            description='District 004',
        )
        old_unit = PoliceUnitFactory(
            id=5,
            unit_name='005',
            description='District 005',
        )

        officer = OfficerFactory(
            id=123,
            first_name='Michael',
            last_name='Flynn',
            last_unit=unit,
            appointed_date=date(2000, 1, 2),
            resignation_date=date(2010, 2, 3),
            active='Yes',
            rank='Sergeant',
            race='Black',
            gender='F',
            current_badge='456',
            birth_year=1950,
            allegation_count=20,
            complaint_percentile='99.9900',
            honorable_mention_count=3,
            sustained_count=4,
            discipline_count=6,
            civilian_compliment_count=2,
            trr_count=7,
            major_award_count=8,
            honorable_mention_percentile='88.8800',
        )

        OfficerBadgeNumberFactory(
            officer=officer,
            current=False,
            star='789'
        )
        OfficerBadgeNumberFactory(
            officer=officer,
            current=True,
            star='456'
        )

        OfficerHistoryFactory(officer=officer, unit=old_unit, effective_date=date(2002, 1, 2))
        OfficerHistoryFactory(officer=officer, unit=unit, effective_date=date(2004, 1, 2))

        OfficerYearlyPercentileFactory(
            officer=officer,
            year=2002,
            percentile_trr='99.88',
            percentile_allegation=None,
            percentile_allegation_civilian='77.66',
            percentile_allegation_internal='66.55'
        )
        OfficerYearlyPercentileFactory(
            officer=officer,
            year=2003,
            percentile_trr='99.99',
            percentile_allegation='88.88',
            percentile_allegation_civilian='77.77',
            percentile_allegation_internal='66.66'
        )

        expect(OfficerInfoMobileSerializer(officer).data).to.eq({
            'officer_id': 123,
            'unit': {
                'unit_id': 4,
                'unit_name': '004',
                'description': 'District 004',
            },
            'date_of_appt': '2000-01-02',
            'date_of_resignation': '2010-02-03',
            'active': 'Active',
            'rank': 'Sergeant',
            'full_name': 'Michael Flynn',
            'race': 'Black',
            'badge': '456',
            'historic_badges': ['789'],
            'gender': 'Female',
            'birth_year': 1950,
            'allegation_count': 20,
            'complaint_percentile': 99.99,
            'honorable_mention_count': 3,
            'sustained_count': 4,
            'discipline_count': 6,
            'civilian_compliment_count': 2,
            'trr_count': 7,
            'major_award_count': 8,
            'honorable_mention_percentile': 88.88,
            'percentiles': [
                {
                    'id': 123,
                    'year': 2002,
                    'percentile_trr': '99.8800',
                    'percentile_allegation_civilian': '77.6600',
                    'percentile_allegation_internal': '66.5500',
                },
                {
                    'id': 123,
                    'year': 2003,
                    'percentile_trr': '99.9900',
                    'percentile_allegation': '88.8800',
                    'percentile_allegation_civilian': '77.7700',
                    'percentile_allegation_internal': '66.6600',
                },
            ]
        })


class BaseTimelineMobileSerializerMobileSerializerTestCase(TestCase):
    def test_raise_NotImplementedError(self):
        expect(lambda: BaseTimelineMobileSerializer().get_kind(None)).to.throw(NotImplementedError)
        expect(lambda: BaseTimelineMobileSerializer().get_priority_sort(None)).to.throw(NotImplementedError)


class RankChangeNewTimelineMobileSerializerTestCase(TestCase):
    def test_serialization(self):
        officer = OfficerFactory(id=123)
        salary = SalaryFactory(
            officer=officer,
            spp_date=date(2002, 2, 3),
            rank='Police Officer',
        )
        setattr(salary, 'unit_name', 'Unit 001')
        setattr(salary, 'unit_description', 'District 001')

        expect(RankChangeNewTimelineMobileSerializer(salary).data).to.eq({
            'unit_name': 'Unit 001',
            'unit_description': 'District 001',
            'rank': 'Police Officer',
            'priority_sort': 25,
            'kind': 'RANK_CHANGE',
            'date_sort': date(2002, 2, 3),
            'date': '2002-02-03'
        })


class JoinedNewTimelineMobileSerializerTestCase(TestCase):
    def test_serialization(self):
        officer = OfficerFactory(id=123, appointed_date=date(2002, 2, 3))
        setattr(officer, 'unit_name', 'Unit 001')
        setattr(officer, 'unit_description', 'District 001')
        setattr(officer, 'rank_name', 'Police Officer')

        expect(JoinedNewTimelineMobileSerializer(officer).data).to.eq({
            'unit_name': 'Unit 001',
            'unit_description': 'District 001',
            'rank': 'Police Officer',
            'priority_sort': 10,
            'kind': 'JOINED',
            'date_sort': date(2002, 2, 3),
            'date': '2002-02-03'
        })


class UnitChangeNewTimelineMobileSerializerTestCase(TestCase):
    def test_serialization(self):
        officer = OfficerFactory(id=123)
        unit = PoliceUnitFactory(
            id=4,
            unit_name='004',
            description='District 004',
        )
        officer_history = OfficerHistoryFactory(
            officer=officer,
            unit=unit,
            effective_date=date(2002, 2, 3)
        )
        setattr(officer_history, 'rank_name', 'Police Officer')

        expect(UnitChangeNewTimelineMobileSerializer(officer_history).data).to.eq({
            'unit_name': '004',
            'unit_description': 'District 004',
            'rank': 'Police Officer',
            'priority_sort': 20,
            'kind': 'UNIT_CHANGE',
            'date_sort': date(2002, 2, 3),
            'date': '2002-02-03'
        })


class CRNewTimelineMobileSerializerTestCase(TestCase):
    def test_serialization(self):
        officer = OfficerFactory(id=123)
        allegation = AllegationFactory(
            crid='CR123',
            incident_date=datetime(2002, 2, 3, tzinfo=pytz.utc),
            coaccused_count=3,
            point=Point([0.01, 0.02])
        )
        allegation_category = AllegationCategoryFactory(
            category='some category',
            allegation_name='some sub category'
        )
        officer_allegation = OfficerAllegationFactory(
            officer=officer,
            allegation=allegation,
            allegation_category=allegation_category,
            final_finding='SU',
            final_outcome='9 Day Suspension'
        )

        AttachmentFileFactory(
            tag='Other',
            allegation=allegation,
            title='title',
            url='url',
            preview_image_url='preview_image_url',
            file_type='document'
        )
        AttachmentFileFactory(
            tag='AR',
            allegation=allegation,
            title='title 2',
            url='url_2',
            preview_image_url='preview_image_url_2',
            file_type='document'
        )
        VictimFactory(allegation=allegation, gender='M', race='Black', age=30)

        setattr(officer_allegation, 'unit_name', 'Unit 001')
        setattr(officer_allegation, 'unit_description', 'District 001')
        setattr(officer_allegation, 'rank_name', 'Police Officer')

        expect(CRNewTimelineMobileSerializer(officer_allegation).data).to.eq({
            'unit_name': 'Unit 001',
            'unit_description': 'District 001',
            'rank': 'Police Officer',
            'priority_sort': 30,
            'kind': 'CR',
            'date_sort': date(2002, 2, 3),
            'date': '2002-02-03',
            'crid': 'CR123',
            'category': 'some category',
            'subcategory': 'some sub category',
            'finding': 'Sustained',
            'outcome': '9 Day Suspension',
            'coaccused': 3,
            'attachments': [
                {
                    'title': 'title',
                    'url': 'url',
                    'preview_image_url': 'preview_image_url',
                    'file_type': 'document',
                }
            ],
            'point': {
                'lon': 0.01,
                'lat': 0.02
            },
            'victims': [
                {
                    'gender': 'Male',
                    'race': 'Black',
                    'age': 30
                }
            ]

        })

    def test_get_point(self):
        allegation = AllegationFactory(crid='CR123', coaccused_count=3, point=None)
        officer_allegation = OfficerAllegationFactory(allegation=allegation)

        setattr(officer_allegation, 'unit_name', 'Unit 001')
        setattr(officer_allegation, 'unit_description', 'District 001')
        setattr(officer_allegation, 'rank_name', 'Police Officer')

        expect(CRNewTimelineMobileSerializer(officer_allegation).data).to.exclude('point')


class AwardNewTimelineMobileSerializerTestCase(TestCase):
    def test_serialization(self):
        officer = OfficerFactory(id=123)
        award = AwardFactory(officer=officer, start_date=date(2002, 2, 3), award_type='Life Saving Award')

        setattr(award, 'unit_name', 'Unit 001')
        setattr(award, 'unit_description', 'District 001')
        setattr(award, 'rank_name', 'Police Officer')

        expect(AwardNewTimelineMobileSerializer(award).data).to.eq({
            'unit_name': 'Unit 001',
            'unit_description': 'District 001',
            'rank': 'Police Officer',
            'priority_sort': 40,
            'kind': 'AWARD',
            'date_sort': date(2002, 2, 3),
            'date': '2002-02-03',
            'award_type': 'Life Saving Award'
        })


class TRRNewTimelineMobileSerializerTestCase(TestCase):
    def test_serialization(self):
        officer = OfficerFactory(id=123)
        trr = TRRFactory(
            id=456,
            officer=officer,
            trr_datetime=datetime(2002, 2, 3, tzinfo=pytz.utc),
            point=Point([0.01, 0.02]),
            taser=True,
            firearm_used=False
        )

        setattr(trr, 'unit_name', 'Unit 001')
        setattr(trr, 'unit_description', 'District 001')
        setattr(trr, 'rank_name', 'Police Officer')

        expect(TRRNewTimelineMobileSerializer(trr).data).to.eq({
            'unit_name': 'Unit 001',
            'unit_description': 'District 001',
            'rank': 'Police Officer',
            'priority_sort': 50,
            'kind': 'FORCE',
            'trr_id': 456,
            'date_sort': date(2002, 2, 3),
            'date': '2002-02-03',
            'taser': True,
            'firearm_used': False,
            'point': {
                'lon': 0.01,
                'lat': 0.02
            }
        })

    def test_get_point(self):
        trr = TRRFactory(id=456, point=None)

        setattr(trr, 'unit_name', 'Unit 001')
        setattr(trr, 'unit_description', 'District 001')
        setattr(trr, 'rank_name', 'Police Officer')

        expect(TRRNewTimelineMobileSerializer(trr).data).to.exclude('point')


class CoaccusalCardMobileSerializerTestCase(TestCase):
    def test_serialization(self):
        officer = OfficerFactory(
            id=123456,
            first_name='Jerome',
            last_name='Finnigan',
            rank='Police Officer',
            race='Black',
            gender='F',
            birth_year=1950,
            allegation_count=20,
            sustained_count=4,
            complaint_percentile='99.9900',
            civilian_allegation_percentile='88.8800',
            internal_allegation_percentile='77.7700',
            trr_percentile='66.6600',
        )

        setattr(officer, 'coaccusal_count', 7)

        expect(CoaccusalCardMobileSerializer(officer).data).to.eq({
            'id': 123456,
            'full_name': 'Jerome Finnigan',
            'coaccusal_count': 7,
            'rank': 'Police Officer',
            'percentile': {
                'percentile_allegation_civilian': '88.8800',
                'percentile_allegation_internal': '77.7700',
                'percentile_trr': '66.6600',
            },
        })


class OfficerCardMobileSerializerTestCase(TestCase):
    def test_serialization(self):
        officer = OfficerFactory(
            id=123,
            first_name='Jame',
            last_name='Bone',
            allegation_count=2,
            sustained_count=1,
            birth_year=1950,
            race='White',
            gender='M',
            resignation_date=date(2000, 1, 1),
            complaint_percentile='99.9900',
            civilian_allegation_percentile='88.8800',
            internal_allegation_percentile='77.7700',
            trr_percentile='66.6600',
        )

        expect(OfficerCardMobileSerializer(officer).data).to.eq({
            'id': 123,
            'full_name': 'Jame Bone',
            'complaint_count': 2,
            'percentile': {
                'percentile_allegation_civilian': '88.8800',
                'percentile_allegation_internal': '77.7700',
                'percentile_trr': '66.6600',
            }
        })
