# SageMaker Studio CLI

SageMaker Studio CLI is an open source command-line utility for interacting with Amazon SageMaker Unified Studio. With this CLI, you can access SageMaker Unified Studio resources and run both local and remote executions.

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
   1. [Setting up Credentials](#setting-up-credentials)
      1. [AWS Named Profile](#aws-named-profile)
   2. [Commands](#commands)
       1. [credentials](#credentials)
          1. [get-domain-execution-role-credential-in-space](#get-domain-execution-role-credential-in-space)
       2. [project](#project)
          1. [get-project-default-environment](#get-project-default-environment)
       3. [git](#git)
          1. [get-clone-url](#get-clone-url)
       4. [execution](#execution)
          1. [start](#start)
          2. [get](#get)
          3. [list](#list-1)
          4. [stop](#stop)

## 1) Installation

The SageMaker Studio CLI is built to PyPI, and the latest version of the CLI can be installed using the following command:

```bash
pip install sagemaker-studio
```

#### Supported Python Versions
SageMaker Studio CLI supports Python versions 3.9 and newer.


#### Licensing

SageMaker Studio CLI is licensed under the Apache 2.0 License. It is copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. The license is available at: http://aws.amazon.com/apache2.0/


## 2) Usage

### Setting Up Credentials

If SageMaker Studio CLI is being used within SageMaker Unified Studio JupyterLab, the CLI will automatically pull your latest credentials from the environment.

If you are using the CLI elsewhere, or if you want to use different credentials within SageMaker Unified Studio JupyterLab, you will need to first retrieve your SageMaker Unified Studio credentials and make them available in the environment by storing them within an [AWS named profile](https://docs.aws.amazon.com/sdkref/latest/guide/file-format.html). If you are using a profile name other than `default`, you need to supply the profile name using one of the following methods:
1. Supplying it as part of your CLI command (e.g. `--profile my_profile_name`)
2. Setting the AWS profile name as an environment variable (e.g. `export AWS_PROFILE="my_profile_name"`)

##### AWS Named Profile

To create an AWS named profile, you can update your AWS `config` file with your profile name and any other settings you would like to use:

```config
[my_profile_name]
region = us-east-1
```

Your `credentials` file should have the credentials stored for your profile:

```config
[my_profile_name]
aws_access_key_id=AKIAIOSFODNN7EXAMPLE
aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
aws_session_token=IQoJb3JpZ2luX2IQoJb3JpZ2luX2IQoJb3JpZ2luX2IQoJb3JpZ2luX2IQoJb3JpZVERYLONGSTRINGEXAMPLE
```

Finally, you can use this profile `my_profile_name` through any of the three methods listed in the above section.


### Commands

SageMaker Studio CLI has several commands that you can use to interact with your resources within SageMaker Unified Studio.


#### credentials


##### get-domain-execution-role-credential-in-space

The following command prints domain execution role credentials for a space.

```bash
sagemaker-studio credentials get-domain-execution-role-credential-in-space --domain-id <domain_id>
```


#### project

##### get-project-default-environment

The following command prints the details of the default environment within your project.

```bash
sagemaker-studio project get-project-default-environment --project-id <project_id> --domain-id <domain_id>
```


#### git

##### get-clone-url

The following command prints the clone URL for the project's Git repository.

```bash
sagemaker-studio git get-clone-url --project-id <project_id> --domain-id <domain_id>
```


#### execution

##### start

The following command starts an execution in the user's space.

```bash
sagemaker-studio execution start --execution-name <execution-name> --input-config '{ "notebook_config": { "input_path": <input_path_relative to user's home directory> } } '
```

To start the execution on remote compute, pass the `--remote` flag and other required parameters like `--compute` in the following command.
```bash
sagemaker-studio execution start --remote --execution-name <execution-name> --input-config '{ "notebook_config": { "input_path": <input_path_relative to user's home directory> } } ' --compute '{ "instance_type": "ml.c4.2xlarge", "image_details": { "image_name": "sagemaker-distribution-embargoed-prod", "image_version": "3.0" }}'
```

##### get
The following command gets details of an execution running in the user's space.
```bash
sagemaker-studio execution get --execution-id <execution-id>
```
To get the details of an execution running on remote compute, pass the `--remote` flag in the following command.
```bash
sagemaker-studio execution get --execution-id <execution-id> --remote
```

##### list
The following command lists executions running in the user's space.
```bash
sagemaker-studio execution list
```

The following optional filters are supported:
- `--name-contains <name>`
- `--status` valid values: ['IN_PROGRESS', 'COMPLETED', 'FAILED', 'STOPPING', 'STOPPED']
- `--sort-by` valid values: ['NAME', 'STATUS', 'START_TIME', 'END_TIME']
- `--sort-order` valid values: ['ASCENDING', 'DESCENDING']
- `--start-time-after <timestamp_in_millis>`
- `--next-token <next_token>`
- `--max-items <int>`

```bash
sagemaker-studio execution list --name-contains "asdf" --status COMPLETED --sort-order ASCENDING --start-time-after 1730327776000
```

To list executions running on remote compute, pass the `--remote` flag in the following command.
```bash
sagemaker-studio execution list --remote --name-contains "asdf" --status COMPLETED --sort-order ASCENDING --start-time-after 1730327776000
```
The following optional filters are supported:
- `--name-contains <name>`
- `--status` valid values: ['IN_PROGRESS', 'COMPLETED', 'FAILED', 'STOPPING', 'STOPPED']
- `--sort-by` valid values: ['NAME', 'STATUS', 'START_TIME', 'END_TIME']
- `--sort-order` valid values: ['ASCENDING', 'DESCENDING']
- `--start-time-after <timestamp_in_millis>`
- `--next-token <next_token>`
- `--max-items <int>`
- `--filter-by-tags <dict>`

##### stop
The following command stops an execution running in the user's space.
```bash
sagemaker-studio execution stop --execution-id <execution-id>
```
To stop an execution running on remote compute, pass the `--remote` flag in the following command.
```bash
sagemaker-studio execution stop --execution-id <execution-id> --remote
```
