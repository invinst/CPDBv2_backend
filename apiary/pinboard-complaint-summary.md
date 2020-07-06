## Pinboard complaint summary [/mobile/pinboards/{pk}/complaint-summary]

### Get complaint summary for current pinboard

+ Parameters
    + pk (string) - ID of Pinboard

+ Response 200 (application/json)

        [
            {
                "category": "Use Of Force",
                "count": 134
            },
            {
                "category": "Operation/Personnel Violations",
                "count": 103
            },
            {
                "category": "Traffic",
                "count": 12
            },
            {
                "category": "Criminal Misconduct",
                "count": 11
            },
            {
                "category": null,
                "count": 11
            }
        ]
