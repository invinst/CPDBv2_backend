## Pinboard complaints [/pinboards/{pk}/complaints]

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
