#!/bin/bash
docker stop qapp || true
docker rm qapp || true

docker build -t qapp:latest .

docker run -d \
  --name qapp \
  -p 8000:8000 \
  --env-file .env \
  qapp:latest

