## Search Aliases [/aliases/{aliasType}/{id}/]

### Update search aliases for a search result [POST]

+ Parameters
    + aliasType (string) - Can be officer/neighborhood/community/report/unit
    + id (number) - Primary key of search result

+ Request (application/json)

        {
            aliases: ["foo", "bar"]
        }

+ Response 200 (application/json)

        {
            "message": "Aliases successfully updated",
            "aliases": ["foo", "bar"]
        }

+ Request (application/json)

        {
            aliases: ["an alias that is absolutely way too long"]
        }

+ Response 400 (application/json)

        {
            "message": {
                "aliases": ["Ensure this field has no more than 20 characters."]
            }
        }
