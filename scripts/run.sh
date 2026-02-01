#!/usr/bin/env bash

usage() {
    echo "Please run one of the following options"
    echo "    -s for setting up the Python venv"
    echo "    -r for running all the scripts"
}

setup() {
    python -m venv .venv
    source ./.venv/bin/activate
    pip install -r ./requirements.txt
    exit 0
}

run() {
    source ./.venv/bin/activate
    for i in *.py; do
        [ -f "$i" ] || break
        ghostty -e python $i &
    done
    wait
    exit 0
}

main() {
    local opt OPTIND OPTARG
    while getopts 'rsh' opt; do
        case $opt in
            r) run ;;
            s) setup ;;
            h) usage ; return 0;;
            *) usage >&2; return 1;;
        esac
    done
    shift "$((OPTIND - 1))"

    "$@"
}

main "$@"
