# Lambda

Implementations for some AWS Lambda functions

## AWS Lambda functions

### 1. [upload_pdf](upload_pdf/lambda_function.py)

Upload a file (at an URL) to an S3 bucket. This function is used by [AttachmentFile.upload_to_s3](../cpdb/data/models/attachment_file.py#L86).

- Event input:
  - url (string): an URL to the uploading file
  - bucket (string): the destination S3 bucket for this uploading
  - key (string): an unique key for the uploading file. This is also the S3 file's key.

### 2. [create_officer_zip](create_officer_zip/lambda_function.py)

Collect files from our S3 and create a zip file of them. The created zip file is also uploaded to our S3, so that users can download it. This function is used by [Officer.invoke_create_zip](../cpdb/data/models/officer.py#L375)

- Event input:
  - file_map (dict): a s3_key -> file_path dictionary
    - s3_key (string): the S3 key points to the file being zipped
    - file_path (string): where the file is located in the created zip file, e.g. `"officerA/TTR1.pdf"`
  - bucket (string): the created zip file will be uploaded to this bucket
  - key (string): the created zip file will be uploaded with this key.
