#!/bin/sh
set -e

WHITELIST_FILE=".license-whitelist"
IGNORE_LIST="{{ cookiecutter.package_name }} pkg-resources"

if [ -s ${WHITELIST_FILE} ]
then
    WHITELIST=$(awk '{printf "%s;",$0}' ${WHITELIST_FILE})

    pip install -U pip-licenses
    pip-licenses \
        --ignore-packages ${IGNORE_LIST} \
        --allow-only="${WHITELIST}"
else
    echo "${WHITELIST_FILE}: License whitelist not found, or found empty"
    exit 1
fi
