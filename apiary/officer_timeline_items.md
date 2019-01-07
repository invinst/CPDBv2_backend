## Officer timeline items list [/officers/{officer_id}/timeline-items/{?offset,limit}]

### Get Officer timeline items list [GET]

+ Parameters
    + officer_id (number) - number ID of the officer
    + offset (number, optional) - offset from which to get additional results
        + Default: `0`
    + limit (number, optional) - limit of how many results to return
        + Default: `20`

+ Response 200 (application/json)

        {
            "count": 20,
            "previous": null,
            "next": "http://cpdp.co/officers/123/timeline-items/?offset=20"
            "results": [
                {
                    "kind": "YEAR",
                    "crs": 2,
                    "year": 2016,
                    "trrs": 0,
                    "salary": 46492.96
                },
                {
                    "kind": "CR",
                    "crid": "307965",
                    "category": "Illegal Search",
                    "subcategory": "Search of premise/vehicle without warrant",
                    "finding": "Unfounded",
                    "coaccused": 4,
                    "date": "2016-08-24"
                },
                {
                    "kind": "UNIT_CHANGE",
                    "unit_name": "003",
                    "date": "2016-08-24"
                },
                {
                    "kind": "JOINED",
                    "date": "2012-08-24"
                }
            ]
        }
