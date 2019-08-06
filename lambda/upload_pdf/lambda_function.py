from urllib.request import urlopen, Request

import boto3


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    url = event['url']
    key = event['key']
    bucket = event['bucket']
    req = Request(url, data=None, headers={'User-Agent': ''})
    data = urlopen(req).read()

    s3.put_object(Body=data, Bucket=bucket, Key=key)
    return {
        'statusCode': 200,
    }
