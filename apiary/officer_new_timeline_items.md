## Officer new timeline items list [/officers/{officer_id}/new-timeline-items]

### Get Officer new timeline items list [GET]

+ Parameters
    + officer_id (number) - number ID of the officer

+ Response 200 (application/json)

        [{
            "date": "2011-09-23",
            "kind": "FORCE",
            "taser": "true",
            "firearm_used": "false",
            "unit_name": "001",
            "rank": "Police Officer",
            "point": {
                "lon": 16.5,
                "lat": 67.8
            }
        }, {
            "date": "2011-08-23",
            "kind": "CR",
            "crid": "123456",
            "category": "category",
            "subcategory": "sub category",
            "finding": "Unfounded",
            "outcome": "Unknown",
            "coaccused": 4,
            "unit_name": "001",
            "rank": "Police Officer",
            "point": {
                "lon": 35.8,
                "lat": 76.8
            },
            "victims": [{
                "gender": "Male",
                "race": "White",
                "age": 34
            }, {
                "gender": "Female",
                "race": "Black",
                "age": 42
            }]
        }, {
            "date": "2011-03-23",
            "kind": "AWARD",
            "award_type": "Honorable Mention",
            "unit_name": "001",
            "rank": "Police Officer"
        }, {
            "date": "2010-01-01",
            "kind": "UNIT_CHANGE",
            "unit_name": "001",
            "rank": "Police Officer"
        }, {
            "date": "2000-01-01",
            "kind": "JOINED",
            "unit_name": "",
            "rank": "Police Officer"
        }]
