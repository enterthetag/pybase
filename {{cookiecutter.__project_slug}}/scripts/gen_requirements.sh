#!/bin/sh
set -e

REQUIREMENTS_DIR="requirements"

PIP_COMPILE_ARGS="--no-header --generate-hashes --allow-unsafe"
PIP_COMPILE_EXTRAS="dev"


pip-compile ${PIP_COMPILE_ARGS} --output-file "${REQUIREMENTS_DIR}/requirements.txt"

for EXTRA in ${PIP_COMPILE_EXTRAS}
do
    pip-compile ${PIP_COMPILE_ARGS} --extra "${EXTRA}" --output-file "${REQUIREMENTS_DIR}/${EXTRA}.txt"
done
