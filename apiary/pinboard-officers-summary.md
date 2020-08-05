## Pinboard officers summary [/mobile/pinboards/{pk}/officers-summary]

### Get officers summary for current pinboard

+ Parameters
    + pk (string) - ID of Pinboard

+ Response 200 (application/json)

        {
            "race": [
                {
                    "race": "Black",
                    "percentage": 0.31
                },
                {
                    "race": "White",
                    "percentage": 0.58
                },
                {
                    "race": "Hispanic",
                    "percentage": 0.1
                },
                {
                    "race": "Other",
                    "percentage": 0.01
                }
            ],
            "gender": [
                {
                    "gender": "M",
                    "percentage": 0.98
                },
                {
                    "gender": "F",
                    "percentage": 0.02
                },
                {
                    "gender": "Unknown",
                    "percentage": 0.0
                }
            ]
        }
