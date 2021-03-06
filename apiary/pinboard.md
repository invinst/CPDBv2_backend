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
    + pk (string) - ID of Pinboard

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
    + pk (string) - ID of Pinboard

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

### Remove a pinboard [DELETE]

+ Parameters
    + pk (string) - ID of Pinboard

+ Response 200

## Pinboards list [/pinboards/]

### Get all pinboards of current user [GET]

+ Parameters
    + detail (boolean, optional) - return detail pinboard data


+ Response 200 (application/json)
    + detail is false
        ```
            [
                {
                    "id": "5cd06f2b",
                    "title": "My Pinboard 1",
                    "created_at": "2020-04-18",
                    "last_viewed_at": "2020-06-17T03:11:47.384524Z"
                },
                {
                    "id": "962d1e05",
                    "title": "My Pinboard 2",
                    "created_at": "2020-07-18"
                    "last_viewed_at": "2020-06-15T07:08:07.699989Z"
                }
            ]
        ```

    + detail is true
        ```
            [
                {
                    "id": "5cd06f2b",
                    "title": "My Pinboard 1",
                    "created_at": "2020-04-18",
                    "last_viewed_at": "2020-06-16T02:55:33.132359Z",
                    "officer_ids": [1, 2],
                    "crids": ['123abc'],
                    "trr_ids": [1]
                },
                {
                    "id": "962d1e05",
                    "title": "My Pinboard 2",
                    "created_at": "2020-07-18",
                    "last_viewed_at": "2020-06-15T07:09:08.599145Z",
                    "officer_ids": [2, 3],
                    "crids": ['456def'],
                    "trr_ids": [2, 4]
                }
            ]
        ```

## All Pinboards [/pinboards/all/]

### Get all pinboards (authentication required)  [GET]

+ Parameters
    + offset (number, optional) - offset from which to get additional results
        + Default: `0`
    + limit (number, optional) - limit of how many results to return
        + Default: `20`

 + Request
    + Headers

            Authorization: Token ABC123

+ Response 200 (application/json)

        {
            "count": 1112,
            "next": "http://localhost:8000/api/v2/pinboards/all/?limit=20&offset=20",
            "previous": None,
            "results": [
                {
                    allegations_count: 0,
                    created_at: "2019-11-01T09:36:56.978310Z",
                    title: "",
                    description: "",
                    id: "f0e5eba4",
                    officers_count: 1,
                    allegations: [],
                    officers: [
                        {
                            count: 2,
                            id: 5200,
                            name: "Thomas Connor",
                            percentile_allegation: "44.8403",
                            year: 1993
                        }
                    ],
                    trrs: [],
                    trrs_count: 0,
                    child_pinboard_count: 2,
                },
                {
                   "id": "962d1e05",
                    "title": "",
                    "description": "",
                    "created_at": "2019-09-30T10:21:45.864200Z",
                    "officers_count": 4,
                    "allegations_count": 1,
                    "trrs_count": 1,
                    "officers": [
                        {
                            "percentile_allegation": "74.7611",
                            "year": 1993,
                            "id": 5,
                            "name": "Carmen Abbate",
                            "count": 4
                        },
                        {
                            "percentile_allegation_civilian": "58.8524",
                            "percentile_allegation_internal": "0.0000",
                            "percentile_allegation": "49.0044",
                            "year": 2003,
                            "id": 4,
                            "name": "Carmel Abbate",
                            "count": 7
                        },
                        {
                            "percentile_allegation_civilian": "0.0000",
                            "percentile_allegation_internal": "0.0000",
                            "percentile_allegation": "0.0000",
                            "year": 2004,
                            "id": 3,
                            "name": "Daniel Abate",
                            "count": 0
                        },
                        {
                            "percentile_trr": "79.8763",
                            "percentile_allegation_civilian": "61.2069",
                            "percentile_allegation_internal": "76.9384",
                            "percentile_allegation": "61.2357",
                            "year": 2016,
                            "id": 1,
                            "name": "Jeffery Aaron",
                            "count": 6
                        }
                    ],
                    "allegations": [
                        {
                            "crid": "1053673",
                            "category": "False Arrest",
                            "incident_date": "2012-04-26"
                        }
                    ],
                    "trrs": [
                        {
                            "id": 123,
                            "trr_datetime": "2004-02-24",
                            "category": "Physical Force - Holding"
                        }
                    ]
                },
                ...
            ]
        }
