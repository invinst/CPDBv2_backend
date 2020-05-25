## General search [/v1/suggestion/{term}/?limit={limit}]

+ Parameters
    + term (string) - Search term
    + limit (number) - Django REST framework limit pagination

### Get search results [GET]

+ Response 200 (application/json)

        {
          "NEIGHBORHOOD": [
            {
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
              "allegation_count": 1081,
              "id": "345"
            },
            {
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
              "allegation_count": 903,
              "id": "339"
            }
          ],
          "CO-ACCUSED": [
            {
              "to": "/officer/28416/henry-thomas/",
              "result_extra_information": "Badge # 20455",
              "result_reason": "coaccused with Walter Ware (17626)",
              "id": "AV_JHHFVEEvAIPTOfirI"
            },
            {
              "to": "/officer/32306/geno-rouse/",
              "result_extra_information": "Badge # 2155",
              "result_reason": "coaccused with Walter Ware (17626)",
              "id": "AV_JHHFfEEvAIPTOfirL"
            },
          ],
          "COMMUNITY": [
            {
              "median_income": "$43,990",
              "tags": [ "community" ],
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
              ],
              "id": "497"
            },
            {
              "median_income": "$21,869",
              "tags": [ "community" ],
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
              ],
              "id": "432"
            }
          ],
          "UNIT": [{
            "tags": [ ],
            "name": "001",
            "description": "District 001",
            "to": "/unit/001/",
            "id": "2"
          }],
          "UNIT > OFFICERS": [{
            "name": "Robert Bullington",
            "to": "/officer/3277/robert-bullington/",
            "tags": [ ],
            "birth_year": 1963,
            "race": "White",
            "gender": "Male",
            "badge": "8684",
            "rank": "Police Officer",
            "unit": {
              "unit_name": "001",
              "description": "District 001",
              "id": 2,
              "long_unit_name": "Unit 001"
            },
            "appointed_date": "1988-11-07",
            "resignation_date": null,
            "allegation_count": 79,
            "sustained_count": 2,
            "trr_count": 0,
            "discipline_count": 1,
            "honorable_mention_count": 13,
            "civilian_compliment_count": 10,
            "major_award_count": 0,
            "honorable_mention_percentile": 63.7869,
            "percentiles": [{
              "percentile_allegation_civilian": "98.5779",
              "year": 2000,
              "id": 3277,
              "percentile_allegation_internal": "0.0000",
              "percentile_allegation": "98.9364"
            }, {
              "percentile_allegation_civilian": "98.8863",
              "year": 2001,
              "id": 3277,
              "percentile_allegation_internal": "0.0000",
              "percentile_allegation": "99.0767"
            }],
            "id": "3277"
          }],
          "OFFICER": [
            {
              "visual_token_background_color": "#90b1f5",
              "result_extra_information": "Badge # 2328",
              "rank": "Sergeant Of Police",
              "sex": "Male",
              "result_reason": "",
              "unit": "005",
              "salary": null,
              "tags": [],
              "to": "/officer/29841/tommy-walker/",
              "race": "Black",
              "id": "29841"
            },
            {
              "visual_token_background_color": "#90b1f5",
              "result_extra_information": "Badge # 1730",
              "rank": "Sergeant Of Police",
              "sex": "Male",
              "result_reason": "",
              "unit": "008",
              "salary": null,
              "tags": [],
              "to": "/officer/29833/corey-walker/",
              "race": "Black",
              "id": "29833"
            },
          ],
          "RANK": [{
            "id": "Chief",
            "name": "Chief",
            "active_officers_count": 12,
            "officers_most_complaints": [{
              "id": 123,
              "name": "John Hollowell",
              "count": 11,
              "percentile_allegation": "76.2821",
              "percentile_allegation_civilian": "79.4791",
              "percentile_allegation_internal": "0.0001"
              "percentile_trr": "99.0001"
            }]
          }],
          CR: [{
            "id": "1054693",
            "crid": "1054693",
            "to": "/complaint/1054693/",
            "incident_date": "2011-10-15",
            "category": "Use Of Force",
            "sub_category": "Civil Suits - Third Party",
            "address": "22XX East 103RD ST, CHICAGO ILLINOIS 60617",
            "victims": [{
              "gender": "Male",
              "race": "Black"
            }],
            "coaccused": [{
              "id": 20661,
              "full_name": "Mark Nottoli",
              "percentile_trr": "88.0064",
              "percentile_allegation_civilian": "94.6432",
              "percentile_allegation_internal": "79.9133"
              "allegation_count": 52
            }],
            "highlight": {
              "summary": [
                "immediate notification by telephone to the operations <em>command</em> and the Independent Police Review Authority (IPRA)"
              ],
              text_content: [
                "the investigation file, the recommendations of <em>Command</em> Channel Review and the Chief of the Bureau of Internal",
                "toward a supervisory member on or off duty”). <em>Command</em> Channel Review -- the District Commander and Deputy",
              ]
            }
          }]
        }
