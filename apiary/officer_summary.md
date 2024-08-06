## Officer summary [/officers/{officer_id}/summary]

### Get Officer Summary (include bio, metrics, and yearly percentiles) [GET]

+ Parameters
    + officer_id (number) - number ID of the officer

+ Response 200 (application/json)

        {
            "id": 1,
            "unit": {
                "id": 1,
                "unit_name": "001",
                "description": "Unit 001"
            },
            "date_of_appt": "2015-09-23",
            "date_of_resignation": "2017-09-23",
            "active": "Active",
            "rank": "NA",
            "race": "White",
            "badge": "12345",
            "historic_badges": ["22", "33"],
            "historic_units": [
              {
                "id": 1,
                "unit_name": "001",
                "description": "Unit 001"
              },
              {
                "id": 2,
                "unit_name": "002",
                "description": "Unit 002"
              }
            ],
            "gender": "Male",
            "birth_year": 1951,
            "allegation_count": 90,
            'total_lawsuit_settlements': '20500.00',
            "discipline_count": 0,
            "honorable_mention_count": 1,
            "honorable_mention_percentile": "88.777",
            "sustained_count": 4,
            "complaint_records": {
                "count": 27,
                "sustained_count": 0,
                "facets": [
                    {
                        "name": "category",
                        "entries": [
                            {
                                "name": "Illegal Search",
                                "count": 20,
                                "sustained_count": 0
                            },
                            {
                                "name": "Use of Force",
                                "count": 7,
                                "sustained_count": 0
                            }
                        ]
                    },
                    {
                        "name": "race"
                        "entries": [
                            {
                                "name": "White",
                                "count": 7,
                                "sustained_count": 0
                            },
                            {
                                "name": null,
                                "count": 20,
                                "sustained_count": 0
                            }
                        ]
                    },
                    {
                        "name": "age",
                        "entries": [
                            {
                                "name": "18",
                                "count": 20,
                                "sustained_count": 0
                            },
                            {
                                "name": "20",
                                "count": 7,
                                "sustained_count": 0
                            }
                        ]
                    },
                    {
                        "name": "gender",
                        "entries": [
                            {
                                "name": "Famale",
                                "count": 20,
                                "sustained_count": 0
                            },
                            {
                                "name": null,
                                "count": 7,
                                "sustained_count": 0
                            }
                        ]
                    }
                ]
            },
            "percentile_trr": "0.000",
            "percentile_allegation": "58.446",
            "current_salary": 100000,
            "trr_count": 14,
            "major_award_count": 46,
            "complaint_records": {
                "count": 27,
                "sustained_count": 0,
                "facets": [
                    {
                        "name": "category",
                        "entries": [
                            {
                                "name": "Illegal Search",
                                "count": 20,
                                "sustained_count": 0
                            },
                            {
                                "name": "Use of Force",
                                "count": 7,
                                "sustained_count": 0
                            }
                        ]
                    },
                    {
                        "name": "race"
                        "entries": [
                            {
                                "name": "White",
                                "count": 7,
                                "sustained_count": 0
                            },
                            {
                                "name": null,
                                "count": 20,
                                "sustained_count": 0
                            }
                        ]
                    },
                    {
                        "name": "age",
                        "entries": [
                            {
                                "name": "18",
                                "count": 20,
                                "sustained_count": 0
                            },
                            {
                                "name": "20",
                                "count": 7,
                                "sustained_count": 0
                            }
                        ]
                    },
                    {
                        "name": "gender",
                        "entries": [
                            {
                                "name": "Famale",
                                "count": 20,
                                "sustained_count": 0
                            },
                            {
                                "name": null,
                                "count": 7,
                                "sustained_count": 0
                            }
                        ]
                    }
                ]
            },
            "percentiles": [
                {
                    "officer_id": 1,
                    "year": 2016,
                    "percentile_trr": "0.000",
                    "percentile_allegation": "76.282",
                    "percentile_allegation_civilian": "79.479",
                    "percentile_allegation_internal": "0.000"
                },
                {
                    "officer_id": 1,
                    "year": 2017,
                    "percentile_trr": "0.000",
                    "percentile_allegation": "58.446",
                    "percentile_allegation_civilian": "63.044",
                    "percentile_allegation_internal": "0.000"
                }
            ]
        }
