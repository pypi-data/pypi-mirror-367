import os
from pathlib import Path

from setuptools import Command, find_packages, setup

VERSION = Path(__file__).parent.joinpath("VERSION").read_text()
# Declare your non-python data files:
# Files underneath configuration/ will be copied into the build preserving the
# subdirectory structure if they exist.
data_files = []
for root, dirs, files in os.walk("configuration"):
    data_files.append(
        (os.path.relpath(root, "configuration"), [os.path.join(root, f) for f in files])
    )

with open("README.md", "r") as fh:
    long_description = fh.read()

AMZN_PACKAGE_NAME_PREFIX = os.environ.get("AMZN_PACKAGE_NAME_PREFIX", "")


class CondaCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        pass


setup(
    name=f"{AMZN_PACKAGE_NAME_PREFIX}sagemaker_studio_cli",
    version=VERSION,
    author="Amazon Web Services",
    description="CLI to interact with SageMaker Studio",
    url="https://aws.amazon.com/sagemaker/",
    long_description=long_description,
    long_description_content_type="text/markdown",
    data_files=data_files,
    packages=find_packages(),
    package_dir={"": "src"},
    package_data={
        "sagemaker_studio_cli": ["install.sh", "test/*"],
    },
    cmdclass={
        "conda": CondaCommand,
    },
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=["click>=8.1.3", f"{AMZN_PACKAGE_NAME_PREFIX}sagemaker_studio>=1.0.0"],
    license="Apache License 2.0",
    entry_points={
        "console_scripts": [
            "sagemaker-studio=sagemaker_studio_cli:sagemaker_studio",
        ],
    },
    platforms="Linux, Mac OS X, Windows",
    keywords=["AWS", "Amazon", "SageMaker", "SageMaker Unified Studio", "CLI"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: Apache Software License",
    ],
    test_suite="src.sagemaker_studio_cli._test",
    tests_require=["pytest"],
    extras_require={
        "test": ["pytest", "pytest-cov", "toml", "coverage"],
        "dev": ["wheel", "invoke", "twine"],
    },
)
