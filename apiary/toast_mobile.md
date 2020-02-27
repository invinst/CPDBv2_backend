## Mobile Toast [/v2/mobile/toast/]

### Get toast [GET]

+ Response 200 (application/json)

         [
            {
                "name": "OFFICER",
                "template": "{full_name} {action_type} pinboard",

            },
            {
                "name": "CR",
                "template": "CR #{crid} {action_type} pinboard",

            },
            {
                "name": "TRR",
                "template": "TRR #{id} {action_type} pinboard",
            }
         ]
