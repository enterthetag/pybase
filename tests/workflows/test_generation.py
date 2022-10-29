import pytest

from .. import get_dependencies, get_meta


class TestPackageGeneration:
    FILES = (
        ".editorconfig",
        ".flake8",
        ".gitignore",
        ".license-whitelist",
        ".vscode/settings.json",
        "LICENSE",
        "pyproject.toml",
        "setup.py",
        "tox.ini",
        "requirements/requirements.txt",
        "requirements/dev.txt",
        "scripts/gen_requirements.sh",
        "scripts/run_audit.sh",
        "scripts/run_license_check.sh",
        "scripts/update_requirements.sh",
        "src/test_package/__init__.py",
        "tests/test_void.py",
    )

    def check_files(self, package):
        for file in self.FILES:
            file_path = package.package / file

            assert file_path.exists() and file_path.is_file()

    def check_bootstrap(self, package):
        # The bootstrap script is gone after it's run.
        bootstrap_script = package.package / "scripts/bootstrap.sh"

        assert not bootstrap_script.exists()

    def check_meta(self, package):
        meta = get_meta(package)

        assert meta == {
            "name": "test_package",
            "version": "22.2.11",
            "author": "John Doe",
            "author_email": "johndoe@domain.tld",
        }

    def check_dependencies(self, package):
        dependencies = get_dependencies(package)

        assert dependencies == {
            "install": [
                "attrs>=20.2",
                "zope.interface>=5.0",
                "mypy-zope>=0.3.3",
            ],
            "extras": {
                "dev": [
                    "bandit",
                    "black>=22.1",
                    "coverage[toml]>=5.0",
                    "flake8",
                    "flake8-bugbear",
                    "hypothesis>=6.0",
                    "isort>=5.0",
                    "mypy>=0.920",
                    "pip-audit",
                    "pylint",
                    "pytest>=6.0",
                    "pytest-cov>=3.0",
                    "tox",
                ],
            },
        }

    def check_requirements_files(self, package):
        requirements_files = (
            package.package / "requirements/requirements.txt",
            package.package / "requirements/dev.txt",
        )

        for file in requirements_files:
            assert file.exists() and file.is_file() and file.stat().st_size > 0

    def test_generated_package(self, package):
        self.check_files(package)
        self.check_bootstrap(package)
        self.check_meta(package)
        self.check_dependencies(package)
        self.check_requirements_files(package)


class TestDBPackageGeneration(TestPackageGeneration):
    FILES = (
        *TestPackageGeneration.FILES,
        "alembic.ini",
        "alembic/README",
        "alembic/env.py",
        "alembic/script.py.mako",
        "alembic/versions/.gitkeep",
        "src/test_package/models.py",
    )

    @pytest.fixture
    def context(self, context):
        return {
            **context,
            "use_db": "y",
        }

    def check_dependencies(self, package):
        dependencies = get_dependencies(package)

        assert dependencies == {
            "install": [
                "attrs>=20.2",
                "zope.interface>=5.0",
                "mypy-zope>=0.3.3",
                "alembic>=1.7",
                "psycopg2-binary",
                "SQLAlchemy>=1.4",
                "sqlalchemy2-stubs",
            ],
            "extras": {
                "dev": [
                    "bandit",
                    "black>=22.1",
                    "coverage[toml]>=5.0",
                    "flake8",
                    "flake8-bugbear",
                    "hypothesis>=6.0",
                    "isort>=5.0",
                    "mypy>=0.920",
                    "pip-audit",
                    "pylint",
                    "pytest>=6.0",
                    "pytest-cov>=3.0",
                    "tox",
                ],
            },
        }


class TestTrioPackageGeneration(TestPackageGeneration):
    @pytest.fixture
    def context(self, context):
        return {
            **context,
            "use_trio": "y",
        }

    def check_dependencies(self, package):
        dependencies = get_dependencies(package)

        assert dependencies == {
            "install": [
                "attrs>=20.2",
                "zope.interface>=5.0",
                "mypy-zope>=0.3.3",
                "trio>=0.19",
                "trio-typing>=0.7",
            ],
            "extras": {
                "dev": [
                    "bandit",
                    "black>=22.1",
                    "coverage[toml]>=5.0",
                    "flake8",
                    "flake8-bugbear",
                    "hypothesis>=6.0",
                    "isort>=5.0",
                    "mypy>=0.920",
                    "pip-audit",
                    "pylint",
                    "pytest>=6.0",
                    "pytest-cov>=3.0",
                    "tox",
                    "pytest-trio>=0.7",
                ],
            },
        }
