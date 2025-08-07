from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from types_aiobotocore_s3.type_defs import (
    CompletedPartTypeDef,
)

MP_THRESHOLD = 25000000
MP_CHUNK_SIZE = 25000000
MP_MAXIMUM_PARTS = 10000


class EmptyMountResponseError(Exception):
    pass


@dataclass
class BlobMeta:
    bucket: str
    key: str
    content_type: Any
    size: int
    version: Any
    update_time: datetime | None


class StorageClient(ABC):
    @abstractmethod
    async def head(self, bucket_name: str, key: str) -> BlobMeta:
        pass

    @abstractmethod
    async def get_blob_bytes(
        self,
        bucket_name: str,
        key: str,
        start: int | None = None,
        end: int | None = None,
    ) -> bytes:
        pass

    @abstractmethod
    def list_keys(
        self,
        bucket_name: str,
        prefix: str | None = None,
        delimiter: str = "/",
    ) -> AsyncGenerator[str, Any]:
        pass

    @abstractmethod
    async def put_blob(
        self,
        bucket_name: str,
        key: str,
        body: bytes = b"",
        content_type: str | None = None,
        acl: str = "bucket-owner-full-control",
    ) -> BlobMeta:
        pass

    @abstractmethod
    async def copy_blob(
        self,
        src_key: str,
        src_bucket_name: str,
        dest_key: str,
        dest_bucket_name: str,
    ) -> None:
        pass

    @abstractmethod
    async def copy_blob_multipart(
        self,
        src_key: str,
        src_bucket_name: str,
        dest_key: str,
        dest_bucket_name: str,
    ) -> None:
        pass

    @abstractmethod
    async def delete_blob(
        self,
        bucket_name: str,
        key: str,
    ) -> None:
        pass

    @abstractmethod
    async def generate_signed_download_url(
        self,
        bucket_name: str,
        key: str,
        content_disposition: str | None = None,
        content_type: str | None = None,
    ) -> str:
        pass

    @abstractmethod
    async def generate_signed_upload_url(
        self,
        bucket_name: str,
        key: str,
    ) -> str:
        pass

    @abstractmethod
    async def generate_signed_part_upload_url(
        self,
        bucket_name: str,
        bucket_key: str,
        upload_id: str,
        part_number: int,
    ) -> str:
        pass

    @abstractmethod
    async def multipart_initiate_upload(
        self,
        bucket_name: str,
        bucket_key: str,
        content_type: str,
        acl: str = "storageAdmin",
    ) -> str:
        pass

    @abstractmethod
    async def multipart_upload_part(
        self,
        bucket_name: str,
        bucket_key: str,
        upload_id: str,
        part_number: int,
        data: bytes,
    ) -> str:
        pass

    @abstractmethod
    async def multipart_complete_upload(
        self,
        bucket_name: str,
        bucket_key: str,
        upload_id: str,
        parts: list[CompletedPartTypeDef],
    ) -> str:
        pass
