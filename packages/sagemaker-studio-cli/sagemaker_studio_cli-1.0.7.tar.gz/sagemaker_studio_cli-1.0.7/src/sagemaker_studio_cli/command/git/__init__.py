import click

from sagemaker_studio_cli.command.api_client import get_api_client
from sagemaker_studio_cli.command.config import (
    CONFIG_DOMAIN_ID_KEY,
    CONFIG_PROJECT_ID_KEY,
    GlobalConfig,
)
from sagemaker_studio_cli.command.utils import print_formatted


@click.group()
def git():
    """
    SageMaker Studio CLI to manage git

    To see options for a command, you can run:
        sagemaker-studio git <subcommand> --help
    """
    pass


@git.command(
    name="get-clone-url",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=False,
    ),
)
@click.option("-dm", "--domain-id", required=False, help="Domain identifier")
@click.option("-pj", "--project-id", required=False, help="Project identifier")
@click.option("--profile", required=False, help="Specifies which AWS profile to use")
@click.option(
    "--region", required=False, help="Specifies which AWS region to send this requests to"
)
@click.pass_context
def get_clone_url(*args, **kwargs):
    sagemaker_studio_cli_api = get_api_client(
        region_name=kwargs.get("region") if kwargs.get("region") else None,
        profile_name=kwargs.get("profile") if kwargs.get("profile") else None,
    )
    global_config = GlobalConfig()
    domain_id = kwargs["domain_id"] or global_config.get(CONFIG_DOMAIN_ID_KEY)
    project_id = kwargs["project_id"] or global_config.get(CONFIG_PROJECT_ID_KEY)
    git_api = sagemaker_studio_cli_api.git_api
    print_formatted(git_api.get_clone_url(domain_id, project_id))
