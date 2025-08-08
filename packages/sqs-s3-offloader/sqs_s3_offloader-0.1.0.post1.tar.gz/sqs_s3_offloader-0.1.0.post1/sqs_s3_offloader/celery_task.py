from celery import Task
import json
from .s3_utils import S3Uploader

class S3PayloadTask(Task):
    """
    Celery Task base class that transparently handles S3 pointer payload.
    If the first arg is an S3 pointer, download the data, delete the S3 object,
    and pass the original payload to the run() method.
    """
    def __call__(self, *args, **kwargs):
        if args and isinstance(args, tuple) and args[0].get('s3_pointer', False):
            bucket = args[0]["bucket"]
            key = args[0]["key"]
            s3 = S3Uploader(bucket)
            data = s3.download(bucket, key)
            s3.delete(bucket, key)  # clean up after download
            real_args = [json.loads(data)] + list(args[1:])
        else:
            real_args = args
        return self.run(*real_args, **kwargs)
