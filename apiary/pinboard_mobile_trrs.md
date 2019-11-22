## Pinboard mobile trrs [/mobile/pinboards/{pk}/trrs]

### Get selected trrs

+ Parameters
    + pk (number) - number ID of Pinboard

+ Response 200 (application/json)

        [
            {
                'id': 1,
                'trr_datetime': '2012-01-01',
                'category': 'Impact Weapon',
                'point': {'lon': 1.0, 'lat': 1.0},
            },
            {
                'id': 2,
                'trr_datetime': '2013-01-01',
                'category': 'Unknown',
                'point': {'lon': 2.0, 'lat': 2.0},
            }
        ]
