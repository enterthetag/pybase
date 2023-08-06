import pytest

from .. import get_dependencies, get_meta


class TestPackageGeneration:
    """
    Class to encapsulate package generation checks.

    It's a bit funny-looking, but there's a reason for that. They way the test
    suite is structured, the "package" fixture, which creates a new Cookiecut
    Python package, is function-scoped. This means each test function has its
    very own Package, so they are free to perform, whichever workflows they
    happen to be testing.

    Package generation needs to check quite a few things. We could check them
    in separate test functions, but that would mean a mean amount of packages
    being created, slowing the whole things down. We could mess with different
    fixture scopes, but that almost invariably ends up looking nasty. Instead,
    we isolate the checks in non-test methods, and just call them, one after
    the other, in the actual test.

    A good side effect of this structure is that we can sub-class, to create
    different package variations, and only override the checks which are
    actually different.
    """

    FILES = (
        ".editorconfig",
        ".flake8",
        ".gitignore",
        ".license-whitelist",
        ".vscode/settings.json",
        "LICENSE",
        "pyproject.toml",
        "Rakefile",
        "setup.py",
        "tox.ini",
        "VERSION",
        "requirements/requirements.txt",
        "requirements/dev.txt",
        "scripts/gen_requirements.sh",
        "scripts/run_audit.sh",
        "scripts/run_license_check.sh",
        "scripts/update_requirements.sh",
        "src/test_package/__init__.py",
        "tests/test_void.py",
    )
    """
    File list we expect the package to include.
    """

    def check_files(self, package):
        """
        Check all the files listed in self.FILES exist, and are regular files.

        Args:
            package (Package): The package to check.
        Raises:
            AssertionError: If the files do not exist, or are not files.
        """

        for file in self.FILES:
            file_path = package.package / file

            assert file_path.exists() and file_path.is_file()

    def check_bootstrap(self, package):
        """
        Check the boostrap script cleaned up after itself.

        Args:
            package (Package): The package to check.
        Raises:
            AssertionError: If the bootstrap script is still present.
        """

        # The bootstrap script is gone after it's run.
        bootstrap_script = package.package / "scripts/bootstrap.sh"

        assert not bootstrap_script.exists()

    def check_meta(self, package):
        """
        Check the setup.py information matches the context provided.

        Args:
            package (Package): The package to check.
        Raises:
            AssertionError: If the setup.py information does not match.
        """

        meta = get_meta(package)

        assert meta == {
            "name": "test_package",
            "version": "22.2.11",
            "author": "John Doe",
            "author_email": "johndoe@domain.tld",
        }

    def check_dependencies(self, package):
        """
        Check the setup.py dependency information matches what we expect.

        Args:
            package (Package): The package to check.
        Raises:
            AssertionError: If the setup.py dependencies do not match.
        """

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
                ],
            },
        }

    def check_requirements_files(self, package):
        """
        Check the pinned requirements files, created by pip-tools, exist and
        are not empty.

        Args:
            package (Package): The package to check.
        Raises:
            AssertionError: If the files do not exist, or are empty.
        """

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
    """
    File list we expect the package to include.
    """

    @pytest.fixture
    def context(self, context):
        """
        Create a DB-enabled package.
        """

        return {
            **context,
            "use_db": "y",
        }

    def check_dependencies(self, package):
        """
        The dependency check is different, as it needs to include DB-specific
        packages.
        """

        dependencies = get_dependencies(package)

        assert dependencies == {
            "install": [
                "attrs>=20.2",
                "zope.interface>=5.0",
                "mypy-zope>=0.3.3",
                "alembic>=1.7",
                "psycopg2-binary",
                "sqlalchemy[mypy]>=2.0",
            ],
            "extras": {
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
                ],
            },
        }


class TestTrioPackageGeneration(TestPackageGeneration):
    @pytest.fixture
    def context(self, context):
        """
        Create an async-enabled package.
        """

        return {
            **context,
            "use_trio": "y",
        }

    def check_dependencies(self, package):
        """
        The dependency check is different, as it needs to include Trio-specific
        packages.
        """

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
                    "pytest-trio>=0.7",
                ],
            },
        }
