import boto3


class AWS(object):
    def __init__(self):
        self._s3 = None
        self._lambda_client = None

    @property
    def s3(self):
        if not self._s3:
            self._s3 = boto3.client('s3')
        return self._s3

    @property
    def lambda_client(self):
        if not self._lambda_client:
            self._lambda_client = boto3.client('lambda')
        return self._lambda_client


aws = AWS()
