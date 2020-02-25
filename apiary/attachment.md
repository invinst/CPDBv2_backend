## Attachments [/attachments/{?match,crid,offset,limit}/]

+ Parameters
    + match (string, optional) - String to match against title and CRID
    + crid (string, optional) - CRID to filter attachments
    + offset (number, optional) - offset from which to get additional results
        + Default: `0`
    + limit (number, optional) - limit of how many results to return
        + Default: `20`

### Get attachments by an unauthenticated user [GET]

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
                    "crid": "123456",
                    "show": false
                    "documents_count": 3,
                    "crid": "1064593"
                }
            ]
        }

### Get attachments by an authenticated user [GET]

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

### Update an attachment [PATCH]

+ Parameters
    + pk (number) - number ID of Attachment

+ Request

        {
            "show": true,
            "title": "New title",
            "text_content": "New text content"
        }

+ Response 200 (application/json)

        {
            "id": 1,
            "show": true,
            "crid": "456",
            "title": "New title",
            "text_content": "New text content",
            "url": "http://foo.com",
            "preview_image_url": "https://assets.documentcloud.org/CRID-456-CR-p1-normal.gif",
            "original_url": "https://www.documentcloud.org/documents/1-CRID-123456-CR.html",
            "created_at": "2017-08-04T09:30:00-05:00",
            "updated_at": "2017-08-05T07:00:01-05:00",
            "crawler_name": "Document Cloud",
            "linked_documents": [],
            "pages": 10,
            "last_updated_by": "Test admin user",
            "views_count": 100,
            "downloads_count": 99,
            "notifications_count": 200,
            "show": true,
        }

### Retrieve an attachment by an authenticated user [GET]

+ Parameters
    + pk (number) - number ID of Attachment


+ Response 200 (application/json)

        {
            "id": "123",
            "crid": "456",
            "title": "CR document",
            "text_content": "CHICAGO POLICE DEPARTMENT RD I HT334604",
            "url": "http://foo.com",
            "preview_image_url": "https://assets.documentcloud.org/CRID-456-CR-p1-normal.gif",
            "original_url": "https://www.documentcloud.org/documents/1-CRID-123456-CR.html",
            "created_at": "2017-08-04T09:30:00-05:00",
            "updated_at": "2017-08-05T07:00:01-05:00",
            "crawler_name": "Document Cloud",
            "linked_documents": [
                {
                    "id": 124,
                    "preview_image_url": "https://assets.documentcloud.org/124/CRID-456-CR-p1-normal.gif",
                },
                {
                    "id": 125,
                    "preview_image_url": "https://assets.documentcloud.org/125/CRID-456-CR-p1-normal.gif",
                }
            ],
            "pages": 10,
            "last_updated_by": "test user",
            "views_count": "100",
            "downloads_count": "99",
            "notifications_count": "200"
        }

### Retrieve an attachment by an unauthenticated user [GET]

+ Parameters
    + pk (number) - number ID of Attachment


+ Response 200 (application/json)

        {
            "id": "123",
            "crid": "456",
            "title": "CR document",
            "text_content": "CHICAGO POLICE DEPARTMENT RD I HT334604",
            "url": "http://foo.com",
            "preview_image_url": "https://assets.documentcloud.org/CRID-456-CR-p1-normal.gif",
            "original_url": "https://www.documentcloud.org/documents/1-CRID-123456-CR.html",
            "created_at": "2017-08-04T09:30:00-05:00",
            "updated_at": "2017-08-05T07:00:01-05:00",
            "crawler_name": "Document Cloud",
            "linked_documents": [
                {
                    "id": "124",
                    "preview_image_url": "https://assets.documentcloud.org/124/CRID-456-CR-p1-normal.gif",
                },
                {
                    "id": "125",
                    "preview_image_url": "https://assets.documentcloud.org/125/CRID-456-CR-p1-normal.gif",
                }
            ],
            "pages": "10",
            "last_updated_by": "test user"
        }

## Retrieve suggestion tags [GET v2/attachments/tags]

+ Response 200 (application/json)

        ['tag1', 'tag2', 'tag3']
