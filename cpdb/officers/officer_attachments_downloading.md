# Officer's documents downloading

Our system not only searchs for new officer documents everyday, but also keep old documented updated. Besides, we allow our users to download all officer's documents at once within a zip file.

This note explains how we impletemented those features

## I. Keep officer's attachments updated

We have a cronjob to search for new attachments and updated attachments, then upload them to our S3, see more in [cpdp/document_cloud/README.md](../document_cloud/README.md#L7)

## II. Support attachments downloading

### 1. Create zip file

- Whenever a user go to an officer page, e.g. https://cpdp.co/officer/17816/edward-may/, our frontend sends a request to [officers/views.create_zip_file](views.py#L119) to create an attachment zip file.
- It will invoke our [create_officer_zip AWS Lambda function](../../lambda/README.md#L13) to collects the officer's attachment files from S3 and build a zip file for it. The created zip is loaded to S3 and almost ready for downloading.
- The zip files will stay in our S3 for at most 1 day, to make sure users always download the lasted documents.

### 2. Trigger a download

- When the user hits download on the officer site. A request to [officers/views.request_download](views.py#L100) is made.
- Our backend creates a presigned URL which points to the zip file and returns the URL to frontend.
- Frontend will start a download with that presigned URL.
