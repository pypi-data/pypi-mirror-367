import json
import base64
import uuid
from datetime import datetime


def create_celery_payload(task_name, args=None, kwargs=None, receipt_handle=None):
    """
    Builds a Celery-compatible SQS message payload with proper encoding and metadata.
    """
    args = args or []
    kwargs = kwargs or {}

    if receipt_handle:
        kwargs['receipt_handle'] = receipt_handle

    # Encode args and kwargs as a base64 encoded JSON string
    body = json.dumps(
        [args, kwargs, {"callbacks": None, "errbacks": None, "chain": None, "chord": None}]
    )
    body_b64 = base64.b64encode(body.encode('utf-8')).decode('utf-8')

    task_id = str(uuid.uuid4())
    reply_to = str(uuid.uuid4())
    delivery_tag = str(uuid.uuid4())

    payload = {
        'body': body_b64,
        'content-encoding': 'utf-8',
        'content-type': 'application/json',
        'headers': {
            'lang': 'py',
            'task': task_name,
            'id': task_id,
            'shadow': None,
            'eta': None,
            'expires': None,
            'group': None,
            'group_index': None,
            'retries': 0,
            'timelimit': [None, None],
            'root_id': task_id,
            'parent_id': None,
            'argsrepr': repr(args),
            'kwargsrepr': repr(kwargs),
            'origin': 'manual_payload_creator',
            'ignore_result': False,
            'replaced_task_nesting': 0,
            'stamped_headers': None,
            'stamps': {},
            'sentry-task-enqueued-time': datetime.utcnow().timestamp(),
        },
        'properties': {
            'correlation_id': task_id,
            'reply_to': reply_to,
            'delivery_mode': 2,
            'delivery_info': {'exchange': '', 'routing_key': 'default'},
            'priority': 0,
            'body_encoding': 'base64',
            'delivery_tag': delivery_tag,
        },
    }
    return payload


def send_message(sqs_client, queue_url, task_name, payload, s3uploader=None):
    """
    Sends a Celery task payload to SQS.
    If payload is larger than 256KB serialized, upload to S3 and send pointer to SQS.

    :param sqs_client: boto3 SQS client
    :param queue_url: SQS Queue URL
    :param task_name: Celery task name as string
    :param args: List of positional args for Celery task
    :param kwargs: Dict of keyword args for Celery task
    :param s3uploader: instance of S3Uploader for large payload offload

    """
    # Serialize payload to JSON bytes
    serialized = json.dumps(payload).encode('utf-8')


    # If large and s3uploader provided, offload to S3
    if s3uploader:# and len(serialized) > 256 * 1024:
        pointer = s3uploader.upload(serialized)
        pointer["s3_pointer"] = True
        celery_payload = create_celery_payload(task_name, [pointer], {}, None)
        sqs_client.send_message(QueueUrl=queue_url, MessageBody=json.dumps(celery_payload))
    else:
        # Send full payload JSON as SQS message body
        sqs_client.send_message(QueueUrl=queue_url, MessageBody=serialized.decode('utf-8'))
