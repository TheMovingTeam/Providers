#!/usr/bin/env bash

if grep -q "NAME=NixOS" /etc/os-release ; then
    nix-shell -p python3Packages.requests python3Packages.jsonpath-ng python3Packages.xmltodict --run "python ./*.py"
else
    python ./*.py
fi

