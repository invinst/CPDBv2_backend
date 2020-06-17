## Pinboard officers [/pinboards/{pk}/officers]

### Get selected officers

+ Parameters
    + pk (string) - ID of Pinboard

+ Response 200 (application/json)

        [
            {
                'id': 123,
                'complaint_count': 20,
                'unit': {
                    'id': 4,
                    'unit_name': '004',
                    'description': 'District 004',
                    'long_unit_name': 'Unit 004',
                },
                'date_of_appt': '2000-01-02',
                'date_of_resignation': '2010-02-03',
                'active': 'Active',
                'rank': 'Sergeant',
                'full_name': 'Michael Flynn',
                'has_unique_name': True,
                'race': 'Black',
                'badge': '456',
                'historic_badges': ['789'],
                'historic_units': [
                    {
                        'id': 4,
                        'unit_name': '004',
                        'description': 'District 004',
                        'long_unit_name': 'Unit 004',
                    },
                    {
                        'id': 5,
                        'unit_name': '005',
                        'description': 'District 005',
                        'long_unit_name': 'Unit 005',
                    }
                ],
                'gender': 'Female',
                'birth_year': 1950,
                'current_salary': 10000,
                'allegation_count': 20,
                'complaint_percentile': 99.99,
                'honorable_mention_count': 3,
                'sustained_count': 4,
                'unsustained_count': 5,
                'discipline_count': 6,
                'civilian_compliment_count': 2,
                'trr_count': 7,
                'major_award_count': 8,
                'honorable_mention_percentile': 88.88,
                'to': '/officer/123/michael-flynn/',
                'url': f'{settings.V1_URL}/officer/michael-flynn/123',
                'tags': ['tag1', 'tag2'],
                'coaccusals': [{
                    'id': 789,
                    'coaccusal_count': 10
                }],
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
            }
        ]
