## Unit summary [/units/{unit_id}/summary]

### Get Unit Summary [GET]

+ Parameters
    + unit_id (number) - number ID of the unit

+ Response 200 (application/json)

        {
            "unit_name": "001",
            "member_records": {
                "active_members": 72,
                "total": 156,
                "facets": [
                    {
                        "name": "race",
                        "entries": [
                            {
                                "name": "White",
                                "count": 10
                            },
                            {
                                "name": "Unknown",
                                "count": 1
                            }
                        ]
                    },
                    {
                        "name": "age",
                        "entries": [
                            {
                                "name": "21-30",
                                "count": 10
                            },
                            {
                                "name": "51+",
                                "count": 2
                            }
                        ]
                    },
                    {
                        "name": "gender",
                        "entries": [
                            {
                                "name": "Male",
                                "count": 10
                            },
                            {
                                "name": "Female",
                                "count": 6
                            },
                            {
                                "name": "X",
                                "count": 4
                            },
                            {
                                "name": "Unknown",
                                "count": 2
                            }
                        ]
                    }
                ]
            },
            "complaint_records": {
                "count": 27,
                "sustained_count": 3,
                "facets": [
                    {
                        "name": "category",
                        "entries": [
                            {
                                "name": "Illegal Search",
                                "count": 12,
                                "sustained_count": 2
                            }
                        ]
                    },
                    {
                        "name": "race"
                        "entries": [
                            {
                                "name": "White",
                                "count": 9,
                                "sustained_count": 1
                            }
                        ]
                    },
                    {
                        "name": "age",
                        "entries": [
                            {
                                "name": "21-30",
                                "count": 5,
                                "sustained_count": 0
                            }
                        ]
                    },
                    {
                        "name": "gender",
                        "entries": [
                            {
                                "name": "Female",
                                "count": 2,
                                "sustained_count": 0
                            }
                        ]
                    }
                ]
            }
        }
