#!/bin/bash

set -euo pipefail

exec hypercorn --config=hypercorn.toml --keyfile=selfsigned.key  \
    --certfile=selfsigned.crt --root-path=${ROOT_PATH} transfer.main:app
