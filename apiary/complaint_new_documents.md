## CR new documents [/cr/list-by-new-document]

### List document which has new documents (in document-cloud) [GET]

+ Parameters
    + limit (number) - number of allegations which has new document

+ Response 200 (application/json)
        [
            {
                "crid": "111",
                "latest_document": {
                    "title": "CR document 1",
                    "url": "http://cr-document.com/1",
                    "preview_image_url": "http://preview.com/url"
                },
                "num_recent_documents": 2
            },
            {
                "crid": "112",
                "latest_document": {
                    "title": "CR document 3",
                    "url": "http://cr-document.com/3",
                    "preview_image_url": "http://preview.com/url3"
                },
                "num_recent_documents": 1
            },
        ]
