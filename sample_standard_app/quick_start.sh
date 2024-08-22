#!/bin/bash

# 判断当前的python版本是否是3.10
if ! python --version | grep -q "3.10"; then
    echo "Error: Python version is not 3.10. Please install Python 3.10 and try again."
    exit 1
fi

# 判断 pip list 是否已安装 agentUniverse
if ! pip list | grep -q "agentUniverse"; then
   pip install agentUniverse
fi

# Check if custom_key file exists, if not, copy from sample
if [ ! -f "config/custom_key" ]; then
    cp config/custom_key.toml.sample config/custom_key.toml
fi

# Set PYTHONPATH to the parent directory of the current working directory
export PYTHONPATH=$PWD/../..

# Start the service
cd app/bootstrap
python -u server_application.py