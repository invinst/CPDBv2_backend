## Pinboard complaints [/pinboards/{pk}/officers]

### Get selected officers

+ Parameters
    + pk (number) - number ID of Pinboard

+ Response 200 (application/json)

        [
            {
                'id': 1,
                'full_name': 'Daryl Mack',
                'complaint_count': 0,
                'sustained_count': 0,
                'birth_year': 1975,
                'complaint_percentile': 99.3450,
                'race': 'White',
                'gender': 'Male',
                'rank': 'Police Officer',
                'percentile': {
                    'percentile_trr': '12.0000',
                    'percentile_allegation': '99.3450',
                    'percentile_allegation_civilian': '98.4344',
                    'percentile_allegation_internal': '99.7840',
                    'year': 2016,
                    'id': 1,
                }
            },
            {
                'id': 2,
                'full_name': 'Ronald Watts',
                'complaint_count': 0,
                'sustained_count': 0,
                'birth_year': 1975,
                'complaint_percentile': 99.5000,
                'race': 'White',
                'gender': 'Male',
                'rank': 'Detective',
                'percentile': {
                    'percentile_trr': '0.0000',
                    'percentile_allegation': '99.5000',
                    'percentile_allegation_civilian': '98.4344',
                    'percentile_allegation_internal': '99.7840',
                    'year': 2016,
                    'id': 2,
                }
            }
        ]
