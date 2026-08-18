#!/bin/bash
/usr/local/bin/mise trust /workspaces/laf-inference/mise.toml && /usr/local/bin/mise install
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
