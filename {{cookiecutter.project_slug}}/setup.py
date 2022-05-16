from setuptools import find_packages, setup

setup(
    name="{{ cookiecutter.project_slug }}",
    version="{{ cookiecutter.version }}",
    author="{{ cookiecutter.full_name }}",
    author_email="{{ cookiecutter.email }}",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "attrs>=20.2",
        "zope.interface>=5.0",
        "mypy-zope>=0.3.3",
{%- if cookiecutter.use_trio == "y" %}
        "trio>=0.19",
        "trio-typing>=0.7",
{%- endif %}
{%- if cookiecutter.use_db == "y" %}
        "alembic>=1.7",
        "psycopg2-binary",
        "SQLAlchemy>=1.4",
        "sqlalchemy2-stubs",
{%- endif %}
    ],
    extras_require={
        "dev": [
            "bandit",
            "black>=22.1",
            "coverage[toml]",
            "flake8",
            "flake8-bugbear",
            "hypothesis",
            "isort>=5.0",
            "mypy>=0.920",
            "pip-audit",
            "pylint",
            "pytest>=6.0",
            "pytest-cov",
            "tox",
{%- if cookiecutter.use_trio == "y" %}
            "pytest-trio>=0.7",
{%- endif %}
        ],
    },
    python_requires=">=3.9",
    zip_safe=False,
)
