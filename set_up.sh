#!/bin/bash

virtualenv --no-site-packages env
mkdir static; mkdir templates
source env/bin/activate
pip install -r requirements.txt 
