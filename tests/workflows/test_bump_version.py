from .. import (
    get_bumpver_info,
    get_current_version,
    get_license_year,
    get_meta,
    run_cmd,
)


def test_bump_version(package):
    """
    Workflow under test:

    - Create a package, and check the version declared is what we expect.
    - Perform a version bump.
    - Check the new version matches what BumpVer thinks it should be.

    When checking the package version, we look into all the places we've told
    BumpVer to keep version information:

    - setup.py, in the version field.
    - src/<package_slug>/__init__.py:__version__, for Python consumers.
    - VERSION, for non-Python consumers.

    We also keep the LICENSE year updated.
    """

    old_meta = get_meta(package)
    old_version = get_current_version()
    old_license_year = get_license_year()

    assert old_version == "22.2.11"
    assert old_meta["version"] == "22.2.11"
    assert old_license_year == "2022"

    run_cmd("bumpver", "update", "--patch", venv=package.venv)

    bumpver_info = get_bumpver_info(package)
    bumpver_year = bumpver_info["YEAR_Y"]
    bumpver_version = bumpver_info["CURRENT_VERSION"]

    new_meta = get_meta(package)
    new_version = get_current_version()
    new_license_year = get_license_year()

    assert new_version == bumpver_version
    assert new_meta["version"] == bumpver_version
    assert new_license_year == bumpver_year
