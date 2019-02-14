## Attachments [/attachments/]

### Get attachments [GET]

+ Response 200 (application/json)

        {
            "count": 2,
            "next": "http://testserver/api/v2/attachment/?limit=2&offset=2",
            "previous": None,
            "results": [
                {
                    "id": 4677,
                    "created_at": "2017-01-14T06:00:01-06:00",
                    "title": "CRID 1051117 CR",
                    "source_type": "DOCUMENTCLOUD",
                    "preview_image_url": "https://assets.documentcloud.org/documents/4769596/pages/CRID-1051117-CR-p1-normal.gif",
                    "views_count": 1,
                    "downloads_count": 1,
                    "show": true
                },
                {
                    "id": 4829,
                    "created_at": "2017-01-14T06:00:01-06:00",
                    "title": "CRID 1064593 CR",
                    "source_type": "DOCUMENTCLOUD",
                    "preview_image_url": "https://assets.documentcloud.org/documents/4769386/pages/CRID-1064593-CR-p1-normal.gif",
                    "views_count": 2,
                    "downloads_count": 1,
                    "show": false
                }
            ]
        }

## Individual Attachment [/attachments/{pk}/]

### Set attachment's show attribute [PATCH]

+ Parameters
    + pk (number) - number ID of Attachment

+ Request

        {
            "show": true
        }

+ Response 200 (application/json)

        {
            "show": true
        }
