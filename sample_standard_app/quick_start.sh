#!/bin/sh

# Ignore broken pipe errors
trap '' PIPE

# Check if Python is installed, if not, install it
if ! command -v python &> /dev/null; then
    echo "Python is not installed. Installing Python..."
    # Check if conda is installed
    if ! command -v conda &> /dev/null; then
        echo "conda is not installed. Installing conda..."
        mkdir -p ~/miniconda3
        # If on macOS
        if [[ "$(uname)" == "Darwin" ]]; then
            curl https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh -o ~/miniconda3/miniconda.sh
        else
            curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o ~/miniconda3/miniconda.sh
        fi
        bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
        # 配置conda环境变量
        echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bashrc
        rm -rf ~/miniconda3/miniconda.sh
        # Configure Tsinghua mirrors
        conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
        conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
        conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
        conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/
    fi
    # Create and activate Python 3.10 environment
    conda create -n python_au3.10 python=3.10 -y
    conda activate python_au3.10
fi

# Install missing packages
if ! pip list | grep -q "agentUniverse"; then
    echo "agentUniverse is not installed. Installing agentUniverse..."
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
python server_application.py
