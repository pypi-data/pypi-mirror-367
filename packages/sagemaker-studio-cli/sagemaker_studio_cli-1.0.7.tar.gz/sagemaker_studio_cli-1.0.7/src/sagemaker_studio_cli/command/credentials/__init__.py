import click

from sagemaker_studio_cli.command.api_client import get_api_client
from sagemaker_studio_cli.command.config import CONFIG_DOMAIN_ID_KEY, GlobalConfig
from sagemaker_studio_cli.command.utils import print_formatted


@click.group()
def credentials() -> None:
    """
    SageMaker Studio CLI command-line interface to manage credentials

    To see options for a command, you can run:
        sagemaker-studio credentials <subcommand> --help
    """
    pass


@credentials.command(
    name="get-domain-execution-role-credential-in-space",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=False,
    ),
)
@click.option("-dm", "--domain-id", required=False, help="Domain identifier")
@click.option("--profile", required=False, help="Specifies which AWS profile to use")
@click.option(
    "--region", required=False, help="Specifies which AWS region to send this requests to"
)
@click.pass_context
def get_domain_execution_role_credential_in_space(*args, **kwargs):
    sagemaker_studio_cli_api = get_api_client(
        region_name=kwargs.get("region") if kwargs.get("region") else None,
        profile_name=kwargs.get("profile") if kwargs.get("profile") else None,
    )
    global_config = GlobalConfig()
    domain_id = kwargs["domain_id"] or global_config.get(CONFIG_DOMAIN_ID_KEY)
    credentials_api = sagemaker_studio_cli_api.credentials_api
    print_formatted(credentials_api.get_domain_execution_role_credential_in_space(domain_id))
