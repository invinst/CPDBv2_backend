## CR Documents [/cr/{crid}/request-document/]

### Request document [POST]

+ Parameters
    + crid (number) - number ID of Allegation

+ Request (application/json)

        {
            "email": "asdf@example.com"
        }

+ Response 200 (application/json)

        {
            "crid": "293928",
            "message": "Thanks for subscribing"
        }

+ Request (application/json)

        {
            "email": "already_used@example.com"
        }

+ Response 200 (application/json)

        {
            "crid": "293928",
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
