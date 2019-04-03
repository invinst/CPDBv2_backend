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
