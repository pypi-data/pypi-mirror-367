import unittest
from moto import mock_aws
import boto3
from sqs_s3_offloader.s3_utils import S3Uploader

@mock_aws
class TestS3Uploader(unittest.TestCase):

    def setUp(self):
        self.bucket = 'test-bucket'
        self.s3_client = boto3.client('s3', region_name='us-east-1')
        self.s3_client.create_bucket(Bucket=self.bucket)  # Create bucket in mock

        self.uploader = S3Uploader(self.bucket, s3_client=self.s3_client)


    def test_upload_and_download(self):
        data = b"Test data for upload"
        pointer = self.uploader.upload(data)
        self.assertEqual(pointer['bucket'], self.bucket)
        self.assertIn('key', pointer)

        downloaded = self.uploader.download(pointer['bucket'], pointer['key'])
        self.assertEqual(downloaded, data)

    def test_delete_object(self):
        data = b"To be deleted"
        pointer = self.uploader.upload(data)
        self.uploader.delete(pointer['bucket'], pointer['key'])

        # Check that the object is deleted
        with self.assertRaises(self.s3_client.exceptions.NoSuchKey):
            self.uploader.download(pointer['bucket'], pointer['key'])


if __name__ == '__main__':
    unittest.main()
