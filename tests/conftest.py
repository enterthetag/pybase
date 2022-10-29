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
    package = create_package(target=tmp_path, **context)
    yield package
    delete_package(package)


@pytest.fixture(autouse=True)
def run_from_package(package):
    with run_from(package.package):
        yield
