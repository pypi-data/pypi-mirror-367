import unittest
from unittest.mock import MagicMock, patch
import json

from sqs_s3_offloader.celery_task import S3PayloadTask


class DummyTask(S3PayloadTask):
    def run(self, *args, **kwargs):
        self.data = None
        self.extra_args = None
        if args:
            self.data = args[0]
            self.extra_args = args[1:]
        self.extra_kwargs = kwargs
        return "done"


class TestS3PayloadTask(unittest.TestCase):

    @patch('sqs_s3_offloader.celery_task.S3Uploader')  # Mock S3Uploader where imported
    def test_s3_pointer_payload(self, MockS3Uploader):
        mock_s3_instance = MockS3Uploader.return_value
        sample_data = {"foo": "bar"}
        encoded_data = json.dumps(sample_data).encode()
        mock_s3_instance.download.return_value = encoded_data
        mock_s3_instance.delete.return_value = None

        task = DummyTask()
        s3_pointer = {
            's3_pointer': True,
            'bucket': 'test-bucket',
            'key': 'test-key'
        }
        # Call __call__ with pointer as first positional arg + extra args/kwargs
        result = task.__call__(s3_pointer, "extra_arg1", foo="bar")

        mock_s3_instance.download.assert_called_once_with('test-bucket', 'test-key')
        mock_s3_instance.delete.assert_called_once_with('test-bucket', 'test-key')
        self.assertEqual(task.data, sample_data)
        self.assertEqual(task.extra_args, ("extra_arg1",))
        self.assertEqual(task.extra_kwargs, {"foo": "bar"})
        self.assertEqual(result, "done")

    def test_normal_payload(self):
        task = DummyTask()
        payload = {"normal": "payload"}
        result = task.__call__(payload, "extra_arg1", foo="bar")
        self.assertEqual(task.data, payload)
        self.assertEqual(task.extra_args, ("extra_arg1",))
        self.assertEqual(task.extra_kwargs, {"foo": "bar"})
        self.assertEqual(result, "done")

    def test_no_args(self):
        task = DummyTask()
        result = task.__call__()
        self.assertEqual(result, "done")


if __name__ == '__main__':
    unittest.main()
