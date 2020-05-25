## Officer Mobile [/mobile/officers/{officer_id}/]

### Get Officer Summary (include yearly percentiles) [GET]

+ Parameters
    + officer_id (number) - number ID of the officer

+ Response 200 (application/json)

        {
            "officer_id": 1,
            "full_name": "Robert Anderson",
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
            ],
            "unit": {
              "unit_id": 2,
              "unit_name": "001",
              "description": "District 001"
            },
            "date_of_appt": "1992-01-02",
            "active": true,
            "rank": "Police Officer",
            "race": "White",
            "birth_year": 1965,
            "badge": "19675",
            "historic_badges": [
              "8137"
            ],
            "gender": "Male",
            "allegation_count": 125,
            "percentile_trr": "0.000",
            "percentile_allegation": "58.446",
            "honorable_mention_count": 29,
            "sustained_count": 0,
            "discipline_count": 0,
            "civilian_compliment_count": 8,
            "trr_count": 24,
            "major_award_count": 0,
            "honorable_mention_percentile": 75.5604
        }
