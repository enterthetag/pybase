#!/bin/sh
set -e

IGNORE_FILE=.audit-ignore
REQUIREMENTS=requirements/requirements.txt

pip-audit \
    --strict \
    --require-hashes \
    --skip-editable \
    -r "${REQUIREMENTS}" \
    $(test -s "${IGNORE_FILE}" && sed 's/^/--ignore-vuln /' "${IGNORE_FILE}")
