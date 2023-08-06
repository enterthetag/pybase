import pathlib
import subprocess

import pytest

from .. import add_and_install_dependency, run_cmd, run_from


@pytest.fixture
def package(package):
    """
    pylint is GLPv2-licensed.
    It depends on astroid, LGPLv2-licensed.
    """

    with run_from(package.package):
        add_and_install_dependency("pylint", package)

    yield package


def test_bad_license_package(package):
    """
    Workflow under test:

    - Create a package, including dependencies with non-whitelisted licenses.
    - Run the license audit script, from tox, so only the install dependencies
      are present. It should fail, reporting the non-whitelisted licenses, and
      the packages attached to them.
    - Add the affected licenses to the whitelist.
    - Run the license audit script again. It should now succeed.
    """

    with pytest.raises(subprocess.CalledProcessError) as error:
        run_cmd("tox", "-e", "licenses", venv=package.venv)

    assert error.value.returncode == 1

    with open(".license-whitelist", "a") as f:
        f.write("GNU General Public License v2 (GPLv2)\n")
        f.write("GNU Lesser General Public License v2 (LGPLv2)\n")

    result = run_cmd("tox", "-e", "licenses", venv=package.venv)

    assert result.returncode == 0


def test_missing_license_whitelist(package):
    """
    Workflow under test:

    - Create a package, including dependencies with non-whitelisted licenses.
    - Remove the license whitelist file.
    - Run the license audit script, from tox, so only the install dependencies
      are present. It should fail, reporting the lack of a whitelist file.
    """

    pathlib.Path(".license-whitelist").unlink()

    with pytest.raises(subprocess.CalledProcessError) as error:
        run_cmd("tox", "-e", "licenses", venv=package.venv)

    assert error.value.returncode == 1
    assert (
        b"license-whitelist: License whitelist not found, or found empty"
    ) in error.value.stdout
