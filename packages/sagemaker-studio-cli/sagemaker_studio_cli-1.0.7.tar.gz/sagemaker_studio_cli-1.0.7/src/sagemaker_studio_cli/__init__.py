import click

from sagemaker_studio_cli.command.credentials import credentials
from sagemaker_studio_cli.command.execution import execution
from sagemaker_studio_cli.command.git import git
from sagemaker_studio_cli.command.project import project


@click.group(name="sagemaker_studio")
def sagemaker_studio() -> None:
    """
    SageMaker Studio CLI is a command line interface for interacting with SageMaker Studio.
    """
    pass


# Add credentials subcommands
sagemaker_studio.add_command(credentials)

# Add execution subcommands
sagemaker_studio.add_command(execution)

# Add project subcommands
sagemaker_studio.add_command(project)

# Add git subcommands
sagemaker_studio.add_command(git)
