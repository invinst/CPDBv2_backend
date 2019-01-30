import botocore
from zipstream import ZipFile
from smart_open import smart_open


def write_file_to_zipfile(zf, s3_source, file_name):
    try:
        file_in = smart_open(s3_source, 'rb')
    except botocore.exceptions.ClientError as e:
        print(e)
    else:
        zf.write_iter(file_name, file_in)


def create_zip_stream(bucket, file_map):
    zf = ZipFile()
    for s3_key, file_path in file_map.items():
        write_file_to_zipfile(zf, f's3://{bucket}/{s3_key}', file_path)
    return zf


def stream_upload_to_s3(bucket, key, zip_stream):
    with smart_open(f's3://{bucket}/{key}', 'wb') as fout:
        for data in zip_stream:
            fout.write(data)


def lambda_handler(event, context):
    key = event['key']
    bucket = event['bucket']
    file_map = event.get('file_map', {})
    zip_stream = create_zip_stream(bucket, file_map)
    stream_upload_to_s3(bucket, key, zip_stream)

    return {
        'statusCode': 200,
    }
