#!/usr/bin/env bash
set -e

docker-compose build
docker-compose up -d db
sleep 2
docker-compose run log_service populate_db.py

docker-compose run log_service -m pytest . -s
