#!/bin/bash

git fetch
git pull
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py