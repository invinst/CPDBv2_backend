## Attachments [/attachments/{?match,crid,offset,limit}/]

+ Parameters
    + match (string, optional) - String to match against title and CRID
    + crid (string, optional) - CRID to filter attachments
    + offset (number, optional) - offset from which to get additional results
        + Default: `0`
    + limit (number, optional) - limit of how many results to return
        + Default: `20`

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
                    "crid": "123456",
                    "show": true,
                    "documents_count": 4,
                    "crid": "1051117"
                },
                {
                    "id": 4829,
                    "created_at": "2017-01-14T06:00:01-06:00",
                    "title": "CRID 1064593 CR",
                    "source_type": "DOCUMENTCLOUD",
                    "preview_image_url": "https://assets.documentcloud.org/documents/4769386/pages/CRID-1064593-CR-p1-normal.gif",
                    "views_count": 2,
                    "downloads_count": 1,
                    "crid": "123456",
                    "show": false
                    "documents_count": 3,
                    "crid": "1064593"
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
