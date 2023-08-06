from setuptools import find_packages, setup

setup(
    name="{{ cookiecutter.__project_slug }}",
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
        "sqlalchemy[mypy]>=2.0",
{%- endif %}
    ],
    extras_require={
        "dev": [
            "bandit",
            "bumpver>=2021.1109",
            "black>=22.1",
            "coverage[toml]>=5.0",
            "flake8",
            "flake8-bugbear",
            "hypothesis>=6.0",
            "isort>=5.0",
            "mypy>=0.920",
            "pdbpp",
            "pip-audit",
            "pylint",
            "pytest>=6.0",
            "pytest-cov>=3.0",
            "tox",
{%- if cookiecutter.use_trio == "y" %}
            "pytest-trio>=0.7",
{%- endif %}
        ],
    },
    python_requires=">=3.9",
    zip_safe=False,
)
