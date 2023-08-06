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
    cryptography<3.3.2 contains this vulnerability IDs:

    - PYSEC-2021-63
    - CVE-2020-36242
    - GHSA-rhm9-p9w5-fwm7

    - CVE-2023-0286
    - GHSA-x4qr-2fvf-3mr5

    - CVE-2023-23931
    - GHSA-w7pp-m8wf-vj6r
    """

    with run_from(package.package):
        add_and_install_dependency("cryptography==3.3.1", package)

    yield package


def test_update_vulnerable_package(package):
    """
    Workflow under test:

    - Create a package, including a vulnerable package.
    - Run the pip-audit script. It should fail, pointing at the vulnerability.
    - Update the affected package to a version fixing the vulnerability.
    - Run the pip-audit script again. It should now succeed, reporting no
      vulnerabilities.

    Keep in mind the way this workflow has been implemented differs a little
    bit from what it would look like in practice. Since installing a vulnerable
    package can be challenging, we force a specific version via an exact
    version specifier in setup.py. This would not happen in reality, as the
    vulnerable version would just be in the pinned requirements (remember using
    exact version specifiers in setup.py tends to be frowned upon, as it can
    complicate deployment). In any real-world setting we'd just run the
    dependency upgrade script (scripts/update_requirements.sh), and pip-sync.
    """

    with pytest.raises(subprocess.CalledProcessError) as error:
        run_cmd("./scripts/run_audit.sh", venv=package.venv)

    assert error.value.returncode == 1

    assert b"cryptography" in error.value.stdout  # Vulnerable package.
    assert b"PYSEC-2021-63" in error.value.stdout  # Vulnerability ID.
    assert b"GHSA-x4qr-2fvf-3mr5" in error.value.stdout  # Vulnerability ID.
    assert b"GHSA-w7pp-m8wf-vj6r" in error.value.stdout  # Vulnerability ID.
    assert b"3.3.2" in error.value.stdout  # Fix version.

    update_and_install_dependency(
        "cryptography==3.3.1",
        "cryptography>3.3.2",
        package,
    )

    result = run_cmd("./scripts/run_audit.sh", venv=package.venv)

    assert result.returncode == 0


@pytest.mark.xfail(reason="pip-audit seems to have changed return codes")
def test_ignore_vulnerable_package(package):
    """
    Workflow under test:

    - Create a package, including a vulnerable package.
    - Run the pip-audit script. It should fail, pointing at the vulnerability.
    - Add the vulnerability to the whitelist of IDs to ignore.
    - Run the pip-audit script again. It should succeed, reporting no
      vulnerabilities.
    """

    with pytest.raises(subprocess.CalledProcessError) as error:
        run_cmd("./scripts/run_audit.sh", venv=package.venv)

    assert error.value.returncode == 1

    assert b"cryptography" in error.value.stdout  # Vulnerable package.
    assert b"PYSEC-2021-63" in error.value.stdout  # Vulnerability ID.
    assert b"GHSA-x4qr-2fvf-3mr5" in error.value.stdout  # Vulnerability ID.
    assert b"GHSA-w7pp-m8wf-vj6r" in error.value.stdout  # Vulnerability ID.
    assert b"3.3.2" in error.value.stdout  # Fix version.

    with open(".audit-ignore", "w") as f:
        f.write("PYSEC-2021-63\n")
        f.write("GHSA-x4qr-2fvf-3mr5\n")
        f.write("GHSA-w7pp-m8wf-vj6r\n")

    run_cmd("./scripts/run_audit.sh", venv=package.venv)

    assert b"PYSEC-2021-63" not in error.value.stdout
    assert b"GHSA-x4qr-2fvf-3mr5" not in error.value.stdout
    assert b"GHSA-w7pp-m8wf-vj6r" not in error.value.stdout
