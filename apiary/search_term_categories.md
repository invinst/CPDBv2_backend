## Search term categories list [/search-term-categories/]

### Get Search term categories [GET]

+ Response 200 (application/json)

        [
            {
                "name": "Geography",
                "items": [
                    {
                        "name": "Police Districts",
                        "description": "A form of division of a geographical area patrolled by a police force",
                        "id": "police-districts",
                        "call_to_action_type": "view_all"
                    }
                ]
            },
            {
                "name": "Officers",
                "items": [
                    {
                        "name": "Officer Name",
                        "description": "Type the name of an officer into the search bar",
                        "id": "officer-name",
                        "call_to_action_type": "plain_text"
                    }
                ]
            },
            {
                "name": "Complaint Categories",
                "items": [
                    {
                        "name": "Conduct Unbecoming",
                        "description": "Search the data tool for Conduct Unbecoming",
                        "id": "conduct-unbecoming",
                        "call_to_action_type": "link",
                        "link": "https://data.cpdp.co/url-mediator/session-builder?cat__category=Conduct%20Unbecoming"
                    }
                ]
            }
        ]
