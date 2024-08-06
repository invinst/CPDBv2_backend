# AWS Lambda
We use S3 and Lambda from AWS. We store all xlsx files, pdf attachment files on S3 and built officer zip files on S3. We use Lambda to upload pdf files and create zip files on the fly.
- All credentials are available in the encoded env files

## Create AWS S3 buckets
- Create bucket with name S3_BUCKET_OFFICER_CONTENT
- Migrate CORS config to new s3 buckets
- Migrate Management -> Lifecycle rules to new s3 buckets

## Development
All Lambda source is at `lambda` directory. Each Lambda function is at a subdirectory, e.g. `lambda/create_officer_zip`.
A Lambda function package should at least contain these files:
- `.env` which contains `FUNCTION_NAME` variable
- `lambda_function.py` which defined `lambda_handler` function
- `requirements.txt` for installing packages via **pip**
- All other packages and modules which is used by the `lambda_handler` function.

**Note**: Dont use `package` to name your packages, because we will install all 3rd party packages into `package`

- Run tests with `docker-compose run web python -m lambda.test`

## Deploy lambda function
- Dev must create Lambda functions manually on AWS console
- To deploy/update Lambda functions, use `docker-compose run web lambda/deploy.sh`
