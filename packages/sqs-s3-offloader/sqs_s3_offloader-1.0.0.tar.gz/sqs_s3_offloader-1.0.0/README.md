# sqs_s3_offloader

A Django/Celery package to transparently handle large AWS SQS payloads by offloading messages larger than 256KB to S3.

## Features

- Automatically uploads large payloads (>256KB) to S3.
- Sends lightweight pointer messages to AWS SQS.
- Celery tasks subclassing `S3PayloadTask` auto-fetch, delete, and process large payloads transparently.
- Works with normal small payloads without overhead.
- Simple integration for Django or pure Python projects.

## Installation

