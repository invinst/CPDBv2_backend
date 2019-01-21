import boto3
import botocore
from zipstream import ZipFile
from smart_open import smart_open

s3 = boto3.client('s3')


def write_file_to_zipfile(zf, s3_source, file_name):
    try:
        file_in = smart_open(s3_source, 'rb')
    except botocore.exceptions.ClientError as e:
        print(e)
    else:
        zf.write_iter(file_name, file_in)


def create_zip_stream(
        officer_id,
        allegation_attachments_dict,
        investigator_attachments_dict,
        bucket,
        xlsx_dir,
        pdf_dir,
):
    zf = ZipFile()

    for xlsx_name in ['accused', 'investigator', 'use_of_force']:
        write_file_to_zipfile(zf, f's3://{bucket}/{xlsx_dir}/{officer_id}/{xlsx_name}.xlsx', f'{xlsx_name}.xlsx')

    for external_id, file_name in allegation_attachments_dict.items():
        write_file_to_zipfile(zf, f's3://{bucket}/{pdf_dir}/{external_id}', f'documents/{file_name}')

    for external_id, file_name in investigator_attachments_dict.items():
        write_file_to_zipfile(zf, f's3://{bucket}/{pdf_dir}/{external_id}', f'investigators/{file_name}')
    return zf


def stream_upload_to_s3(bucket, key, zip_stream):
    with smart_open(f's3://{bucket}/{key}', 'wb') as fout:
        for data in zip_stream:
            fout.write(data)


def lambda_handler(event, context):
    officer_id = event['officer_id']
    key = event['key']
    bucket = event['bucket']
    xlsx_dir = event['xlsx_dir']
    pdf_dir = event['pdf_dir']
    allegation_attachments_dict = event.get('allegation_attachments_dict', {})
    investigator_attachments_dict = event.get('investigator_attachments_dict', {})
    zip_stream = create_zip_stream(
        officer_id,
        allegation_attachments_dict,
        investigator_attachments_dict,
        bucket,
        xlsx_dir,
        pdf_dir,
    )
    stream_upload_to_s3(bucket, key, zip_stream)

    return {
        'statusCode': 200,
        'body': ''
    }
