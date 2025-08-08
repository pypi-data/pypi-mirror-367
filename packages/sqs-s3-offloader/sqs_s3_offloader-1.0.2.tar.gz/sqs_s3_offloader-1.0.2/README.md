# SQS S3 Offloader

[![PyPI version](https://badge.fury.io/py/sqs-s3-offloader.svg)](https://pypi.org/project/sqs-s3-offloader/)

`sqs-s3-offloader` is a utility library that allows you to bypass the AWS SQS message size limit (256 KB) by offloading large payloads to Amazon S3. It wraps your Celery task, automatically uploads large payloads to S3, sends a reference pointer via SQS, and downloads the actual data during task execution.

---

## ✨ Features

- ✅ Automatically detects and offloads large SQS payloads to S3
- ✅ Transparent integration with Celery tasks via a simple decorator
- ✅ Secure upload and deletion of temporary payloads from S3
- ✅ Works with boto3 and AWS credentials setup

---

## 🚀 Installation

```bash
pip install sqs-s3-offloader
```

---

## ⚙️ Usage

```python
from sqs_s3_offloader.celery_task import S3PayloadTask

@shared_task(base=S3PayloadTask)
def my_task(*args, **kwargs):
    # Your logic here
    print(args, kwargs)
```

### How It Works

- Before sending the task to SQS, if the payload size is too large, the decorator uploads the data to S3 and sends a pointer like:
  ```json
  {"s3_bucket": "your-bucket", "s3_key": "tmp/uuid4.json", "s3_pointer":  True}
  ```
- The decorator on the worker side checks if the argument contains the S3 pointer, fetches the actual payload from S3, deletes it, and executes the task with original data.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

## 👨‍💻 Author

Developed by [Aniket Dinesh Gavali](https://github.com/aniket-dg)