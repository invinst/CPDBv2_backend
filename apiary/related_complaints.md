## Related Complaints [/cr/{crid}/related-complaints/{?match,distance,offset,limit}]

### Get related complaints [GET]

+ Parameters
    + crid (number, required) - number ID of Allegation
    + match (enum[string], required) - whether the related complaints have similar categories or similar officers
        + Members
            + `categories`
            + `officers`
    + distance (enum[number], required) - distance from where this incident happen in miles
        + Members
            + `0.5`
            + `1`
            + `2.5`
            + `5`
            + `10`
    + offset (number, optional) - offset from which to get additional results
        + Default: `0`
    + limit (number, optional) - limit of how many results to return
        + Default: `20`

+ Response 200 (application/json)

        {
            "count": 1,
            "previous": null,
            "next": null
            "results": [
                {
                    "crid": "838409",
                    "complainants": [{
                        "race": "White",
                        "gender": "Male",
                        "age": 18
                    }],
                    "coaccused": [
                        "R. Piwnicki",
                        "T. Parker"
                    ],
                    "category_names": [
                        "False Arrest",
                        "Use Of Force"
                    ],
                    "point": {
                        "lat": 84.343,
                        "lon": 1.3434
                    }
                    "incident_date": "2016-02-23"
                }
            ]
        }
