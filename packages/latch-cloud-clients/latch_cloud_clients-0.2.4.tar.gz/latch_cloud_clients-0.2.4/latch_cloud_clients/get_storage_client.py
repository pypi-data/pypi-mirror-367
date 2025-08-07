from typing import Literal

from .aws.storage_client import S3StorageClient
from .gcp.storage_client import GCPStorageClient
from .utils import StorageClient


def get_storage_client(
    root_type: (
        Literal[
            "account_root", "dir", "obj", "mount", "link", "mount_gcp", "mount_azure"
        ]
        | None
    ),
) -> StorageClient:
    if root_type is not None and root_type not in [
        "account_root",
        "mount",
        "mount_gcp",
        "mount_azure",
    ]:
        raise ValueError(f"Type is not a root, got: {root_type}")

    if root_type == "mount_gcp":
        return GCPStorageClient()
    elif root_type == "mount_azure":
        raise NotImplementedError("Azure storage is not implemented")
    else:
        return S3StorageClient()
