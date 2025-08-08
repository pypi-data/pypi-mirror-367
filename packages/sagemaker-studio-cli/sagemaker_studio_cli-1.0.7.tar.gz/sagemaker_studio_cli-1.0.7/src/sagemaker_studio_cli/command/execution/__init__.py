import click
from sagemaker_studio.models.execution import InternalServerError

from sagemaker_studio_cli.command.api_client import get_api_client
from sagemaker_studio_cli.command.utils import parse_execution_args, print_formatted, prune_args


@click.group()
def execution():
    """
    SageMaker Studio CLI to manage execution

    To see options for a command, you can run:
        sagemaker-studio execution <subcommand> --help
    """
    pass


@execution.command(
    name="start",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=False,
    ),
)
@click.option("--execution-name", required=True)
@click.option("--input-config", required=True)
@click.option("--execution-type", required=False)
@click.option("--domain-identifier", required=False)
@click.option("--project-identifier", required=False)
@click.option("--output-config", required=False)
@click.option("--compute", required=False)
@click.option("--client-token", required=False)
@click.option("--termination-condition", required=False)
@click.option("--tags", required=False)
@click.option("--remote", is_flag=True, hidden=True)
@click.option("--profile", required=False, help="Specifies which AWS profile to use")
@click.option(
    "--region", required=False, help="Specifies which AWS region to send this requests to"
)
def start_execution(*args, **kwargs):
    args = parse_execution_args(kwargs)
    execution_client = get_execution_client(args)
    request_args = prune_args(args)
    print_formatted(execution_client.start_execution(**request_args))


@execution.command(
    name="stop",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=False,
    ),
)
@click.option("--execution-id", required=True)
@click.option("--domain-identifier", required=False)
@click.option("--project-identifier", required=False)
@click.option("--remote", is_flag=True, hidden=True)
@click.option("--profile", required=False, help="Specifies which AWS profile to use")
@click.option(
    "--region", required=False, help="Specifies which AWS region to send this requests to"
)
def stop_execution(*args, **kwargs):
    args = parse_execution_args(kwargs)
    execution_client = get_execution_client(args)
    request_args = prune_args(args)
    print_formatted(execution_client.stop_execution(**request_args))


@execution.command(
    name="get",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=False,
    ),
)
@click.option("--execution-id", required=True)
@click.option("--domain-identifier", required=False)
@click.option("--project-identifier", required=False)
@click.option("--remote", is_flag=True, hidden=True)
@click.option("--profile", required=False, help="Specifies which AWS profile to use")
@click.option(
    "--region", required=False, help="Specifies which AWS region to send this requests to"
)
def get_execution(*args, **kwargs):
    args = parse_execution_args(kwargs)
    execution_client = get_execution_client(args)
    request_args = prune_args(args)
    print_formatted(execution_client.get_execution(**request_args))


@execution.command(
    name="list",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=False,
    ),
)
@click.option("--domain-identifier", required=False)
@click.option("--project-identifier", required=False)
@click.option("--start-time-after", required=False, type=int)
@click.option("--name-contains", required=False)
@click.option("--status", required=False)
@click.option("--sort-by", required=False)
@click.option("--sort-order", required=False)
@click.option("--filter-by-tags", required=False)
@click.option("--next-token", required=False)
@click.option("--max-results", required=False, type=int)
@click.option("--remote", is_flag=True, hidden=True)
@click.option("--profile", required=False, help="Specifies which AWS profile to use")
@click.option(
    "--region", required=False, help="Specifies which AWS region to send this requests to"
)
def list_executions(*args, **kwargs):
    args = parse_execution_args(kwargs)
    execution_client = get_execution_client(args)
    request_args = prune_args(args)
    print_formatted(execution_client.list_executions(**request_args))


def get_execution_client(kwargs):
    execution_client = get_api_client(
        region_name=kwargs.get("region") if kwargs.get("region") else None,
        profile_name=kwargs.get("profile") if kwargs.get("profile") else None,
        use_local_execution=(not kwargs["remote"]),
    ).execution_client
    if execution_client is None:
        raise InternalServerError("execution api is not configured")
    return execution_client
