#!/usr/bin/env bash

CONFIG=$1
GPUS=$2

PORT=${PORT:-29511}

PYTHONPATH="$(dirname $0)/..":$PYTHONPATH \
python3.9 -m torch.distributed.run --nproc_per_node=$GPUS --master_port=$PORT \
    $(dirname "$0")/train.py $CONFIG --launcher pytorch ${@:3}