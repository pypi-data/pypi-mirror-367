import unittest
from unittest.mock import MagicMock
import json
import base64
import uuid
from datetime import datetime

# Import your actual send_message and create_celery_payload functions
# Assume they are in your_package.extended_sqs_sender for this example
from sqs_s3_offloader.sqs_producer import send_message, create_celery_payload


class TestExtendedSqsSender(unittest.TestCase):
    def setUp(self):
        # Mock boto3 SQS client
        self.mock_sqs_client = MagicMock()

        # Fake queue URL
        self.queue_url = "https://sqs.mock-region.amazonaws.com/000000000000/mock-queue"

        # Simple test payload
        self.payload = {"foo": "bar", "data": [1, 2, 3]}

        # Sample task name
        self.task_name = "myapp.tasks.example_task"

        # Mock s3uploader with upload method
        class MockS3Uploader:
            def __init__(self):
                self.upload_called_with = None

            def upload(self, data):
                self.upload_called_with = data
                # Return a dummy S3 pointer
                return {
                    "bucket": "mock-bucket",
                    "key": "mock-key",
                }

        self.mock_s3uploader = MockS3Uploader()

    def test_send_message_with_s3uploader(self):
        # Call send_message providing s3uploader
        send_message(self.mock_sqs_client, self.queue_url, self.task_name, self.payload, self.mock_s3uploader)

        # Assert S3 uploader.upload was called once with serialized payload JSON bytes
        self.assertIsNotNone(self.mock_s3uploader.upload_called_with)

        # The argument to upload() must be bytes (JSON-encoded)
        self.assertIsInstance(self.mock_s3uploader.upload_called_with, bytes)

        # Assert SQS client's send_message was called once
        self.mock_sqs_client.send_message.assert_called_once()

        # Extract the actual MessageBody sent to SQS
        called_args, called_kwargs = self.mock_sqs_client.send_message.call_args
        body_sent = called_kwargs['MessageBody']

        # The body is a JSON-encoded Celery payload (dict)
        celery_payload = json.loads(body_sent)

        # 'args' inside Celery payload header should contain a pointer dict with s3_pointer=True
        # Decode the base64 body to check args inside
        body_b64 = celery_payload['body']
        decoded_bytes = base64.b64decode(body_b64.encode('utf-8'))
        decoded_list = json.loads(decoded_bytes.decode('utf-8'))

        args_list = decoded_list[0]  # args is first element
        self.assertEqual(len(args_list), 1)

        pointer = args_list[0]

        # Pointer is a dict and should have s3_pointer key (our code adds s3_pointer=True in send_message)
        self.assertIsInstance(pointer, dict)
        self.assertTrue('bucket' in pointer and pointer['bucket'] == 'mock-bucket')
        self.assertTrue('key' in pointer and pointer['key'] == 'mock-key')
        # s3_pointer key is added, so check it exists and is True
        self.assertIn('s3_pointer', pointer)
        self.assertTrue(pointer['s3_pointer'])

    def test_send_message_without_s3uploader(self):
        # Call send_message without s3uploader - payload should be sent as is (JSON string)
        send_message(self.mock_sqs_client, self.queue_url, self.task_name, self.payload, s3uploader=None)

        # S3 upload should not have been called; so no info here, just check SQS send_message call
        self.mock_sqs_client.send_message.assert_called_once()

        called_args, called_kwargs = self.mock_sqs_client.send_message.call_args
        body_sent = called_kwargs['MessageBody']

        # Since s3uploader is None, the body should be JSON dump of payload directly (str)
        # It should be equal to json.dumps(self.payload)
        self.assertEqual(body_sent, json.dumps(self.payload))

    def test_create_celery_payload_structure(self):
        # Just test create_celery_payload returns correct keys
        payload = create_celery_payload(self.task_name, args=[self.payload], kwargs={"foo": "bar"})
        self.assertIsInstance(payload, dict)

        # Must contain 'body', 'headers', 'properties' keys
        self.assertIn('body', payload)
        self.assertIn('headers', payload)
        self.assertIn('properties', payload)

        # The 'body' should be base64 encoded string, decoding it should give JSON list [args, kwargs, meta]
        decoded_body = base64.b64decode(payload['body']).decode('utf-8')
        lst = json.loads(decoded_body)

        # lst is [args, kwargs, meta]
        self.assertIsInstance(lst, list)
        self.assertEqual(lst[0], [self.payload])
        self.assertEqual(lst[1], {"foo": "bar"})
        self.assertIsInstance(lst[2], dict)


if __name__ == '__main__':
    unittest.main()
