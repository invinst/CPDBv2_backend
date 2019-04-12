## Pinboard relevant documents [/pinboards/{pinboard_id}/relevant-documents/{?offset,limit}]

### Get Pinboard relevant documents list [GET]

+ Parameters
    + pinboard_id (number) - number ID of the pinboard
    + offset (number, optional) - offset from which to get additional results
        + Default: `0`
    + limit (number, optional) - limit of how many results to return
        + Default: `20`

+ Response 200 (application/json)

        {
          "count": 100,
          "previous": "http://cpdp.co/pinboards/f871a13f/relevant-documents/?",
          "next": "http://cpdp.co/pinboards/f871a13f/relevant-documents/?limit=20&offset=40",
          "results": [
            {
              "preview_image_url": "http://via.placeholder.com/121x157",
              "url": "https://assets.documentcloud.org/documents/5680384/CRID-1083633-CR-CRID-1083633-CR-Tactical.pdf",
              "allegation": {
                "crid": "1071234",
                "category": "Lockup Procedures",
                "incident_date": "2004-04-23",
                "officers": [
                  {
                    "id": 123,
                    "rank": "Detective",
                    "full_name": "Richard Sullivan",
                    "coaccusal_count": 53
                  },
                  {
                    "id": 456,
                    "rank": "Officer",
                    "full_name": "Baudilio Lopez",
                    "coaccusal_count": 47
                  }
                ]
              }
            },
            {
              "preview_image_url": "http://via.placeholder.com/121x157",
              "url": "https://assets.documentcloud.org/documents/5680384/CRID-1083633-CR-CRID-1083633-CR-Tactical.pdf",
              "allegation": {
                "crid": "1079876",
                "category": "Operations/Personnel Violation",
                "incident_date": "2014-05-02",
                "officers": []
              }
            },
            ...
          ]
        }


## Pinboard relevant coaccusals [/pinboards/{pinboard_id}/relevant-coaccusals/{?offset,limit}]

### Get Pinboard relevant coaccusals list [GET]

+ Parameters
    + pinboard_id (number) - number ID of the pinboard
    + offset (number, optional) - offset from which to get additional results
        + Default: `0`
    + limit (number, optional) - limit of how many results to return
        + Default: `20`

+ Response 200 (application/json)

        {
          "count": 100,
          "previous": "http://cpdp.co/pinboards/f871a13f/relevant-coaccusals/?",
          "next": "http://cpdp.co/pinboards/f871a13f/relevant-coaccusals/?limit=20&offset=40",
          "results": [
            {
              "id": 123,
              "rank": "Detective",
              "full_name": "Richard Sullivan",
              "coaccusal_count": 53
            },
            {
              "id": 456,
              "rank": "Officer",
              "full_name": "Baudilio Lopez",
              "coaccusal_count": 47
            },
            ...
          ]
        }


## Pinboard relevant complaints [/pinboards/{pinboard_id}/relevant-complaints/{?offset,limit}]

### Get Pinboard relevant complaints list [GET]

+ Parameters
    + pinboard_id (number) - number ID of the pinboard
    + offset (number, optional) - offset from which to get additional results
        + Default: `0`
    + limit (number, optional) - limit of how many results to return
        + Default: `20`

+ Response 200 (application/json)

        {
          "count": 100,
          "previous": "http://cpdp.co/pinboards/f871a13f/relevant-complaints/?",
          "next": "http://cpdp.co/pinboards/f871a13f/relevant-complaints/?limit=20&offset=40",
          "results": [
            {
              "crid": "1071234",
              "category": "Lockup Procedures",
              "incident_date": "2004-04-23",
              "point": {"lon": 12.0, "lat": 21.0},
              "officers": [
                {
                  "id": 123,
                  "rank": "Detective",
                  "full_name": "Richard Sullivan",
                  "coaccusal_count": 53
                },
                {
                  "id": 456,
                  "rank": "Officer",
                  "full_name": "Baudilio Lopez",
                  "coaccusal_count": 47
                }
              ]
            },
            {
              "crid": "1079876",
              "cateory": "Operations/Personnel Violation",
              "incident_date": "2014-05-02",
              "point": null,
              "officers": []
            },
            ...
          ]
        }
