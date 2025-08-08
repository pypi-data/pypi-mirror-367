from typing import Optional

from sagemaker_studio import ClientConfig, SageMakerStudioAPI

from sagemaker_studio_cli.command.config import (
    CONFIG_DZ_ENDPOINT_KEY,
    CONFIG_PROFILE_KEY,
    CONFIG_REGION_KEY,
    GlobalConfig,
)


def get_api_client(
    region_name: Optional[str] = None, profile_name: Optional[str] = None, use_local_execution=True
):
    global_config = GlobalConfig()
    region = region_name or global_config.get(CONFIG_REGION_KEY) or "us-east-1"
    profile = profile_name or global_config.get(CONFIG_PROFILE_KEY) or "default"

    datazone_endpoint = global_config.get(CONFIG_DZ_ENDPOINT_KEY)

    config = ClientConfig(
        region=region,
        profile_name=profile,
        overrides={
            "execution": {
                "local": use_local_execution,
            },
            "datazone": {
                "endpoint_url": datazone_endpoint,
            },
        },
    )
    return SageMakerStudioAPI(config=config)
