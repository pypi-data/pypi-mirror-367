from setuptools import setup, find_packages

setup(
    name="sqs-s3-offloader",
    version="0.1.0.post1",
    author="Aniket Gavali",
    author_email="aniket.dg25@gmail.com",
    description="A utility to offload large messages to S3 and use SQS seamlessly",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/aniket-dg/sqs-s3-offloader",
    license="MIT",
    include_package_data=True,
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "boto3>=1.28.0",
        "celery>=5.3.0"
    ],
    extras_require={
        "dev": ["pytest", "moto", "coverage"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
