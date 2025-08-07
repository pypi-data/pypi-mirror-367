from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Literal, TypedDict
from urllib.parse import quote, urljoin, urlparse
from xml.etree import ElementTree as ET

import aiohttp
import xmltodict
from google.api_core.exceptions import (
    BadRequest,
    Forbidden,
    NotFound,
    ServerError,
    TooManyRequests,
    Unauthorized,
)
from google.auth import default as google_default_auth
from google.auth.transport import requests as google_transport_requests
from google.cloud import storage
from latch_o11y.o11y import dict_to_attrs
from opentelemetry.trace import SpanKind, get_tracer

max_presigned_url_age = timedelta(days=7) // timedelta(seconds=1)

tracer = get_tracer(__name__)


class Bucket(TypedDict):
    id: str
    name: str
    creation_time: datetime
    update_time: datetime
    project_number: str


class Object(TypedDict):
    id: str
    name: str
    bucket: str
    size: int
    media_link: str | None
    generation: str | None
    content_type: str | None
    creation_time: datetime | None
    update_time: datetime | None


class CompletedPartTypeDef(TypedDict):
    ETag: str
    ChecksumCRC32: str
    ChecksumCRC32C: str
    ChecksumSHA1: str
    ChecksumSHA256: str
    PartNumber: int


class AsyncGCPStorageClient:
    credentials, _ = google_default_auth(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    def __init__(self, session: aiohttp.ClientSession):
        self.api_url = "https://storage.googleapis.com/storage/v1/"
        self.upload_api_url = "https://storage.googleapis.com/upload/storage/v1/"
        self.google_client = storage.Client()
        self.session = session

    def __aexit__(self, exc_type, exc_val, exc_tb):
        return self.session.__aexit__(exc_type, exc_val, exc_tb)

    @staticmethod
    def get_auth_token():
        credentials = AsyncGCPStorageClient.credentials

        if credentials.token is None or credentials.expired:
            credentials.refresh(google_transport_requests.Request())
        return credentials.token

    async def _make_api_request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        url: str,
        operation_name: str,
        *,
        data: Any | None = None,
        headers: dict | None = None,
        params: dict | None = None,
        return_bytes=False,
        return_json=False,
        return_response=False,
    ) -> Any:
        endpoint_parts = urlparse(url)

        port = endpoint_parts.port
        if port is None:
            if endpoint_parts.scheme == "http":
                port = 80
            elif endpoint_parts.scheme == "https":
                port = 443

        with tracer.start_as_current_span(
            f"gcp-api.{operation_name}",
            kind=SpanKind.CLIENT,
            attributes={
                "service.name": f"gcp.{operation_name}",
                "http.scheme": endpoint_parts.scheme,
                "http.host": endpoint_parts.netloc,
                "http.endpoint": endpoint_parts.path,
                "net.peer.name": str(endpoint_parts.hostname),
                "rpc.method": operation_name,
                "rpc.system": "gcp-api",
                "span.type": "http",
                "resource.name": operation_name,
            }
            | (
                {
                    "net.peer.port": port,
                }
                if port is not None
                else {}
            )
            | dict_to_attrs(params if params is not None else {}, "rpc.gcp-api.params"),
        ):

            if headers is None:
                headers = {}

            headers["Authorization"] = (
                f"Bearer {AsyncGCPStorageClient.get_auth_token()}"
            )

            async with self.session.request(
                method,
                url,
                headers=headers,
                params=params,
                data=data,
            ) as resp:
                if resp.status >= 400:
                    err = await resp.text()
                    if resp.status == 400:
                        raise BadRequest(message=err, response=resp)
                    if resp.status == 401:
                        raise Unauthorized(message=err, response=resp)
                    if resp.status == 403:
                        raise Forbidden(message=err, response=resp)
                    if resp.status == 404:
                        raise NotFound(message=err, response=resp)
                    if resp.status == 429:
                        raise TooManyRequests(message=err, response=resp)
                    raise ServerError(message=err, response=resp)
                if resp.status == 204:
                    return
                if return_bytes:
                    return await resp.content.read()
                if return_json:
                    return await resp.json()
                if return_response:
                    return resp
                return await resp.text()

    async def get_bucket(self, bucket_name: str):
        with tracer.start_as_current_span("get_bucket") as s:
            s.set_attributes({"bucket_name": bucket_name})
            try:
                res = await self._make_api_request(
                    "GET",
                    urljoin(
                        self.api_url,
                        f"b/{bucket_name}",
                    ),
                    "GetBucket",
                    return_json=True,
                )
            except NotFound:
                return None

            return Bucket(
                name=res["name"],
                id=res["id"],
                creation_time=res["timeCreated"],
                update_time=res["updated"],
                project_number=res["projectNumber"],
            )

    async def get_blob_meta(self, bucket_name: str, key: str):
        try:
            res = await self._make_api_request(
                "GET",
                urljoin(self.api_url, f"b/{bucket_name}/o/{quote(key, safe='')}"),
                "GetBlobMeta",
                return_json=True,
            )
        except NotFound:
            return None

        return Object(
            name=res["name"],
            id=res["id"],
            bucket=res["bucket"],
            media_link=res.get("mediaLink"),
            generation=res.get("generation"),
            content_type=res.get("contentType"),
            size=int(res["size"]),
            creation_time=datetime.fromisoformat(res["timeCreated"]),
            update_time=datetime.fromisoformat(res["updated"]),
        )

    def list_blobs(
        self,
        bucket_name: str,
        *,
        prefix: str | None = None,
        delimiter: str = "/",
        match_glob: str | None = None,
        page_token: str | None = None,
        include_trailing_delimeter: bool | None = None,
        include_folders_as_prefixes: bool | None = None,
        max_items: int | None = None,
    ):
        if match_glob is not None and delimiter != "/":
            raise ValueError("match_glob is only supported with delimeter='/'")

        if include_folders_as_prefixes and delimiter != "/":
            raise ValueError(
                "include_folders_as_prefixes is only supported with delimeter='/'"
            )

        params = {
            "bucket": bucket_name,
            "prefix": prefix,
            "delimiter": delimiter,
            "matchGlob": match_glob,
            "maxResults": 1000,
            "pageToken": page_token,
            "includeTrailingDelimeter": include_trailing_delimeter,
            "includeFoldersAsPrefixes": include_folders_as_prefixes,
        }

        params = {k: str(v) for k, v in params.items() if v is not None}

        return AsyncGCPListBlobsIterator(
            url=urljoin(self.api_url, f"b/{bucket_name}/o"),
            headers={},
            params=params,
            storage_client=self,
            max_items=max_items,
        )

    async def get_blob_bytes(
        self,
        bucket_name: str,
        key: str,
        *,
        start: int | None = None,
        end: int | None = None,
    ):
        with tracer.start_as_current_span("get_blob_bytes") as s:
            headers = {}
            if start is None:
                start = 0

            if end is not None:
                headers["Range"] = f"bytes={start}-{end}"

            s.set_attributes(
                {
                    "bucket_name": bucket_name,
                    "key": key,
                    "range": headers.get("Range", ""),
                }
            )

            return bytes(
                await self._make_api_request(
                    "GET",
                    urljoin(self.api_url, f"b/{bucket_name}/o/{quote(key, safe='')}"),
                    "GetBlobBytes",
                    params={"alt": "media"},
                    headers=headers,
                    return_bytes=True,
                )
            )

    async def put_blob(
        self,
        bucket_name: str,
        key: str,
        data: bytes,
        *,
        content_type: str | None = None,
    ):
        if content_type is None:
            content_type = "text/plain"

        resp = await self._make_api_request(
            "POST",
            urljoin(self.upload_api_url, f"b/{bucket_name}/o"),
            "PutBlob",
            params={"name": key, "uploadType": "media"},
            headers={"Content-Type": content_type},
            data=data,
            return_json=True,
        )

        return Object(
            id=resp["id"],
            name=resp["name"],
            bucket=resp["bucket"],
            media_link=resp.get("mediaLink"),
            generation=resp.get("generation"),
            content_type=resp.get("contentType"),
            size=int(resp["size"]),
            creation_time=datetime.fromisoformat(resp["timeCreated"]),
            update_time=datetime.fromisoformat(resp["updated"]),
        )

    async def copy_blob(
        self,
        src_bucket_name: str,
        src_key: str,
        dest_bucket_name: str,
        dest_key: str,
    ):
        done = False
        rewrite_token = None
        try:
            while not done:
                params = {}
                if rewrite_token:
                    params = {"rewriteToken": rewrite_token}

                resp = await self._make_api_request(
                    "POST",
                    urljoin(
                        self.api_url,
                        f"b/{src_bucket_name}/o/{quote(src_key, safe='')}/rewriteTo/b/{dest_bucket_name}/o/{quote(dest_key, safe='')}",
                    ),
                    "CopyBlob",
                    params=params,
                    headers={"Content-Type": "application/json"},
                    return_json=True,
                )

                done = resp["done"]
                rewrite_token = resp.get("rewriteToken", None)
        except NotFound:
            return None

    async def delete_blob(
        self, bucket_name: str, key: str, *, generation: str | None = None
    ):
        params = {}
        if generation is not None:
            params["generation"] = generation

        try:
            await self._make_api_request(
                "DELETE",
                urljoin(self.api_url, f"b/{bucket_name}/o/{quote(key, safe='')}"),
                "DeleteBlob",
                params=params,
            )
        except NotFound:
            return None

    def get_signed_download_url(
        self,
        bucket_name: str,
        key: str,
        *,
        content_disposition: str | None = None,
        content_type: str | None = None,
    ):
        with tracer.start_as_current_span("get_signed_download_url") as s:
            s.set_attributes(
                {
                    "bucket_name": bucket_name,
                    "key": str(key),
                    "content_disposition": str(content_disposition),
                    "content_type": str(content_type),
                }
            )
            # note(taras): This will not make an HTTP request
            blob = self.google_client.bucket(bucket_name).blob(key)

            return blob.generate_signed_url(
                version="v4",
                expiration=max_presigned_url_age,
                method="GET",
                response_disposition=content_disposition,
                response_type=content_type,
            )

    async def get_signed_upload_url(
        self,
        bucket_name: str,
        key: str,
    ):
        with tracer.start_as_current_span("get_signed_upload_url") as s:
            s.set_attributes(
                {
                    "bucket_name": bucket_name,
                    "key": key,
                }
            )

            # note(taras): This will not make an HTTP request
            blob = self.google_client.bucket(bucket_name).blob(key)

            return blob.generate_signed_url(
                version="v4",
                expiration=max_presigned_url_age,
                method="PUT",
            )

    async def get_signed_part_upload_url(
        self,
        bucket_name: str,
        key: str,
        upload_id: str,
        part_number: int,
    ):
        with tracer.start_as_current_span("get_signed_part_upload_url") as s:
            s.set_attributes(
                {
                    "bucket_name": bucket_name,
                    "key": key,
                    "upload_id": upload_id,
                    "part_number": part_number,
                }
            )

            # note(taras): This will not make an HTTP request
            blob = self.google_client.bucket(bucket_name).blob(key)

            return blob.generate_signed_url(
                version="v4",
                expiration=max_presigned_url_age,
                method="PUT",
                query_parameters={
                    "partNumber": part_number,
                    "uploadId": upload_id,
                },
            )

    async def multipart_initiate_upload(
        self,
        bucket_name: str,
        key: str,
        *,
        content_type: str = "text/plain",
    ):
        resp = await self._make_api_request(
            "POST",
            f"https://storage.googleapis.com/{bucket_name}/{quote(key, safe='')}?uploads",
            "InitiateMultipartUpload",
            headers={
                "Content-Type": content_type,
                "Content-Length": "0"
            },
        )

        return str(xmltodict.parse(resp)["InitiateMultipartUploadResult"]["UploadId"])

    async def multipart_upload_part(
        self,
        bucket_name: str,
        key: str,
        upload_id: str,
        part_number: int,
        data: bytes,
    ) -> str:
        resp = await self._make_api_request(
            "PUT",
            f"https://storage.googleapis.com/{bucket_name}/{quote(key, safe='')}?uploadId={upload_id}&partNumber={part_number}",
            "UploadPart",
            data=data,
            return_response=True,
        )

        return resp.headers["ETag"]

    async def multipart_complete_upload(
        self,
        bucket_name: str,
        key: str,
        upload_id: str,
        parts: list[CompletedPartTypeDef],
    ) -> str:
        root = ET.Element("CompleteMultipartUpload")

        for part in parts:
            if "PartNumber" not in part:
                raise ValueError("PartNumber is required")
            if "ETag" not in part:
                raise ValueError("ETag is required")

            part_element = ET.SubElement(root, "Part")
            ET.SubElement(part_element, "PartNumber").text = str(part["PartNumber"])
            ET.SubElement(part_element, "ETag").text = part["ETag"]

        await self._make_api_request(
            "POST",
            f"https://storage.googleapis.com/{bucket_name}/{quote(key, safe='')}?uploadId={upload_id}",
            "CompleteMultipartUpload",
            data=ET.tostring(root),
        )

        blob = await self.get_blob_meta(bucket_name, key)
        if blob is None:
            raise ServerError("Failed to complete multipart upload: can't find blob")
        if blob["generation"] is None:
            raise ServerError("The uploaded blob has no generation")

        return blob["generation"]


@dataclass
class AsyncGCPListBlobsIterator:
    url: str
    headers: dict[str, str]
    params: dict[str, str]
    storage_client: AsyncGCPStorageClient
    max_items: int | None

    cur_item = 0
    items: list = field(default_factory=list)
    prefixes: set[str] = field(default_factory=set)
    next_page_token: str | None = None

    def __aiter__(self):
        return self

    async def __anext__(self):
        if (self.max_items is not None and self.cur_item >= self.max_items) or (
            len(self.items) == 0 and self.next_page_token == ""
        ):
            raise StopAsyncIteration

        if len(self.items) > 0:
            obj = self.items.pop()
            self.cur_item = self.cur_item + 1

            creation_time = obj.get("timeCreated")
            if creation_time is not None:
                creation_time = datetime.fromisoformat(creation_time)

            update_time = obj.get("updated")
            if update_time is not None:
                update_time = datetime.fromisoformat(update_time)

            return Object(
                id=obj["id"],
                name=obj["name"],
                bucket=obj["bucket"],
                media_link=obj.get("mediaLink"),
                generation=obj.get("generation"),
                content_type=obj.get("contentType"),
                size=int(obj["size"]),
                creation_time=creation_time,
                update_time=update_time,
            )

        if self.next_page_token:
            self.params["pageToken"] = self.next_page_token

        res = await self.storage_client._make_api_request(
            "GET",
            self.url,
            "ListBlobs",
            headers=self.headers,
            params=self.params,
            return_json=True,
        )

        self.items = res.get("items", [])
        prefixes = res.get("prefixes", [])
        self.next_page_token = res.get("nextPageToken", "")

        for prefix in prefixes:
            self.prefixes.add(prefix)

        if "items" not in res:
            raise StopAsyncIteration

        return await self.__anext__()
