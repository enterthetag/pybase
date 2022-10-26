#!/bin/sh
set -e

pip-compile --no-header --generate-hashes --output-file requirements/requirements.txt
pip-compile --no-header --generate-hashes --extra dev --output-file requirements/dev.txt
