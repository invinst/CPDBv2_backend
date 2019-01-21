import urllib

import boto3

s3 = boto3.client('s3')


def lambda_handler(event, context):
    url = event['url']
    key = event['key']
    bucket = event['bucket']
    data = urllib.request.urlopen(url).read()
    s3.put_object(Body=data, Bucket=bucket, Key=key)
    return {
        'statusCode': 200,
        'body': ''
    }
