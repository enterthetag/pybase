import pytest

from . import create_package, delete_package, run_from


@pytest.fixture
def context():
    return {
        "full_name": "John Doe",
        "email": "johndoe@domain.tld",
        "project_name": "Test Package",
        "version": "22.2.11",
    }


@pytest.fixture
def package(context, tmp_path):
    """
    Create a new package, in a temporary directory, given the configuration
    given by the "context" fixture. Once done, clean it up.
    """

    package = create_package(target=tmp_path, **context)
    yield package
    delete_package(package)


@pytest.fixture(autouse=True)
def run_from_package(package):
    """
    By default, all tests will run with the package as their working directory.
    """

    with run_from(package.package):
        yield
