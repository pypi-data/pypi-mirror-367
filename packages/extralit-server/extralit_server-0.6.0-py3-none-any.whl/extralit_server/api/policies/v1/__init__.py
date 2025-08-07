#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from extralit_server.api.policies.v1.commons import authorize, is_authorized
from extralit_server.api.policies.v1.dataset_policy import DatasetPolicy
from extralit_server.api.policies.v1.field_policy import FieldPolicy
from extralit_server.api.policies.v1.metadata_property_policy import MetadataPropertyPolicy
from extralit_server.api.policies.v1.question_policy import QuestionPolicy
from extralit_server.api.policies.v1.record_policy import RecordPolicy
from extralit_server.api.policies.v1.response_policy import ResponsePolicy
from extralit_server.api.policies.v1.suggestion_policy import SuggestionPolicy
from extralit_server.api.policies.v1.user_policy import UserPolicy
from extralit_server.api.policies.v1.vector_settings_policy import VectorSettingsPolicy
from extralit_server.api.policies.v1.workspace_policy import WorkspacePolicy
from extralit_server.api.policies.v1.workspace_user_policy import WorkspaceUserPolicy
from extralit_server.api.policies.v1.webhook_policy import WebhookPolicy
from extralit_server.api.policies.v1.job_policy import JobPolicy
from extralit_server.api.policies.v1.file_policy import FilePolicy
from extralit_server.api.policies.v1.document_policy import DocumentPolicy

__all__ = [
    "DatasetPolicy",
    "FieldPolicy",
    "MetadataPropertyPolicy",
    "QuestionPolicy",
    "RecordPolicy",
    "ResponsePolicy",
    "SuggestionPolicy",
    "UserPolicy",
    "VectorSettingsPolicy",
    "WorkspacePolicy",
    "WorkspaceUserPolicy",
    "WebhookPolicy",
    "JobPolicy",
    "FilePolicy",
    "DocumentPolicy",
    "authorize",
    "is_authorized",
]
