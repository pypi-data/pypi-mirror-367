# Copyright 2024-present, Extralit Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Security
from fastapi.responses import StreamingResponse
from minio import Minio, S3Error

from extralit_server.contexts import files
from extralit_server.models import User
from extralit_server.api.policies.v1 import FilePolicy, authorize
from extralit_server.api.schemas.v1.files import ListObjectsResponse, ObjectMetadata
from extralit_server.security import auth

_LOGGER = logging.getLogger(__name__)

router = APIRouter(tags=["files"])


@router.get("/file/{bucket}/{object:path}")
async def get_file(
    *,
    bucket: str,
    object: str,
    version_id: Optional[str] = None,
    client: Minio = Depends(files.get_minio_client),
    current_user: Optional[User] = Security(auth.get_optional_current_user),
):
    # TODO Check if the current user is in the workspace to have access to the s3 bucket of the same name
    # if current_user is not None or current_user.role != "owner":
    #     await authorize(current_user, FilePolicy.get(bucket))

    try:
        file_response = files.get_object(client, bucket, object, version_id=version_id, include_versions=True)

        return StreamingResponse(
            file_response.response, media_type=file_response.metadata.content_type, headers=file_response.http_headers
        )
    except S3Error as se:
        _LOGGER.error(f"Error getting object '{bucket}/{object}': {se}")
        raise HTTPException(status_code=404, detail=f"No object at path '{object}' was found") from se

    except Exception as e:
        _LOGGER.error(f"Error getting object '{bucket}/{object}': {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/file/{bucket}/{object:path}", response_model=ObjectMetadata)
async def put_file(
    *,
    bucket: str,
    object: str,
    file: UploadFile = File(...),
    client: Minio = Depends(files.get_minio_client),
    current_user: User = Security(auth.get_current_user),
):
    # Check if the current user is in the workspace to have access to the s3 bucket of the same name
    await authorize(current_user, FilePolicy.put_object(bucket))

    try:
        response = files.put_object(
            client, bucket, object, data=file.file, size=file.size, content_type=file.content_type
        )
        return response
    except S3Error as se:
        raise HTTPException(status_code=500, detail=f"Internal server error: {se.message}") from se


@router.get("/files/{bucket}/{prefix:path}", response_model=ListObjectsResponse)
async def list_objects(
    *,
    bucket: str,
    prefix: str,
    include_version=True,
    recursive=True,
    start_after: Optional[str] = None,
    client: Minio = Depends(files.get_minio_client),
    current_user: User = Security(auth.get_current_user),
):
    # Check if the current user is in the workspace to have access to the s3 bucket of the same name
    await authorize(current_user, FilePolicy.list(bucket))

    try:
        objects = files.list_objects(
            client, bucket, prefix=prefix, include_version=include_version, recursive=recursive, start_after=start_after
        )
        return objects
    except S3Error as se:
        _LOGGER.error(f"Error listing objects in '{bucket}/{prefix}': {se}")
        if se.code == "NoSuchBucket":
            raise HTTPException(
                status_code=404,
                detail=f"Bucket '{bucket}' not found, please run `ex.Workspace.create('{bucket}')` to create the S3 bucket.",
            ) from se
        else:
            raise HTTPException(
                status_code=404, detail=f"Cannot list objects as '{bucket}/{prefix}' is not found"
            ) from se
    except Exception as e:
        raise e


@router.delete("/file/{bucket}/{object:path}")
async def delete_files(
    *,
    bucket: str,
    object: str,
    version_id: Optional[str] = None,
    client: Minio = Depends(files.get_minio_client),
    current_user: User = Security(auth.get_current_user),
):
    # Check if the current user is in the workspace to have access to the s3 bucket of the same name
    await authorize(current_user, FilePolicy.delete(bucket))

    try:
        files.delete_object(client, bucket, object, version_id=version_id)
        return {"message": "File deleted"}
    except S3Error as se:
        raise HTTPException(status_code=500, detail="Internal server error") from se
    except Exception as e:
        raise e
