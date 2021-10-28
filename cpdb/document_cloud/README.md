# document_cloud

This package provides commands to work with www.documentcloud.org.

## Commands

We have two commands which are run schedulefly using cron jobs.

### 1. [update_documents](management/commands/update_documents.py)

This command searches for attachments from DocumentCloud, then uploads it to our S3 and does some more NLP tasks on fetched texts. The steps are:

1. [Searching for attachments](importers.py#L238) from DocumentCloud
2. [Updating our DB](importers.py#L240) with [new_attachments](importers.py#L212) and [updated_attachments](importers.py#L202)
3. [Upload them to S3](importers.py#L242) by using our AWS Lambda function, see more in [AttachmentFile.upload_to_s3](../data/models/attachment_file.py#L85) and [the lambda package](../../lambda/README.md)
4. [Preprocess texts](importers.py#L244)
5. [Extract copa summary](importers.py#L246)

### 2. [update_titles_to_documentcloud](management/commands/update_titles_to_documentcloud.py)

This command updates our new file titles to DocumentCloud
