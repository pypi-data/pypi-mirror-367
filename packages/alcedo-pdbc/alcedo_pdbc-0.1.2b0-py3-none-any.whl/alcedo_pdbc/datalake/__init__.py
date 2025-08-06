# -*- encoding：utf-8 -*-
"""
@File :__init__.py
@Time :2025-7-16  14:18
@Author：AI Lab Morgan
"""
from .minio import Minio,S3
from .gcs import GCS
from .azureblob import AzureBlob

__all__ = ['Minio',
           'S3',
           'GCS',
           'AzureBlob'
           ]
