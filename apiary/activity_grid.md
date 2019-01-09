## Activity grid [/activity-grid/]

### Get activity cards [GET]

+ Response 200 (application/json)

        [
            {
                "id": 1,
                "full_name": "Jerome Finnigan",
                "visual_token_background_color": "#90b1f5",
                "birth_year": 1963,
                "complaint_count": 90,
                "complaint_percentile": 88.55,
                "gender": "Male",
                "rank": "Police Officer",
                "race": "White",
                "sustained_count": 4,
                "percentile": {
                    "officer_id": 5193,
                    "year": 2017,
                    "percentile_trr": "91.696",
                    "percentile_allegation": "99.870",
                    "percentile_allegation_civilian": "99.895",
                    "percentile_allegation_internal": "80.494"
                }
            },
            {
                "id": 2,
                "full_name": "Raymond Piwnicki",
                "visual_token_background_color": "#aec9e8",
                "birth_year": 1963,
                "complaint_count": 89,
                "complaint_percentile": None,
                "gender": "Male",
                "rank": "Detective",
                "race": "White",
                "sustained_count": 6,
                "percentile": {
                    "officer_id": 5193,
                    "year": 2017,
                    "percentile_trr": "91.696",
                    "percentile_allegation": "99.870",
                    "percentile_allegation_civilian": "99.895",
                    "percentile_allegation_internal": "80.494"
                }
            }
        ]
