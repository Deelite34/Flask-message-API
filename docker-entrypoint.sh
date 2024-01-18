#!/bin/bash
set -e
# https://github.com/sudo-bmitch/docker-base/blob/f1b7e1a775d41d93b354037f193c2dcc8946ee34/bin/entrypointd.sh#L66
# Handle a kill signal before the final "exec" command runs
# Without this, docker would take 10s to shut down flask container
trap "{ exit 0; }" TERM INT

umask 0000

flask db upgrade

exec flask --app app run --debug --port 5000 --host 0.0.0.0