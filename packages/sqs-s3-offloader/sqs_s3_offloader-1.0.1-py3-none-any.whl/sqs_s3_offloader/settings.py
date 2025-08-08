try:
    from django.conf import settings
    S3_BUCKET = getattr(settings, 'SQS_LARGE_PAYLOADS_S3_BUCKET', None)
except ImportError:
    S3_BUCKET = None  # fallback if Django not used
