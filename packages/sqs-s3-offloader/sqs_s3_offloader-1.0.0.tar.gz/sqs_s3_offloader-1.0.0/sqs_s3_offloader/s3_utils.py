import boto3
from uuid import uuid4

class S3Uploader:
    def __init__(self, bucket, s3_client=None):
        self.bucket = bucket
        self.client = s3_client or boto3.client('s3')

    def upload(self, data: bytes) -> dict:
        key = f"sqs-large-payloads/{uuid4()}"
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data)
        return {"bucket": self.bucket, "key": key}

    def download(self, bucket: str, key: str) -> bytes:
        obj = self.client.get_object(Bucket=bucket, Key=key)
        return obj['Body'].read()

    def delete(self, bucket: str, key: str):
        self.client.delete_object(Bucket=bucket, Key=key)
