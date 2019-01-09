## TRR [/trr/{trr_id}/]

### Get TRR [GET]

+ Parameters
    + trr_id (number) - number ID of Use of Force Report

+ Response 200 (application/json)
        {
            "id": 781,
            "officer": {
                "id": 583,
                "full_name": "Robert Anderson",
                "gender": "Male",
                "race": "White",
                "rank": 'Detective',
                "appointed_date": "2000-10-10",
                "birth_year": 1973,
                "resignation_date": "2008-03-26",
                "unit": {
                    "unit_name": "253",
                    "description": "Targeted Response Unit"
                },
                "percentile_allegation_civilian": 92.7014,
                "percentile_allegation_internal": 0.0,
                "percentile_trr": 76.9689
            },
            "officer_in_uniform": true,
            "officer_assigned_beat": "4682E",
            "officer_on_duty": true,
            "subject_race": "BLACK",
            "subject_gender": "Male",
            "subject_age": 27,
            "force_category": "Other",
            "force_types": [
                "Physical Force - Stunning",
                "Verbal Commands",
                "Member Presence"
            ],
            "date_of_incident": "2004-04-23",
            "location_type": "Street",
            "address": "11XX 79Th St",
            "beat": 612,
            "point": {
                "lat": 41.7508596,
                "lng": -87.6533166
            }
        }
