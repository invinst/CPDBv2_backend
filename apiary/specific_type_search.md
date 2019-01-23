## Specific type search [/v1/suggestion/{term}/single/{?contentType,offset,limit}]

+ Parameters
    + term (string) - Search term
    + contentType (string) - Data content type (OFFICER, UNIT, COMMUNITY, NEIGHBORHOOD, CO-ACCUSED, UNIT > OFFICERS)
    + offset (number, optional) - offset from which to get additional results
        + Default: `0`
    + limit (number, optional) - limit of how many results to return
        + Default: `20`

### Get search results [GET]

+ Response 200 (application/json)

        {
          "count": 2,
          "previous": null,
          "next": null,
          "results": [
            {
              "text": "Orson Ward",
              "payload": {
                "visual_token_background_color": "#c6d4ec",
                "result_extra_information": "Badge # 13603",
                "rank": "Police Officer",
                "sex": "Male",
                "result_reason": "",
                "unit": "010",
                "salary": null,
                "result_text": "Orson Ward",
                "tags": [],
                "to": "/officer/30022/orson-ward/",
                "race": "Black"
              },
              "id": "30022"
            },
            {
              "text": "Orson Kallenback",
              "payload": {
                "visual_token_background_color": "#f5f4f4",
                "result_extra_information": "",
                "rank": "Police Officer",
                "sex": "Male",
                "result_reason": "",
                "unit": "169",
                "salary": null,
                "result_text": "Orson Kallenback",
                "tags": [],
                "to": "/officer/14026/orson-kallenback/",
                "race": "White"
              },
              "id": "14026"
            }
          ]
        }
