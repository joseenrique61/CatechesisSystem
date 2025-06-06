#!/bin/bash

version=$(python --version)
if [[ $version != *"3.11.0" ]]; then
    echo "Python 3.11.0 needed"
    exit 1
else
    echo "Starting configuration"
fi

if [[ $VIRTUAL_ENV != "" ]]; then
    echo "Deactivating virtual environment"
    source "$VIRTUAL_ENV/Scripts/activate" 
    deactivate
fi

if [[ -d ".venv" ]]; then
    echo "Deleting .venv"
    rm -rf .venv
fi

echo "Creating new virtual environment"
python -m venv .venv
source .venv/Scripts/activate

echo "Installing packages"
pip install -r requirements.txt

echo "Creating .env"
cp env-template.txt .env

echo "Configuration completed"