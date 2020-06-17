## Pinboard trrs [/pinboards/{pk}/trrs]

### Get selected trrs

+ Parameters
    + pk (string) - ID of Pinboard

+ Response 200 (application/json)

        [
            {
                'id': 1,
                'trr_datetime': '2012-01-01',
                'category': 'Impact Weapon',
                'point': {'lon': 1.0, 'lat': 1.0},
                'to': '/trr/1/',
                'taser': False,
                'firearm_used': False,
                'address': '14XX CHICAGO IL 60636',
                'officer': {
                    'id': 1,
                    'full_name': 'Daryl Mack',
                    'complaint_count': 0,
                    'sustained_count': 0,
                    'birth_year': 1975,
                    'complaint_percentile': 99.345,
                    'race': 'White',
                    'gender': 'Male',
                    'rank': 'Police Officer',
                    'percentile': {
                        'percentile_trr': '12.0000',
                        'percentile_allegation_civilian': '98.4344',
                        'percentile_allegation_internal': '99.7840',
                    }
                }
            },
            {
                'id': 2,
                'trr_datetime': '2013-01-01',
                'category': 'Unknown',
                'point': {'lon': 2.0, 'lat': 2.0},
                'to': '/trr/2/',
                'taser': False,
                'firearm_used': False,
                'address': '14XX CHICAGO IL 60636',
                'officer': {
                    'id': 1,
                    'full_name': 'Daryl Mack',
                    'complaint_count': 0,
                    'sustained_count': 0,
                    'birth_year': 1975,
                    'complaint_percentile': 99.345,
                    'race': 'White',
                    'gender': 'Male',
                    'rank': 'Police Officer',
                    'percentile': {
                        'percentile_trr': '12.0000',
                        'percentile_allegation_civilian': '98.4344',
                        'percentile_allegation_internal': '99.7840',
                    }
                }
            }
        ]
