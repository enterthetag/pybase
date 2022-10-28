#!/bin/sh
set -e

prepare_requirements() {
    pip install -U setuptools wheel pip pip-tools
    ./scripts/gen_requirements.sh
}

install_dev_requirements() {
    pip-sync requirements/dev.txt
    pip install -e .
}

cleanup() {
    rm -f ./scripts/bootstrap.sh
}

main() {
    prepare_requirements
    install_dev_requirements
    cleanup
}
main
