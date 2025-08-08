import json
import os
from typing import Dict

LOOSE_LEAF_METADATA_FILE_PATH = "/opt/ml/metadata/resource-metadata.json"
LOOSE_LEAF_METADATA_JSON_KEY = "AdditionalMetadata"

CONFIG_REGION_KEY = "region"
CONFIG_PROFILE_KEY = "profile"
CONFIG_DZ_ENDPOINT_KEY = "dataZoneEndpoint"
CONFIG_REPO_HOME_KEY = "repoHome"
CONFIG_USER_ID_KEY = "dataZoneUserId"
CONFIG_USER_NAME_KEY = "dataZoneUserName"
CONFIG_USER_EMAIL_KEY = "dataZoneUserEmail"
CONFIG_DOMAIN_ID_KEY = "dataZoneDomainId"
CONFIG_PROJECT_ID_KEY = "dataZoneProjectId"
CONFIG_DEFAULT_ENV_ID_KEY = "dataZoneEnvironmentId"
CONFIG_REPO_NAME_KEY = "dataZoneProjectRepositoryName"
CONFIG_PROJECT_IDENTIFIER_KEY = "projectIdentifier"
CONFIG_DOMAIN_IDENTIFIER_KEY = "domainIdentifier"
CONFIG_STAGE_KEY = "dataZoneStageName"


class GlobalConfig:

    def __init__(self):
        self._config: Dict = {}

        region = os.environ.get("AWS_DEFAULT_REGION") or os.environ.get("AWS_REGION") or "us-east-1"
        profile = os.environ.get("AWS_PROFILE") or "default"
        user_identifier = os.environ.get("DataZoneUserId") or ""
        repo_user_name = os.environ.get("DataZoneUserName") or ""
        repo_user_email = os.environ.get("DataZoneUserEmail") or ""
        domain_id = os.environ.get("DataZoneDomainId") or ""
        project_id = os.environ.get("DataZoneProjectId") or ""
        repo_name = os.environ.get("DataZoneProjectRepositoryName") or ""
        stage = ""

        if os.path.exists(LOOSE_LEAF_METADATA_FILE_PATH):
            with open(
                LOOSE_LEAF_METADATA_FILE_PATH, "r", encoding="utf-8"
            ) as loose_leaf_metadata_file:
                metadata_top_level_json = json.load(loose_leaf_metadata_file)
                metadata_json = metadata_top_level_json.get(LOOSE_LEAF_METADATA_JSON_KEY) or {}
                user_identifier = metadata_json.get("DataZoneUserId") or ""
                repo_user_name = metadata_json.get("DataZoneUserName") or ""
                repo_user_email = metadata_json.get("DataZoneUserEmail") or ""
                domain_id = metadata_json.get("DataZoneDomainId") or ""
                project_id = metadata_json.get("DataZoneProjectId") or ""
                region = metadata_json.get("DataZoneDomainRegion") or "us-east-1"
                stage = metadata_json.get("DataZoneStage") or ""
                datazone_endpoint = metadata_json.get("DataZoneEndpoint") or ""

        self.set("domainIdentifier", domain_id)
        self.set("projectIdentifier", project_id)

        if CONFIG_REGION_KEY not in self._config:
            self.set(CONFIG_REGION_KEY, region)
        if CONFIG_PROFILE_KEY not in self._config:
            self.set(CONFIG_PROFILE_KEY, profile)
        if CONFIG_DOMAIN_ID_KEY not in self._config:
            self.set(CONFIG_DOMAIN_ID_KEY, domain_id)
        if CONFIG_PROJECT_ID_KEY not in self._config:
            self.set(CONFIG_PROJECT_ID_KEY, project_id)
        if CONFIG_USER_ID_KEY not in self._config:
            self.set(CONFIG_USER_ID_KEY, user_identifier)
        if CONFIG_USER_NAME_KEY not in self._config:
            self.set(CONFIG_USER_NAME_KEY, repo_user_name)
        if CONFIG_USER_EMAIL_KEY not in self._config:
            self.set(CONFIG_USER_EMAIL_KEY, repo_user_email)
        if CONFIG_REPO_NAME_KEY not in self._config:
            self.set(CONFIG_REPO_NAME_KEY, repo_name)
        if CONFIG_REPO_HOME_KEY not in self._config:
            self.set(
                CONFIG_REPO_HOME_KEY,
                "{home}/{repo}/".format(home=os.environ.get("HOME"), repo=repo_name),
            )
        if CONFIG_STAGE_KEY not in self._config:
            self.set(CONFIG_STAGE_KEY, stage)
        if CONFIG_DZ_ENDPOINT_KEY not in self._config:
            self.set(CONFIG_DZ_ENDPOINT_KEY, datazone_endpoint)

    def get(self, key):
        if key in self._config:
            return self._config[key]
        return None

    def set(self, key, value):
        self._config[key] = value

    def store(self):
        return self._config if len(self._config) > 0 else None

    def get_api_context(self):
        api_context = {}
        if CONFIG_DOMAIN_IDENTIFIER_KEY in self._config:
            api_context[CONFIG_DOMAIN_IDENTIFIER_KEY] = self.get(CONFIG_DOMAIN_IDENTIFIER_KEY)
        if CONFIG_PROJECT_IDENTIFIER_KEY in self._config:
            api_context[CONFIG_PROJECT_IDENTIFIER_KEY] = self.get(CONFIG_PROJECT_IDENTIFIER_KEY)

        return api_context

    def set_or_delete(self, key, value):
        if value is not None:
            if len(value) > 0:
                self.set(key, value)
            else:
                del self._config[key]
