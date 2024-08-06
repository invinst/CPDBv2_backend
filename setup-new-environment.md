# Setup new environment
This is a tutorial on how to setup a new environment. Let's call it `beta`.

## 1. Create new branch
- `master` and `develop` should be at the same point, or at least there is no commits that affects database.
- Check out a new branch called `beta` from `master`.

## 2. Create new secret files
##### 2.1. Ignore secret files
Add these two files into `.gitignore`
- `beta.env`
- `kubernetes/secrets-beta.yml`

##### 2.2. Kubernetes secrets
- All the secrets must be base64 encoded using `echo  'linuxhint.com' | base64`
- Clone `kubernetes/secrets-staging.yml` and name the created file `kubernetes/secrets-beta.yml`
- These secrets are the same for staging, beta and production then keep them as is.
    - `google-nl-api-credentials`
    - `tls-secret`
    - `cloudsql-postgres-credentials`
    - `documentcloud`
    - `airtable` (beta uses production secrets)
    - `mailgun`
    - `papertrail`
    - `twitterbot-storage-account`
    - `twitter-cpdpbot-app` (beta uses staging bot app)
    - `mailchimp` ??? (only used on production)
- Django secret: randomly generate a string and put it to `django secret-key`
- Azure Storage Account (used for `azure-storage-account` and `datapipeline-storage-account`)
    - Go to [https://portal.azure.com/](https://portal.azure.com/) and create a storage account for `beta`
    - Copy storage data from production storage account to beta storage account
        + Clone `fixture`, `csv`, `heatmap` blobs
        + Create the empty `static` container with blob access
    - Edit the CORS rule as follow

        | ALLOWED ORIGINS | ALLOWED METHODS | ALLOWED HEADERS                                         | EXPOSED HEADERS                                                               |
        |:----------------|:----------------|:--------------------------------------------------------|:------------------------------------------------------------------------------|
        | https://beta.cpdp.co | GET             | Accept, Accept-Language, Content-Language, Content-Type | Cache-Control, Content-Language, Content-Type, Expires, Last-Modified, Pragma |
        | https://betaapi.cpdp.co | GET             | Accept, Accept-Language, Content-Language, Content-Type | Cache-Control, Content-Language, Content-Type, Expires, Last-Modified, Pragma |
    - Put storage account name as `name` and api key as `key` into `azure-storage-account` and `datapipeline-storage-account`

##### 2.3. Environment variables
- Clone `staging.env` and rename the created file to beta.env
- `PGCLOUD_INSTANCE=twitterbot-180604:us-central1:cpdp-beta-database`
    - Ask Jeeves to grand you the access permission
    - Go to https://console.cloud.google.com/sql/instances?project=twitterbot-180604
    - Clone `cpdp-production` and rename it to `cpdp-beta-database`
- `DESKTOP_DOMAIN=beta.cpdp.co`
- `MOBILE_DOMAIN=mb.cpdp.co`
- `API_DOMAIN=betaapi.cpdp.co`
- Keep the rest unchanged

##### 2.4. Hide secrets
  - Run `git secret hide`

## 3. Beta config settings
- Create `cpdb/config/settings/beta.py` based on `cpdb/config/settings/staging.py`
- Enable email service by removing `EMAIL_BACKEND` and `BANDIT_EMAIL`
- `beta` uses the same AirTable table with `production` then remove `AIRTABLE_COPA_AGENCY_ID` and `AIRTABLE_CPD_AGENCY_ID`

## 4. Clone AWS environment`
- AWS S3
    - Create bucket with name S3_BUCKET_CRAWLER_LOG
- AWS Lambda
    - Update `lambda/deploy.sh` with new environment (beta)
    - Follow `docs/aws-lambda.md` to create beta's s3 buckets and lambda functions
    - Deploy new lambda functions using `docker-compose run web lambda/deploy.sh --beta`

## 5. Update scripts
- Add `beta` option to most of files in `bin` folder
- Edit `.circleci/config.yml` to add `beta` workflows (similar to `staging` workflows). Unlike `staging` we need `beta`
branch to trigger rebuilding index and search index.

## 6. Initialize new namespace/virtual-cluster
- Run `./bin/initialize_kubernetes_namespace.sh --beta`

## 7. Activate new domains
- Go to https://mycloud.rackspace.com
- Add A record for `betaapi.cpdp.co`, `mb.cpdp.co` and `beta.cpdp.co`, they should point to the same ip as `cpdp.co`

## 8. Deploy
- Push the new `beta` branch and let CircleCI do the rest

## 9. Post deploy
- Run `./bin/manage.sh --beta upload_pdf` to upload pdf files to s3
- Check if `betaapi.cpdp.co/admin/`, `beta.cpdp.co`, `mb.cpdp.co` are working properly
- Delete all existing attachment requests because of these:
    - We are using the same AirTable ID for `production` and `beta`. We don't want `beta` to edit/remove any `production`'s records.
    - We enable email notification feature and we don't want to sent duplicated emails to real users.

## 10. Github
- `beta` branch must be protected from now on.
