import asyncio
import math
from collections.abc import AsyncGenerator, Coroutine
from datetime import datetime
from typing import Any

import botocore.exceptions
from latch_aws.aws import max_presigned_url_age
from latch_aws.client_pool import s3_pool
from types_aiobotocore_s3.type_defs import (
    CompletedPartTypeDef,
)

from ..utils import (
    MP_CHUNK_SIZE,
    MP_MAXIMUM_PARTS,
    BlobMeta,
    EmptyMountResponseError,
    StorageClient,
)


class S3StorageClient(StorageClient):
    async def head(self, bucket_name: str, key: str) -> BlobMeta:
        blob = None
        async with s3_pool.s3_client_for_bucket(bucket_name) as s3:
            try:
                obj = await s3.head_object(Bucket=bucket_name, Key=key)
                if key.endswith("/"):
                    obj["ContentType"] = "dir"
                    obj["ContentLength"] = 0
            except botocore.exceptions.ClientError as e:
                res = e.response
                if res.get("Error", {}).get("Code") != "404":
                    raise e

                try:
                    key = key.rstrip("/") + "/"

                    res = await s3.list_objects_v2(
                        Bucket=bucket_name,
                        Prefix=key,
                        MaxKeys=1,
                    )

                    if "Contents" not in res:
                        raise EmptyMountResponseError()

                    obj = {
                        "ContentType": "dir",
                        "ContentLength": 0,
                        "LastModified": None,
                        "VersionId": None,
                    }
                except botocore.exceptions.ClientError as e:
                    raise EmptyMountResponseError from e

            blob = BlobMeta(
                bucket=bucket_name,
                key=key,
                content_type=obj["ContentType"],
                size=obj["ContentLength"],
                version=obj.get("VersionId"),
                update_time=obj.get("LastModified"),
            )
        return blob

    async def get_blob_bytes(
        self,
        bucket_name: str,
        key: str,
        start: int | None = None,
        end: int | None = None,
    ) -> bytes:
        async with s3_pool.s3_client_for_bucket(bucket_name) as s3:
            meta = await self.head(bucket_name=bucket_name, key=key)

            start = start if start is not None else 0
            end = end if end is not None else meta.size - 1

            response = await s3.get_object(
                Bucket=bucket_name,
                Key=key,
                Range=f"bytes={start}-{end}",
            )

            return await response["Body"].read()

    async def list_keys(
        self,
        bucket_name: str,
        prefix: str | None = None,
        delimiter: str = "/",
    ) -> AsyncGenerator[str, Any]:
        async with s3_pool.s3_client_for_bucket(bucket_name) as s3:
            paginator = s3.get_paginator("list_objects_v2")

            params = {
                "Bucket": bucket_name,
                "Delimiter": delimiter,
            }
            if prefix is not None:
                params["Prefix"] = prefix

            async for page in paginator.paginate(**params):
                for x in [y["Key"] for y in page.get("Contents", [])] + [
                    y["Prefix"] for y in page.get("CommonPrefixes", [])
                ]:
                    if prefix is None or x.rstrip("/") != prefix.rstrip("/"):
                        yield x

    async def put_blob(
        self,
        bucket_name: str,
        key: str,
        body: bytes = b"",
        content_type: str = "text/plain",
        acl: str = "bucket-owner-full-control",
    ) -> BlobMeta:
        async with s3_pool.s3_client_for_bucket(bucket_name) as s3:
            res = await s3.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=body,
                ContentType=content_type,
                ACL=acl,
            )

            return BlobMeta(
                bucket=bucket_name,
                key=key,
                content_type=content_type,
                size=len(body),
                version=res["VersionId"],
                update_time=datetime.now(),
            )

    async def copy_blob(
        self,
        src_key: str,
        src_bucket: str,
        dest_key: str,
        dest_bucket: str,
    ) -> None:
        blob = await self.head(src_bucket, src_key)
        if blob is None:
            return
        async with s3_pool.s3_client_for_bucket(dest_bucket) as s3:
            await s3.copy_object(
                CopySource={
                    "Bucket": src_bucket,
                    "Key": src_key,
                },
                Bucket=dest_bucket,
                Key=dest_key,
                ContentType=blob.content_type,
                ACL="bucket-owner-full-control",
            )

    async def copy_blob_multipart(
        self,
        src_key: str,
        src_bucket: str,
        dest_key: str,
        dest_bucket: str,
    ) -> None:
        blob = await self.head(src_bucket, src_key)
        if blob is None:
            raise EmptyMountResponseError()

        async with s3_pool.s3_client_for_bucket(dest_bucket) as s3:
            upload_id = await self.multipart_initiate_upload(
                dest_bucket,
                dest_key,
                blob.content_type,
                "bucket-owner-full-control",
            )

            chunk_size = MP_CHUNK_SIZE
            parts = math.ceil(blob.size / MP_CHUNK_SIZE)

            if parts > MP_MAXIMUM_PARTS:
                parts = MP_MAXIMUM_PARTS
                chunk_size = math.ceil(blob.size / parts)

            async def run_upload_chunk(
                byte_range: str, index: int
            ) -> CompletedPartTypeDef:
                res = await s3.upload_part_copy(
                    CopySource={
                        "Bucket": src_bucket,
                        "Key": src_key,
                    },
                    Bucket=dest_bucket,
                    Key=dest_key,
                    PartNumber=index + 1,
                    UploadId=upload_id,
                    CopySourceRange=byte_range,
                )
                if "CopyPartResult" not in res or "ETag" not in res["CopyPartResult"]:
                    raise ValueError("Etag not in response")

                return {
                    "ETag": res["CopyPartResult"]["ETag"],
                    "PartNumber": index + 1,
                }

            upload_chunk_requests: list[Coroutine[Any, Any, CompletedPartTypeDef]] = []

            upload_chunk_responses: list[CompletedPartTypeDef] = []
            for i in range(parts):
                byte_start = i * chunk_size
                byte_end = (i + 1) * chunk_size - 1
                byte_end = min(byte_end, blob.size - 1)
                byte_range = f"bytes={byte_start}-{byte_end}"

                upload_chunk_requests.append(run_upload_chunk(byte_range, i))

                if len(upload_chunk_requests) >= 50:
                    upload_chunk_responses.extend(
                        await asyncio.gather(*upload_chunk_requests)
                    )
                    upload_chunk_requests = []

            upload_chunk_responses.extend(await asyncio.gather(*upload_chunk_requests))

            await self.multipart_complete_upload(
                dest_bucket, dest_key, upload_id, upload_chunk_responses
            )

    async def delete_blob(
        self,
        bucket_name: str,
        key: str,
    ) -> None:
        try:
            async with s3_pool.s3_client_for_bucket(bucket_name) as s3:
                await s3.delete_object(
                    Bucket=bucket_name,
                    Key=key,
                )
        except botocore.exceptions.ClientError as e:
            res = e.response
            if res.get("Error", {}).get("Code") != "404":
                raise e

            return

    async def generate_signed_download_url(
        self,
        bucket_name: str,
        key: str,
        content_disposition: str | None = None,
        content_type: str | None = None,
    ) -> str:
        async with s3_pool.s3_client_for_bucket(bucket_name) as s3:
            return await s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": bucket_name,
                    "Key": key,
                    # todo(maximsmol): add extra validation
                    # "ExpectedBucketOwner": "",
                    # "IfMatch": "",
                    # "VersionId": ""
                }
                | (
                    {"ResponseContentDisposition": content_disposition}
                    if content_disposition is not None
                    else {}
                )
                | (
                    {"ResponseContentType": content_type}
                    if content_type is not None
                    else {}
                ),
                ExpiresIn=max_presigned_url_age,
            )

    async def generate_signed_upload_url(
        self,
        bucket_name: str,
        key: str,
    ) -> str:
        async with s3_pool.s3_client_for_bucket(bucket_name) as s3:
            return await s3.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": bucket_name,
                    "Key": key,
                },
                ExpiresIn=max_presigned_url_age,
            )

    async def generate_signed_part_upload_url(
        self,
        bucket_name: str,
        bucket_key: str,
        upload_id: str,
        part_number: int,
    ) -> str:
        async with s3_pool.s3_client_for_bucket(bucket_name) as s3:
            return await s3.generate_presigned_url(
                "upload_part",
                Params={
                    "Bucket": bucket_name,
                    "Key": bucket_key,
                    "UploadId": upload_id,
                    "PartNumber": part_number,
                    # todo(maximsmol): add extra validation
                    # "ExpectedBucketOwner": "",
                },
                ExpiresIn=max_presigned_url_age,
            )

    async def multipart_initiate_upload(
        self,
        bucket_name: str,
        bucket_key: str,
        content_type: str,
        acl: str = "bucket-owner-full-control",
    ) -> str:
        async with s3_pool.s3_client_for_bucket(bucket_name) as s3:
            multipart_res = await s3.create_multipart_upload(
                Bucket=bucket_name,
                Key=bucket_key,
                ACL=acl,
                ContentType=content_type,
                # todo(maximsmol): add extra validation
                # "ExpectedBucketOwner": "",
            )
            return multipart_res["UploadId"]

    async def multipart_upload_part(
        self,
        bucket_name: str,
        bucket_key: str,
        upload_id: str,
        part_number: int,
        data: bytes,
    ) -> str:
        async with s3_pool.s3_client_for_bucket(bucket_name) as s3:
            ret = await s3.upload_part(
                Bucket=bucket_name,
                Key=bucket_key,
                UploadId=upload_id,
                PartNumber=part_number,
                Body=data,
            )
            return ret["ETag"]

    async def multipart_complete_upload(
        self,
        bucket_name: str,
        bucket_key: str,
        upload_id: str,
        parts: list[CompletedPartTypeDef],
    ) -> str:
        try:
            async with s3_pool.s3_client_for_bucket(bucket_name) as s3:
                res = await s3.complete_multipart_upload(
                    Bucket=bucket_name,
                    Key=bucket_key,
                    UploadId=upload_id,
                    MultipartUpload={"Parts": parts},
                    # todo(maximsmol): add extra validation
                    # "ExpectedBucketOwner": "",
                )

                return res["VersionId"]
        except botocore.exceptions.ClientError as e:
            err_res = e.response
            if "Error" not in err_res:
                raise e

            if "Code" not in err_res["Error"]:
                raise e

            if err_res["Error"]["Code"] != "EntityTooSmall":
                raise e

            raise ValueError("Upload size is less than minimum allowed") from e
