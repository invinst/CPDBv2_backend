## Mobile TRR Documents [/mobile/trr/{trr_id}/request-document/]

### Request document [POST]

+ Parameters
    + trr_id (number) - number ID of TRR

+ Request (application/json)

        {
            "email": "asdf@example.com"
        }

+ Response 200 (application/json)

        {
            "trr_id": "293928",
            "message": "Thanks for subscribing"
        }

+ Request (application/json)

        {
            "email": "already_used@example.com"
        }

+ Response 200 (application/json)

        {
            "trr_id": "293928",
            "message": "Email already added"
        }

+ Request (application/json)

        {
            "email": "malformed email"
        }

+ Response 400 (application/json)

        {
            "message": "Please enter a valid email"
        }
