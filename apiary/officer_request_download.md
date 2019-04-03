## Officer request download [/officers/{officer_id}/request-download/{?with-docs}]

### Get the url to the officer zip file[GET]

+ Parameters
    + officer_id (number) - number ID of the officer
    + with-docs (string, optional) - should the zip file contain docs or not
        + Default: `false`

+ Response 200 (application/text)

        "https://officer-content-staging.s3.amazonaws.com/zip_with_docs/Jerome_Finnigan_with_docs.zip"
