## Pinboard TRR summary [/mobile/pinboards/{pk}/trr-summary]

### Get TRR summary for current pinboard

+ Parameters
    + pk (string) - ID of Pinboard

+ Response 200 (application/json)

        [
            {
                "force_type": null,
                "count": 331
            },
            {
                "force_type": "Verbal Commands",
                "count": 88
            },
            {
                "force_type": "Physical Force - Stunning",
                "count": 83
            },
            {
                "force_type": "Taser",
                "count": 10
            },
            {
                "force_type": "Chemical",
                "count": 3
            }
        ]
