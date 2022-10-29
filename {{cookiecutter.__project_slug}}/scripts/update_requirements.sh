#!/bin/sh
set -e

if [ $# -lt 1 ]
then
    echo "Please, provide at least one package to update"
    exit 1
    fi


AWK_UPGRADE_ARGS=$(cat <<'EOS'
{
    for(k=1; k<=NF; k++) {
        printf "--upgrade-package \"%s\" ",$k
    }
}
EOS
)

REQUIREMENTS_DIR="requirements"

PIP_COMPILE_UPGRADE_ARGS=$(echo "$@" | awk "${AWK_UPGRADE_ARGS}")
PIP_COMPILE_ARGS="--no-header --generate-hashes --allow-unsafe ${PIP_COMPILE_UPGRADE_ARGS}"
PIP_COMPILE_EXTRAS="dev"


echo "${PIP_COMPILE_ARGS}" | xargs pip-compile --output-file "${REQUIREMENTS_DIR}/requirements.txt"

for EXTRA in ${PIP_COMPILE_EXTRAS}
do
    echo "${PIP_COMPILE_ARGS}" | xargs pip-compile --extra "${EXTRA}" --output-file "${REQUIREMENTS_DIR}/${EXTRA}.txt"
done
