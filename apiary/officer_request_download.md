## Officer create zip file [/officers/{officer_id}/request-download/{?with-docs}]

### Create zip file from excel and pdf files then save it on S3[GET]

+ Parameters
    + officer_id (number) - number ID of the officer
    + offset (string, optional) - should the zip file contain docs or not
        + Default: `false`

+ Response 200 (application/text)

        "https://officer-content-staging.s3.amazonaws.com/zip_with_docs/Officer_1_with_docs.zip"
