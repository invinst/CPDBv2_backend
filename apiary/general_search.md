## General search [/v1/suggestion/{term}/?limit={limit}]

+ Parameters
    + term (string) - Search term
    + limit (number) - Django REST framework limit pagination

### Get search results [GET]

+ Response 200 (application/json)

        {
          "NEIGHBORHOOD": [
            {
              "text": "Washington Heights",
              "payload": {
                "name": "Washington Heights",
                "tags": ["neighborhoods"],
                "url": "https://data.cpdp.co/url-mediator/session-builder?neighborhood=Washington Heights",
                "most_common_complaint": [
                    {
                        "count": 104,
                        "id": 204,
                        "name": "Operation/Personnel Violations"
                    },
                    {
                        "count": 66,
                        "id": 98,
                        "name": "Use Of Force"
                    },
                    {
                        "count": 53,
                        "id": 71,
                        "name": "Illegal Search"
                    }
                ],
                "officers_most_complaint": [
                    {
                        "count": 16,
                        "id": 32344,
                        "name": "Brandon Smith"
                    },
                    {
                        "count": 15,
                        "id": 7199,
                        "name": "Richard Doroniuk"
                    },
                    {
                        "count": 15,
                        "id": 9115,
                        "name": "Freddie Frazier"
                    }
                ],
                "result_text": "Washington Heights",
                "allegation_count": 1081
              },
              "id": "345"
            },
            {
              "text": "Washington Park",
              "payload": {
                "name": "Washington Park",
                "tags": ["neighborhoods"],
                "url": "https://data.cpdp.co/url-mediator/session-builder?neighborhood=Washington Park",
                "most_common_complaint": [
                    {
                        "count": 99,
                        "id": 204,
                        "name": "Operation/Personnel Violations"
                    },
                    {
                        "count": 78,
                        "id": 98,
                        "name": "Use Of Force"
                    },
                    {
                        "count": 39,
                        "id": 194,
                        "name": "Operation/Personnel Violations"
                    }
                ],
                "officers_most_complaint": [
                    {
                        "count": 9,
                        "id": 10259,
                        "name": "Daniel Gomez"
                    },
                    {
                        "count": 9,
                        "id": 32154,
                        "name": "Pablo Mariano"
                    },
                    {
                        "count": 7,
                        "id": 966,
                        "name": "Stephen Austin"
                    }
                ],
                "result_text": "Washington Park",
                "allegation_count": 903
              },
              "id": "339"
            }
          ],
          "CO-ACCUSED": [
            {
              "text": "Henry Thomas",
              "payload": {
                "result_text": "Henry Thomas",
                "to": "/officer/28416/henry-thomas/",
                "result_extra_information": "Badge # 20455",
                "result_reason": "coaccused with Walter Ware (17626)"
              },
              "id": "AV_JHHFVEEvAIPTOfirI"
            },
            {
              "text": "Geno Rouse",
              "payload": {
                "result_text": "Geno Rouse",
                "to": "/officer/32306/geno-rouse/",
                "result_extra_information": "Badge # 2155",
                "result_reason": "coaccused with Walter Ware (17626)"
              },
              "id": "AV_JHHFfEEvAIPTOfirL"
            },
          ],
          "COMMUNITY": [
            {
              "text": "Washington Heights",
              "payload": {
                "median_income": "$43,990",
                "tags": [
                    "community"
                ],
                "allegation_count": 1081,
                "most_common_complaint": [
                    {
                        "count": 104,
                        "id": 204,
                        "name": "Operation/Personnel Violations"
                    },
                    {
                        "count": 66,
                        "id": 98,
                        "name": "Use Of Force"
                    },
                    {
                        "count": 53,
                        "id": 71,
                        "name": "Illegal Search"
                    }
                ],
                "officers_most_complaint": [
                    {
                        "count": 16,
                        "id": 32344,
                        "name": "Brandon Smith"
                    },
                    {
                        "count": 15,
                        "id": 7199,
                        "name": "Richard Doroniuk"
                    },
                    {
                        "count": 15,
                        "id": 9115,
                        "name": "Freddie Frazier"
                    }
                ],
                "name": "Washington Heights",
                "url": "https://data.cpdp.co/url-mediator/session-builder?community=Washington Heights",
                "result_text": "Washington Heights",
                "race_count": [
                    {
                        "count": 25968,
                        "race": "Black or African-American"
                    },
                    {
                        "count": 510,
                        "race": "Other"
                    },
                    {
                        "count": 351,
                        "race": "White"
                    },
                    {
                        "count": 287,
                        "race": "Persons of Spanish Language"
                    },
                    {
                        "count": 0,
                        "race": "Asian"
                    }
                ]
              },
              "id": "497"
            },
            {
              "text": "Washington Park",
              "payload": {
                "median_income": "$21,869",
                "tags": [
                    "community"
                ],
                "allegation_count": 903,
                "most_common_complaint": [
                    {
                        "count": 99,
                        "id": 204,
                        "name": "Operation/Personnel Violations"
                    },
                    {
                        "count": 78,
                        "id": 98,
                        "name": "Use Of Force"
                    },
                    {
                        "count": 39,
                        "id": 194,
                        "name": "Operation/Personnel Violations"
                    }
                ],
                "officers_most_complaint": [
                    {
                        "count": 9,
                        "id": 10259,
                        "name": "Daniel Gomez"
                    },
                    {
                        "count": 9,
                        "id": 32154,
                        "name": "Pablo Mariano"
                    },
                    {
                        "count": 7,
                        "id": 966,
                        "name": "Stephen Austin"
                    }
                ],
                "name": "Washington Park",
                "url": "https://data.cpdp.co/url-mediator/session-builder?community=Washington Park",
                "result_text": "Washington Park",
                "race_count": [
                    {
                        "count": 11595,
                        "race": "Black or African-American"
                    },
                    {
                        "count": 271,
                        "race": "Other"
                    },
                    {
                        "count": 158,
                        "race": "Persons of Spanish Language"
                    },
                    {
                        "count": 48,
                        "race": "White"
                    },
                    {
                        "count": 9,
                        "race": "Asian"
                    }
                ]
              },
              "id": "432"
            }
          ],
          "UNIT": [],
          "UNIT > OFFICERS": [],
          "OFFICER": [
            {
              "text": "Tommy Walker",
              "payload": {
                "visual_token_background_color": "#90b1f5",
                "result_extra_information": "Badge # 2328",
                "rank": "Sergeant Of Police",
                "sex": "Male",
                "result_reason": "",
                "unit": "005",
                "salary": null,
                "result_text": "Tommy Walker",
                "tags": [],
                "to": "/officer/29841/tommy-walker/",
                "race": "Black"
              },
              "id": "29841"
            },
            {
              "text": "Corey Walker",
              "payload": {
                "visual_token_background_color": "#90b1f5",
                "result_extra_information": "Badge # 1730",
                "rank": "Sergeant Of Police",
                "sex": "Male",
                "result_reason": "",
                "unit": "008",
                "salary": null,
                "result_text": "Corey Walker",
                "tags": [],
                "to": "/officer/29833/corey-walker/",
                "race": "Black"
              },
              "id": "29833"
            },
          ]
        }
