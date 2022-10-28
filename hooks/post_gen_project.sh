#!/bin/sh
set -e


remove_db_files() {
    rm -f src/{{ cookiecutter.__project_slug }}/models.py
    rm -f alembic.ini
    rm -fr alembic/
}

format() {
    black -q .
    isort .
}

next_steps() {
    echo
    echo "{{ cookiecutter.project_name }} is ready."
    echo "Now, create and activate a virtual environment, and run ./scripts/bootstrap.sh"
    echo
}

main() {
{%- if cookiecutter.use_db == "n" %}
    remove_db_files
{%- endif %}

    format
    next_steps
}
main
