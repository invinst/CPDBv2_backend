## Sign In [/users/sign-in/]

### Sign in and get an api access token [POST]

+ Request (application/json)

        {
            "username": "admin",
            "password": "admin@123"
        }

+ Response 200 (application/json)

        {
            "apiAccessToken": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
        }

+ Request (application/json)

        {
            "username": "incorrectname",
            "password": "password"
        }

+ Response 400 (application/json)

        {
            "message": "Sorry, you‚Äôve entered an incorrect name."
        }

+ Request (application/json)

        {
            "username": "admin",
            "password": "incorrect"
        }

+ Response 400 (application/json)

        {
            "message": "You‚Äôve entered an incorrect password."
        }
