#!/bin/sh
set -e

AWK_IGNORE_ARGS=$(cat <<'EOS'
{
    for(k=1; k<=NF; k++) {
        printf "--ignore-vuln %s ",$k
    }
}
EOS
)

IGNORE_FILE=.audit-ignore
REQUIREMENTS=requirements/requirements.txt

PIP_AUDIT_ARGS="--strict --require-hashes --skip-editable"

if [ -s "${IGNORE_FILE}" ]
then
    PIP_AUDIT_IGNORE=$(awk "${AWK_IGNORE_ARGS}" "${IGNORE_FILE}")
    PIP_AUDIT_ARGS="${PIP_AUDIT_ARGS} ${PIP_AUDIT_IGNORE}"
fi


pip-audit ${PIP_AUDIT_ARGS} -r "${REQUIREMENTS}"
