## Pinboard officers summary [/mobile/pinboards/{pk}/officers-summary]

### Get officers summary for current pinboard

+ Parameters
    + pk (string) - ID of Pinboard

+ Response 200 (application/json)

        {
            "race": [
                {
                    "race": "Black",
                    "percentage": 0.55
                },
                {
                    "race": "White",
                    "percentage": 0.37
                },
                {
                    "race": "Other",
                    "percentage": 0.08
                }
            ],
            "gender": [
                {
                    "gender": "M",
                    "percentage": 0.96
                },
                {
                    "gender": "F",
                    "percentage": 0.04
                }
            ]
        }
