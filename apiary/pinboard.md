## Pinboards [/pinboards/]

### Create a pinboard [POST]

+ Request

        {
            "title": "My Pinboard",
            "officer_ids": [1, 2],
            "crids": ['123abc'],
            "trr_ids": [1],
            "description": "abc"
        }

+ Response 201 (application/json)

        {
            "id": 1
            "title": "My Pinboard",
            "officer_ids": [1, 2],
            "crids": ["123abc"],
            "trr_ids": [1],
            "description": "abc"
        }


## Individual Pinboard [/pinboards/{pk}/]

### Retrieve a pinboard [GET]

+ Parameters
    + pk (number) - number ID of Pinboard

+ Response 200 (application/json)


        {
            "id": 1,
            "title": "My Pinboard",
            "officer_ids": [1, 2],
            "crids": ['123abc'],
            "trr_ids": [1],
            "description": "abc"
        }

### Update a pinboard [PUT]

+ Parameters
    + pk (number) - number ID of Pinboard

+ Request

        {
            "title": "My Pinboard",
            "officer_ids": [1, 2],
            "crids": ['123abc'],
            "trr_ids": [1],
            "description": "abc"
        }

+ Response 200 (application/json)

        {
            "id": 1,
            "title": "My Pinboard",
            "officer_ids": [1, 2],
            "crids": ['123abc'],
            "trr_ids": [1],
            "description": "abc"
        }

### Get selected complaints

+ Parameters
    + pk (number) - number ID of Pinboard

+ Response 200 (application/json)

        [
            {
                "crid": "1000001",
                "incident_date": "2010-01-01",
                "point": {"lon": 1.0, "lat": 1.0},
                "most_common_category": "Use Of Force",
            },
            {
                "crid": "1000002",
                "incident_date": "2011-01-01",
                "point": {"lon": 2.0, "lat": 2.0},
                "most_common_category": "Verbal Abuse",
            }
        ]

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
