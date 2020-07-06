## Pinboard complainants summary [/mobile/pinboards/{pk}/complainants-summary]

### Get complainants summary for current pinboard

+ Parameters
    + pk (string) - ID of Pinboard

+ Response 200 (application/json)

        {
            "race": [
                {
                    "race": "Black",
                    "percentage": 0.7
                },
                {
                    "race": "White",
                    "percentage": 0.13
                },
                {
                    "race": "Hispanic",
                    "percentage": 0.06
                },
                {
                    "race": "Other",
                    "percentage": 0.11
                }
            ],
            "gender": [
                {
                    "gender": "M",
                    "percentage": 0.51
                },
                {
                    "gender": "F",
                    "percentage": 0.45
                },
                {
                    "gender": "Unknown",
                    "percentage": 0.04
                }
            ]
        }
