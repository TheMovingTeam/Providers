#!/usr/bin/env bash

if [ "$#" -lt 1 ]; then
    echo ""
    echo "Please run one of the following options"
    echo "    -s for setting up the Python venv"
    echo "    -r for running all the scripts"
    exit 1
fi

if [[ "$1" == "-s" ]]; then
    python -m venv .venv
    source ./.venv/bin/activate
    pip install -r ./requirements.txt
    exit 0
fi

if [[ "$1" == "-r" ]]; then
    source ./.venv/bin/activate
    for i in *.py; do
        [ -f "$i" ] || break
        python $i &
    done
    wait
    exit 0
fi
