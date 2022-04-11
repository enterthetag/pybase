# Python project boilerplate.

This template creates a bare-bones Python project, using my conventions and
standards.

## Requirements.

This template requires:

* [Cookiecutter](https://cookiecutter.readthedocs.io).
* [Black](https://black.readthedocs.io).
* [isort](https://pycqa.github.io/isort/).

## Project creation.

Then, create the project from the template:

```sh
$ cookiecutter gh:enterthetag/pybase
```

Two variants are available:

* [Trio](https://trio.readthedocs.io): Async-enabled, including Trio support for pytest and mypy.
* DB: Includes an ergonomic [SQLAlchemy](https://www.sqlalchemy.org) declarative base, and [Alembic](https://alembic.sqlalchemy.org) configured to use [Postgres](https://www.postgresql.org).

Further instructions will be displayed after successful project creation. The
`bootstrap.sh` script should take care of most post-creation tasks, and it will
clean itself up once done.
