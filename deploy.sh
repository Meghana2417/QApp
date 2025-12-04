#!/bin/bash

cd /home/ubuntu/QApp
source venv/bin/activate

pip install -r requirements.txt
pip install gunicorn

sudo systemctl restart qapp
sudo systemctl restart nginx
