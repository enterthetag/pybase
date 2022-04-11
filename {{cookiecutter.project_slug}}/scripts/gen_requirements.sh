#!/bin/sh
set -e

pip-compile --no-header --generate-hashes --allow-unsafe --output-file requirements/requirements.txt
pip-compile --no-header --generate-hashes --allow-unsafe --extra dev --output-file requirements/dev.txt
