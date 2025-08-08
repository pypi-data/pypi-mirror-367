#!/usr/bin/env bash

set -eux

uv export --no-editable --no-emit-project > resources/docker_dev/requirements.txt
docker compose build