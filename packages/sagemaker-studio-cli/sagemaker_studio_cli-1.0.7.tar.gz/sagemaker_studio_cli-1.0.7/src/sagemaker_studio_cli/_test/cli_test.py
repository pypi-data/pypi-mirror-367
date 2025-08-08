import pytest
from click.testing import CliRunner

import sagemaker_studio_cli


@pytest.fixture()
def cli_runner():
    return CliRunner()


def test_sagemaker_studio_cli_importable():
    from sagemaker_studio_cli import sagemaker_studio

    assert sagemaker_studio is not None


def test_sagemaker_studio_cli_get_domain_execution_role_credential_in_space_missing_option_successful(
    cli_runner,
):
    result = cli_runner.invoke(
        sagemaker_studio_cli.sagemaker_studio,
        ["credentials", "get-domain-execution-role-credential-in-space"],
    )
    assert result.exit_code == 1


def test_sagemaker_studio_cli_get_domain_exectuion_role_credential_in_space(cli_runner):
    result = cli_runner.invoke(
        sagemaker_studio_cli.sagemaker_studio,
        [
            "credentials",
            "get-domain-execution-role-credential-in-space",
            "--domain-id",
            "dzd_12345678910112",
        ],
    )
    assert result.exit_code == 1


def test_sagemaker_studio_cli_list_executions(cli_runner):
    result = cli_runner.invoke(sagemaker_studio_cli.sagemaker_studio, ["execution", "list"])
    assert result.exit_code == 1


def test_sagemaker_studio_cli_get_project_default_environment(cli_runner):
    result = cli_runner.invoke(
        sagemaker_studio_cli.sagemaker_studio,
        [
            "project",
            "get-project-default-environment",
            "--domain-id",
            "dzd_66ij67biyjty4w",
            "--project-id",
            "61p1t7s1b4n40g",
        ],
    )
    assert result.exit_code == 1


def test_sagemaker_studio_cli_get_clone_url(cli_runner):
    result = cli_runner.invoke(
        sagemaker_studio_cli.sagemaker_studio,
        [
            "git",
            "get-clone-url",
            "--domain-id",
            "dzd_66ij67biyjty4w",
            "--project-id",
            "61p1t7s1b4n40g",
        ],
    )
    assert result.exit_code == 1
