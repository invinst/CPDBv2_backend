## Pinboard trrs [/pinboards/{pk}/trrs]

### Get selected trrs

+ Parameters
    + pk (number) - number ID of Pinboard

+ Response 200 (application/json)

        [
            {
                'id': 1,
                'trr_datetime': '2012-01-01',
                'category': 'Impact Weapon',
            },
            {
                'id': 2,
                'trr_datetime': '2013-01-01',
                'category': 'Unknown',
            }
        ]
