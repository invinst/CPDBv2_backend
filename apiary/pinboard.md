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
            "id": "5cd06f2b",
            "title": "My Pinboard",
            "officer_ids": [1, 2],
            "crids": ["123abc"],
            "trr_ids": [1],
            "description": "abc"
        }
        
### Create a pinboard with some missing item ids [POST]

+ Request

        {
            "title": "My Pinboard",
            "officer_ids": [1, 2, 0, 666],
            "crids": ['123abc', '666zzz'],
            "trr_ids": [0, 1, 5],
            "description": "abc"
        }

+ Response 201 (application/json)

        {
            "id": "5cd06f2b",
            "title": "My Pinboard",
            "officer_ids": [1, 2],
            "crids": ["123abc"],
            "trr_ids": [1],
            "description": "abc",
            "not_found_items": {
                "officer_ids": [0, 666],
                "crids": ["666zzz"],
                "trr_ids": [0, 5]
            }
        }



## Individual Pinboard [/pinboards/{pk}/]

### Retrieve a pinboard [GET]

+ Parameters
    + pk (number) - number ID of Pinboard

+ Response 200 (application/json)

        {
            "id": "5cd06f2b",
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
            "id": "5cd06f2b",
            "title": "My Pinboard",
            "officer_ids": [1, 2],
            "crids": ['123abc'],
            "trr_ids": [1],
            "description": "abc"
        }

## All Pinboards [/pinboards/all/]

### Get all pinboards [GET]

+ Parameters
    + offset (number, optional) - offset from which to get additional results
        + Default: `0`
    + limit (number, optional) - limit of how many results to return
        + Default: `20`

+ Response 200 (application/json)

        {
            count: 1000,
            next: '/pinboards/all/?limit=20&offset=20',
            previous: null,
            results: [
                {
                    'id': '197dcdc7',
                    'title': '',
                    'description': '',
                    'created_at': '2019-10-25',
                    'officers_count': 7,
                    'allegations_count': 7,
                    'trrs_count': 0,
                },
                {
                    'id': '361ee7cc',
                    'title': '',
                    'description': '',
                    'created_at': '2019-10-25',
                    'officers_count': 1,
                    'allegations_count': 0,
                    'trrs_count': 0,
                },
                {
                    'id': 'c08762fa',
                    'title': '',
                    'description': '',
                    'created_at': '2019-10-25',
                    'officers_count': 4,
                    'allegations_count': 4,
                    'trrs_count': 0,
                },
            ],
        }
