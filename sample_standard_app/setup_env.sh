#!/bin/bash

# Activate the conda environment
CONDA_PATH=$(conda info --base)
source $CONDA_PATH/etc/profile.d/conda.sh
conda activate python_au3.10

# Install dependencies using poetry
poetry install

# Set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:/Users/mac/Desktop/code-open/agentUniverse

echo "Environment setup complete!"
