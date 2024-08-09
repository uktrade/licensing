from typing import Any, List

from core.document_storage import PermanentDocumentStorage, TemporaryDocumentStorage
from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase
from django.core.cache import cache
from django.http import HttpRequest
from django.urls import reverse
from storages.backends.s3boto3 import S3Boto3Storage


def get_s3_client_from_storage(s3_storage: S3Boto3Storage) -> Any:
    """Get the S3 client object from the storage object."""
    return s3_storage.bucket.meta.client


def generate_presigned_url(s3_storage: Any, s3_file_object: Any) -> str:
    """Generates a Presigned URL for the s3 object."""

    s3_client = get_s3_client_from_storage(s3_storage=s3_storage)

    presigned_url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": s3_storage.bucket_name, "Key": s3_file_object},
        HttpMethod="GET",
        ExpiresIn=settings.PRESIGNED_URL_EXPIRY_SECONDS,
    )
    return presigned_url


def get_all_session_files(s3_storage: S3Boto3Storage, session: SessionBase) -> dict[str, Any]:
    """Gets all files that a user has uploaded in a session."""
    s3_client = get_s3_client_from_storage(s3_storage=s3_storage)
    response = s3_client.list_objects_v2(Bucket=s3_storage.bucket.name, Prefix=session.session_key)
    session_files = {}

    user_uploaded_files = get_user_uploaded_files(session)
    for content in response.get("Contents", []):
        file_name = content["Key"].rpartition("/")[2]

        # checking that a file with this name was uploaded in the session
        if file_name in user_uploaded_files:
            session_files[file_name] = reverse("download_document", kwargs={"file_name": file_name})
    return session_files


def get_licence_documents(s3_storage: S3Boto3Storage, licence_id: str) -> dict[str, Any]:
    """Gets all files associated with a licensing application."""
    s3_client = get_s3_client_from_storage(s3_storage=s3_storage)
    response = s3_client.list_objects_v2(Bucket=s3_storage.bucket.name, Prefix=licence_id)
    licence_files = {}
    for content in response.get("Contents", []):
        file_name = content["Key"].rpartition("/")[2]
        licence_files[file_name] = generate_presigned_url(
            s3_storage=s3_storage,
            s3_file_object=content["Key"],
        )
    return licence_files


def delete_session_files(s3_storage: S3Boto3Storage, session: SessionBase) -> None:
    s3_client = get_s3_client_from_storage(s3_storage=s3_storage)

    response = s3_client.list_objects_v2(Bucket=s3_storage.bucket.name, Prefix=session.session_key)
    delete_keys = {"Objects": []}
    delete_keys["Objects"] = [{"Key": k} for k in [obj["Key"] for obj in response.get("Contents", [])]]
    s3_client.delete_objects(Bucket=s3_storage.bucket.name, Delete=delete_keys)


def get_user_uploaded_files(session: SessionBase) -> List[str]:
    """Returns a list of file_names that a user has uploaded in a session.

    Files are uploaded to the session's key in the cache, so we scan the entire redis cache for all keys that
    start with the session key and return a list of the values."""
    cache_keys = list(cache.iter_keys(f"{session.session_key}*"))
    uploaded_files = [file_name for key, file_name in cache.get_many(cache_keys).items()]
    return uploaded_files


def store_documents_in_s3(request: HttpRequest, licence_id: str) -> None:
    """
    Copies documents from the default temporary storage to permanent storage on s3
    """
    temporary_storage_bucket = TemporaryDocumentStorage()
    permanent_storage_bucket = PermanentDocumentStorage()

    if session_files := get_all_session_files(temporary_storage_bucket, request.session):
        for object_key in session_files.keys():
            permanent_storage_bucket.bucket.meta.client.copy(
                CopySource={
                    "Bucket": settings.TEMPORARY_S3_BUCKET_NAME,
                    "Key": f"{request.session.session_key}/{object_key}",
                },
                Bucket=settings.PERMANENT_S3_BUCKET_NAME,
                Key=f"{licence_id}/{object_key}",
                SourceClient=temporary_storage_bucket.bucket.meta.client,
            )
