## Pinboard complainants summary [/mobile/pinboards/{pk}/complainants-summary]

### Get complainants summary for current pinboard

+ Parameters
    + pk (string) - ID of Pinboard

+ Response 200 (application/json)

        {
            "race": [
                {
                    "race": "Black",
                    "percentage": 0.67
                },
                {
                    "race": "Other",
                    "percentage": 0.18
                }
                {
                    "race": "White",
                    "percentage": 0.14
                },
            ],
            "gender": [
                {
                    "gender": "F",
                    "percentage": 0.49
                },
                {
                    "gender": "M",
                    "percentage": 0.47
                },
                {
                    "gender": "",
                    "percentage": 0.04
                }
            ]
        }
