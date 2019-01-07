## CMS Page [/cms-pages/{page_id}/]

+ Parameters
    + page_id (string) - ID of the Page that look like a slug

### Get CMS page content [GET]

**Properties**:

- `fields` is an array of fields. Each fields has `name`, `type` and `value`. `value` is an opaque object that should be only of interest to whatever module that deal with it directly. As such it's content might violate some of conventions followed elsewhere such as having property name be in snake case.

+ Response 200 (application/json)

        {
            "fields": [
                {
                    "name": "vftg_date",
                    "type": "date",
                    "value": "2016-10-07"
                },
                {
                    "name": "vftg_link",
                    "type": "link",
                    "value": "https://google.com"
                },
                {
                    "name": "vftg_content",
                    "type": "plain_text",
                    "value": {
                        "blocks": [
                            {
                                "data": {},
                                "depth": 0,
                                "entityRanges": [],
                                "inlineStyleRanges": [],
                                "key": "5gia1",
                                "text": "Real Independence for Police Oversight Agencies",
                                "type": "unstyled"
                            }
                        ],
                        "entityMap": {}
                    }
                },
                {
                    "name": "collaborate_header",
                    "type": "plain_text",
                    "value": {
                        "blocks": [
                            {
                                "data": {},
                                "depth": 0,
                                "entityRanges": [],
                                "inlineStyleRanges": [],
                                "key": "5gia1",
                                "text": "Collaborate With Us.",
                                "type": "unstyled"
                            }
                        ],
                        "entityMap": {}
                    }
                },
                {
                    "name": "collaborate_content",
                    "type": "multiline_text",
                    "value": {
                        "blocks": [
                            {
                                "data": {},
                                "depth": 0,
                                "entityRanges": [],
                                "inlineStyleRanges": [],
                                "key": "a4b9s",
                                "text": "We are collecting and publishing information that sheds light on police misconduct.",
                                "type": "unstyled"
                            },
                            {
                                "data": {},
                                "depth": 0,
                                "entityRanges": [],
                                "inlineStyleRanges": [],
                                "key": "a4b9z",
                                "text": "If you have documents or datasets you would like to publish, please email us, or learn more.",
                                "type": "unstyled"
                            }
                        ],
                        "entityMap": {}
                    }
                },
                {
                    "name": "about_header",
                    "type": "plain_text",
                    "value": {
                        "blocks": [
                            {
                                "data": {},
                                "depth": 0,
                                "entityRanges": [],
                                "inlineStyleRanges": [],
                                "key": "a89s0",
                                "text": "About",
                                "type": "unstyled"
                            }
                        ],
                        "entityMap": {}
                    }
                },
                {
                    "name": "about_content",
                    "type": "multiline_text",
                    "value": {
                        "blocks": [
                            {
                                "data": {},
                                "depth": 0,
                                "entityRanges": [],
                                "inlineStyleRanges": [],
                                "key": "a9sn8",
                                "text": "The Citizens Police Data Project houses police disciplinary information obtained from the City of Chicago..",
                                "type": "unstyled"
                            },
                            {
                                "data": {},
                                "depth": 0,
                                "entityRanges": [],
                                "inlineStyleRanges": [],
                                "key": "a9sn5",
                                "text": "The information and stories we have collected here are intended as a resource for public oversight. Our aim is to create a new model of accountability between officers and citizens.",
                                "type": "unstyled"
                            }
                        ],
                        "entityMap": {}
                    }
                }
            ]
        }

### Partial update CMS page content [PATCH]

This api require an api access token set in `Authorization` header. To get an api access token, use **Sign In** api.

+ Request (application/json)

    + Headers

            Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

    + Body

            {
                "fields": [
                    {
                        "name": "collaborate_header",
                        "type": "plain_text",
                        "value": {
                            "blocks": [
                                {
                                    "data": {},
                                    "depth": 0,
                                    "entityRanges": [],
                                    "inlineStyleRanges": [],
                                    "key": "5gia1",
                                    "text": "Collaborate With Us.",
                                    "type": "unstyled"
                                }
                            ],
                            "entityMap": {}
                        }
                    },
                    {
                        "name": "collaborate_content",
                        "type": "multiline_text",
                        "value": {
                            "blocks": [
                                {
                                    "data": {},
                                    "depth": 0,
                                    "entityRanges": [],
                                    "inlineStyleRanges": [],
                                    "key": "a4b9s",
                                    "text": "We are collecting and publishing information that sheds light on police misconduct.",
                                    "type": "unstyled"
                                },
                                {
                                    "data": {},
                                    "depth": 0,
                                    "entityRanges": [],
                                    "inlineStyleRanges": [],
                                    "key": "a4b9z",
                                    "text": "If you have documents or datasets you would like to publish, please email us, or learn more.",
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
                "fields": [
                {
                    "name": "vftg_date",
                    "type": "date",
                    "value": "2016-10-07"
                },
                {
                    "name": "vftg_link",
                    "type": "link",
                    "value": "https://google.com"
                },
                {
                    "name": "vftg_content",
                    "type": "plain_text",
                    "value": {
                        "blocks": [
                            {
                                "data": {},
                                "depth": 0,
                                "entityRanges": [],
                                "inlineStyleRanges": [],
                                "key": "5gia1",
                                "text": "Real Independence for Police Oversight Agencies",
                                "type": "unstyled"
                            }
                        ],
                        "entityMap": {}
                    }
                },
                {
                    "name": "collaborate_header",
                    "type": "plain_text",
                    "value": {
                        "blocks": [
                            {
                                "data": {},
                                "depth": 0,
                                "entityRanges": [],
                                "inlineStyleRanges": [],
                                "key": "5gia1",
                                "text": "Collaborate With Us.",
                                "type": "unstyled"
                            }
                        ],
                        "entityMap": {}
                    }
                },
                {
                    "name": "collaborate_content",
                    "type": "multiline_text",
                    "value": {
                        "blocks": [
                            {
                                "data": {},
                                "depth": 0,
                                "entityRanges": [],
                                "inlineStyleRanges": [],
                                "key": "a4b9s",
                                "text": "We are collecting and publishing information that sheds light on police misconduct.",
                                "type": "unstyled"
                            },
                            {
                                "data": {},
                                "depth": 0,
                                "entityRanges": [],
                                "inlineStyleRanges": [],
                                "key": "a4b9z",
                                "text": "If you have documents or datasets you would like to publish, please email us, or learn more.",
                                "type": "unstyled"
                            }
                        ],
                        "entityMap": {}
                    }
                },
                {
                    "name": "about_header",
                    "type": "plain_text",
                    "value": {
                        "blocks": [
                            {
                                "data": {},
                                "depth": 0,
                                "entityRanges": [],
                                "inlineStyleRanges": [],
                                "key": "a89s0",
                                "text": "About",
                                "type": "unstyled"
                            }
                        ],
                        "entityMap": {}
                    }
                },
                {
                    "name": "about_content",
                    "type": "multiline_text",
                    "value": {
                        "blocks": [
                            {
                                "data": {},
                                "depth": 0,
                                "entityRanges": [],
                                "inlineStyleRanges": [],
                                "key": "a9sn8",
                                "text": "The Citizens Police Data Project houses police disciplinary information obtained from the City of Chicago..",
                                "type": "unstyled"
                            },
                            {
                                "data": {},
                                "depth": 0,
                                "entityRanges": [],
                                "inlineStyleRanges": [],
                                "key": "a9sn5",
                                "text": "The information and stories we have collected here are intended as a resource for public oversight. Our aim is to create a new model of accountability between officers and citizens.",
                                "type": "unstyled"
                            }
                        ],
                        "entityMap": {}
                    }
                }
            ]
        }

+ Request (application/json)

        {
            "fields": [
                {
                    "name": "collaborate_header",
                    "type": "plain_text",
                    "value": {
                        "blocks": [
                            {
                                "data": {},
                                "depth": 0,
                                "entityRanges": [],
                                "inlineStyleRanges": [],
                                "key": "5gia1",
                                "text": "Collaborate With Us.",
                                "type": "unstyled"
                            }
                        ],
                        "entityMap": {}
                    }
                }
            ]
        }

+ Response 401 (application/json)

    + Headers

            WWW-Authenticate: Token
