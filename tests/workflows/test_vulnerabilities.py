import subprocess

import pytest

from .. import (
    add_and_install_dependency,
    run_cmd,
    run_from,
    update_and_install_dependency,
)


@pytest.fixture
def package(package):
    """
    cryptography<3.3.2 contains this vulnerability ID:
    - cryptography<3.3.2
    - PYSEC-2021-63
    - CVE-2020-36242
    - GHSA-rhm9-p9w5-fwm7
    """

    with run_from(package.package):
        add_and_install_dependency("cryptography==3.3.1", package)

    yield package


def test_update_vulnerable_package(package):
    with pytest.raises(subprocess.CalledProcessError) as error:
        run_cmd("./scripts/run_audit.sh", venv=package.venv)

    assert error.value.returncode == 1

    assert b"cryptography" in error.value.stdout  # Vulnerable package.
    assert b"PYSEC-2021-63" in error.value.stdout  # Vulnerability ID.
    assert b"3.3.2" in error.value.stdout  # Fix version.

    update_and_install_dependency(
        "cryptography==3.3.1",
        "cryptography>3.3.2",
        package,
    )

    result = run_cmd("./scripts/run_audit.sh", venv=package.venv)

    assert result.returncode == 0


def test_ignore_vulnerable_package(package):
    with pytest.raises(subprocess.CalledProcessError) as error:
        run_cmd("./scripts/run_audit.sh", venv=package.venv)

    assert error.value.returncode == 1

    assert b"cryptography" in error.value.stdout  # Vulnerable package.
    assert b"PYSEC-2021-63" in error.value.stdout  # Vulnerability ID.
    assert b"3.3.2" in error.value.stdout  # Fix version.

    with open(".audit-ignore", "w") as f:
        f.write("PYSEC-2021-63\n")

    result = run_cmd("./scripts/run_audit.sh", venv=package.venv)

    assert result.returncode == 0
