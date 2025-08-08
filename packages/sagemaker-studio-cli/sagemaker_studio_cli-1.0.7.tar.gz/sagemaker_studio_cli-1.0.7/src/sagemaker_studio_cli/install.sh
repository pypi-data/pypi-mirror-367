#!/bin/bash

# Install the package
pip install -e .

# Get the installation path
CLI_PATH=$(which sagemaker_studio_cli)
CLI_DIR=$(dirname "$CLI_PATH")

# Check if the path is already in .zshrc
if grep -q "$CLI_DIR" ~/.zshrc; then
    echo "Path already in .zshrc"
else
    # Add the path to .zshrc
    echo "export PATH=\"$CLI_DIR:\$PATH\"" >> ~/.zshrc
    echo "Path added to .zshrc"
fi

# Source .zshrc
source ~/.zshrc

echo "Installation complete. You can now use 'sagemaker-studio' from anywhere."
echo "Please restart your terminal or run 'source ~/.zshrc' to apply the changes."
