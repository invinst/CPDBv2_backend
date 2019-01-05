## Forgot password [/users/forgot-password/]

### Forgot password [POST]

+ Request (application/json)

        {
            "email": "admin@domain.com"
        }

+ Response 200 (application/json)

        {
            "message": "Please check your email for a password reset link."
        }

+ Request (application/json)

        {
            "email": "unregistered@email.co"
        }

+ Response 400 (application/json)

        {
            "message": "Sorry, there‚Äôs no account registered with this email address."
        }

### Partial Update report [PATCH]

This api require an api access token set in `Authorization` header. To get an api access token, use **Sign In** api.

+ Request (application/json)

    + Headers

            Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

    + Body

            {
                "fields": [
                    {
                        "name": "title",
                        "type": "plain_text",
                        "value": {
                            "blocks": [
                                {
                                    "data": {},
                                    "depth": 0,
                                    "entityRanges": [],
                                    "inlineStyleRanges": [],
                                    "key": "5gia1",
                                    "text": "Commentary: Chicago's police crisis fall on all of us",
                                    "type": "unstyled"
                                }
                            ],
                            "entityMap": {}
                        }
                    },
                    {
                        "name": "excerpt",
                        "type": "multiline_text",
                        "value": {
                            "blocks": [
                                {
                                    "data": {},
                                    "depth": 0,
                                    "entityRanges": [],
                                    "inlineStyleRanges": [],
                                    "key": "a4b9s",
                                    "text": "The “few bad apples” theory of police violence posits that a small portion of the police force is ill-intentioned or inclined to misconduct or violence, while the majority of officers are good cops. Until recently, this theory was difficult for civilians to investigate, but department data on complaints against officers obtained through a legal challenge shows that police misconduct in Chicago is overwhelmingly the product of a small fraction of officers and that it may be possible to identify those officers and reduce misconduct.",
                                    "type": "unstyled"
                                },
                                {
                                    "data": {},
                                    "depth": 0,
                                    "entityRanges": [],
                                    "inlineStyleRanges": [],
                                    "key": "a4b9z",
                                    "text": "This far-reaching data set, a product of the nonprofit Invisible Institute‚Äôs Citizens Police Data Project, comprehensively covers nearly five years of complaints against Chicago police officers. Each of the 28,588 records in the database offers a detailed account of the incident, including information on the accused officer, the complainant, the type of alleged misconduct, and whether the complaint was found legitimate by an internal investigation.",
                                    "type": "unstyled"
                                }
                            ],
                            "entityMap": {}
                        }
                    }
                ]
            }

+ Response 200 (application/json)

            {
                "id": 1,
                "fields": [
                    {
                        "name": "title",
                        "type": "plain_text",
                        "value": {
                            "blocks": [
                                {
                                    "data": {},
                                    "depth": 0,
                                    "entityRanges": [],
                                    "inlineStyleRanges": [],
                                    "key": "5gia1",
                                    "text": "Commentary: Chicago's police crisis",
                                    "type": "unstyled"
                                }
                            ],
                            "entityMap": {}
                        }
                    },
                    {
                        "name": "excerpt",
                        "type": "multiline_text",
                        "value": {
                            "blocks": [
                                {
                                    "data": {},
                                    "depth": 0,
                                    "entityRanges": [],
                                    "inlineStyleRanges": [],
                                    "key": "a4b9s",
                                    "text": "The “few bad apples” theory of police violence posits that a small portion of the police force is ill-intentioned or inclined to misconduct or violence, while the majority of officers are good cops. Until recently, this theory was difficult for civilians to investigate, but department data on complaints against officers obtained through a legal challenge shows that police misconduct in Chicago is overwhelmingly the product of a small fraction of officers and that it may be possible to identify those officers and reduce misconduct.",
                                    "type": "unstyled"
                                },
                                {
                                    "data": {},
                                    "depth": 0,
                                    "entityRanges": [],
                                    "inlineStyleRanges": [],
                                    "key": "a4b9z",
                                    "text": "This far-reaching data set, a product of the nonprofit Invisible Institute‚Äôs Citizens Police Data Project, comprehensively covers nearly five years of complaints against Chicago police officers. Each of the 28,588 records in the database offers a detailed account of the incident, including information on the accused officer, the complainant, the type of alleged misconduct, and whether the complaint was found legitimate by an internal investigation.",
                                    "type": "unstyled"
                                }
                            ],
                            "entityMap": {}
                        }
                    },
                    {
                        "name": "publication",
                        "type": "string",
                        "value": "New York Times"
                    },
                    {
                        "name": "publish_date",
                        "type": "date",
                        "value": "2016-09-23"
                    },
                    {
                        "name": "author",
                        "type": "string",
                        "value": "Edgar Sterling"
                    },
                    {
                        "name": "officers",
                        "type": "officers_list",
                        "value": [
                            {
                                "id": 123,
                                "full_name": "Edgar Davis",
                                "allegation_count": 14,
                                "v1_url": "http://cpdb.co/officer/edgar/123",
                                "gender": "Male",
                                "race": "White"
                            }
                        ]
                    }
                ]

        }
