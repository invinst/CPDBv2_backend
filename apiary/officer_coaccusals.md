## Officer coaccusals [/officers/{officer_id}/coaccusals]

### Get Officer coaccusals [GET]

+ Parameters
    + officer_id (number) - number ID of the officer

+ Response 200 (application/json)

        {
            "id": "8562",
            "coaccusals": [
                {
                    "id": 1,
                    "full_name": "Officer 1",
                    "complaint_count": 2,
                    "sustained_count": 1,
                    "complaint_percentile": 94.0,
                    "race": "White",
                    "gender": "Male",
                    "birth_year": 1950,
                    "coaccusal_count": 2,
                    "rank": "Police Officer",
                    "percentile": {
                        "percentile_trr": "94.0000",
                        "percentile_allegation_internal": "95.0000",
                        "percentile_allegation_civilian": "91.0000",
                        "percentile_allegation": "94.0000",
                        "year": 2016
                    }
                }, {
                    "id": 2,
                    "full_name": "Officer 2",
                    "complaint_count": 1,
                    "sustained_count": 1,
                    "complaint_percentile": 99.0,
                    "race": "Black",
                    "gender": "Male",
                    "birth_year": 1970,
                    "coaccusal_count": 1,
                    "rank": "Police Officer",
                    "percentile": {
                        "percentile_trr": "82.0000",
                        "percentile_allegation_internal": "71.0000",
                        "percentile_allegation_civilian": "98.0000",
                        "percentile_allegation": "95.0000",
                        "year": 2016
                    }
                }
            ]
        }
