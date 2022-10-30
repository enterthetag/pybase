import ast
import contextlib
import copy
import dataclasses
import os
import pathlib
import re
import shlex
import shutil
import subprocess
import venv

from cookiecutter.main import cookiecutter

PACKAGE_DIR = "test_package"
VENV_DIR = "package_venv"


@dataclasses.dataclass
class Package:
    package: pathlib.Path
    venv: pathlib.Path


@contextlib.contextmanager
def run_from(path):
    """
    Context manager to run code from a given path.

    When done, go back to the original working directory.

    Virtually none of the functions defined in this file call this, so the
    caller is expected to run them from a run_from() context. In practice, the
    test suite does that for you, via an autouse fixture.

    Args:
        path (str | pathlib.Path): Path to run from.
    """

    original_path = pathlib.Path.cwd().resolve()
    target_path = pathlib.Path(path).resolve()

    os.chdir(target_path)
    yield
    os.chdir(original_path)


def run_cmd(cmd, *args, venv=None):
    """
    Run the given command, with the provided arguments, optionally from a
    specific virtual environment.

    Runs the command using subprocess.run(), in check and capture mode: all
    process output is stored, and it will raise on non-zero exit code.

    Args:
        cmd (str): Command to run.
        args (list[str]): Arguments to pass to the command.
        venv (str | pathlib.Path, optional): Virtual environment to run the
                                             command from. Defaults to None.

    Returns:
        subprocess.CompletedProcess: The return value from subprocess.run(),
                                     representing a process that has finished.

    Raises:
        subprocess.CalledProcessError: Exception holding the arguments, the
                                       exit code, stdout and stderr.
    """

    command = shlex.join([cmd, *args])
    environment = copy.deepcopy(os.environ)

    if venv:
        venv_bin = pathlib.Path(venv).resolve() / "bin"
        environment["PATH"] = ":".join(
            [
                str(venv_bin),
                *environment["PATH"].split(":"),
            ]
        )

    return subprocess.run(
        command,
        env=environment,
        check=True,
        shell=True,
        capture_output=True,
    )


def delete_package(package):
    """
    Delete a previously created Python package, and its associated virtual
    environment.

    Args:
        package (Package): Package to delete.
    """

    shutil.rmtree(package.package, ignore_errors=True)
    shutil.rmtree(package.venv, ignore_errors=True)


def create_package(target, **context):
    """
    Create a Cookiecut Python package.

    Performs the following steps:

    - Ensure the target is empty.
    - Call Cookiecutter, with the provided context, to create the package.
    - Create a virtual environment.
    - Run the bootstrap script.

    Args:
        target (str | pathlib.Path): Directory where the package and virtual
                                     environment will be created.
        context (dict[str, str]): Context to provide to Cookiecutter on package
                                  creation.

    Returns:
        Package: Structure containing the location of the package and its
                 associated virtual environment.
    """

    target_loc = pathlib.Path(target).resolve()
    package = Package(
        package=target_loc / PACKAGE_DIR,
        venv=target_loc / VENV_DIR,
    )

    delete_package(package)

    cookiecutter_path = pathlib.Path(__file__).parent.parent
    cookiecutter(
        str(cookiecutter_path),
        output_dir=target,
        no_input=True,
        extra_context=context,
    )

    virtualenv = venv.EnvBuilder(clear=True, with_pip=True, upgrade_deps=True)
    virtualenv.create(package.venv)

    with run_from(package.package):
        run_cmd("./scripts/bootstrap.sh", venv=package.venv)

    return package


def gen_requirements(package):
    """
    Generate the pinned requirements files, with pip-tools.

    Args:
        package (Package): The target package.
    """

    run_cmd("./scripts/gen_requirements.sh", venv=package.venv)


def install_dev_requirements(package):
    """
    Install all package development requirements.

    Installs:

    - All pinned requirements defined in requirements/dev.txt.
    - The package itself, in editable mode.

    Args:
        package (Package): The target package.
    """

    run_cmd("pip-sync", "requirements/dev.txt", venv=package.venv)
    run_cmd("pip", "install", "-e", ".[dev]", venv=package.venv)


def add_dependency(dependency, package):
    """
    Declare a new dependency for a package.

    Parses setup.py and appends a new dependency to "install_requires",
    using a subclass of ast.NodeTransformer.

    Args:
        dependency (str): Dependency to add, following PEP-440.
        package (Package): The target package.
    """

    class DependencyAdder(ast.NodeTransformer):
        def visit_keyword(self, node):
            if node.arg == "install_requires":
                return ast.keyword(
                    arg=node.arg,
                    value=ast.List(
                        elts=[
                            *node.value.elts,
                            ast.Constant(value=dependency),
                        ],
                        ctx=node.value.ctx,
                    ),
                )

            return node

    setup_path = package.package / "setup.py"

    with open(setup_path, "r") as setup_file:
        setup = ast.parse(setup_file.read())
        new_setup = ast.fix_missing_locations(DependencyAdder().visit(setup))

    with open(setup_path, "w") as setup_file:
        setup_file.write(ast.unparse(new_setup))


def update_dependency(old, new, package):
    """
    Declare an updated dependency for a package.

    Parses setup.py, looks for the old dependency in "install_requires", and
    replaces it with the new version.

    Args:
        old (str): Dependency to replace, following PEP-440.
        new (str): Dependency to replace with, following PEP-440.
        package (Package): The target package.
    """

    class DependencyUpdater(ast.NodeTransformer):
        def visit_keyword(self, node):
            if node.arg == "install_requires":
                new_deps = []
                for elt in node.value.elts:
                    if elt.value == old:
                        new_deps.append(ast.Constant(value=new))
                    else:
                        new_deps.append(elt)

                return ast.keyword(
                    arg=node.arg,
                    value=ast.List(
                        elts=new_deps,
                        ctx=node.value.ctx,
                    ),
                )

            return node

    setup_path = package.package / "setup.py"

    with open(setup_path, "r") as setup_file:
        setup = ast.parse(setup_file.read())
        new_setup = ast.fix_missing_locations(DependencyUpdater().visit(setup))

    with open(setup_path, "w") as setup_file:
        setup_file.write(ast.unparse(new_setup))


def add_and_install_dependency(dependency, package):
    """
    Declare and install a new dependency for a package.

    Performs the following steps:

    - Adds the new dependency to setup.py.
    - Regenerates the pinned requirements files, using pip-tools.
    - Installs the pinned development requirements, and the package, in
      editable mode.

    Args:
        dependency (str): Dependency to add, following PEP-440.
        package (Package): The target package.
    """

    add_dependency(dependency, package)
    gen_requirements(package)
    install_dev_requirements(package)


def update_and_install_dependency(old, new, package):
    """
    Declare and install an updated dependency for a package.

    Performs the following steps:

    - Updates the dependency in setup.py.
    - Regenerates the pinned requirements files, using pip-tools.
    - Installs the pinned development requirements, and the package, in
      editable mode.

    Args:
        old (str): Dependency to replace, following PEP-440.
        new (str): Dependency to replace with, following PEP-440.
        package (Package): The target package.
    """

    update_dependency(old, new, package)
    run_cmd("./scripts/update_requirements.sh", new, venv=package.venv)
    install_dev_requirements(package)


def get_meta(package):
    """
    Extract meta information from a package setup.py.

    Extracts the information from the call to setup(), using a subclass of
    ast.NodeVisitor. This roundabout way is meant to avoid the perils of
    importing setup.py.

    The keys it returns are:

    - name
    - version
    - author
    - author_email

    Args:
        package (Package): The target package.

    Returns:
        dict[str, str]: Information extracted from setup.py.
    """

    meta = {}

    class MetaVisitor(ast.NodeVisitor):
        def visit_keyword(self, node):
            if node.arg in ("name", "version", "author", "author_email"):
                meta[node.arg] = node.value.value

    setup_path = package.package / "setup.py"

    with open(setup_path, "r") as setup_file:
        setup = ast.parse(setup_file.read())
        MetaVisitor().visit(setup)

    return meta


def get_dependencies(package):
    """
    Extract dependency information from a package setup.py.

    Extracts the dependency lists from the call to setup(), using a subclass of
    ast.NodeVisitor. This roundabout way is meant to avoid the perils of
    importing setup.py.

    Returns a dictionary, with two keys:

    - install: A list of install dependencies, in PEP-440 format.
    - extras: A dictionary, with one key per extra. Each key points to a list,
              containing that particular extra dependencies, in PEP-440 format.

    Args:
        package (Package): The target package.

    Returns:
        dict[list[str], dict[str, list[str]]]: Dependency information extracted
                                               from setup.py.
    """

    dependencies = {
        "install": [],
        "extras": {},
    }

    class DependenciesVisitor(ast.NodeVisitor):
        def visit_keyword(self, node):
            if node.arg == "install_requires":
                deps = node.value.elts
                dependencies["install"] = [dep.value for dep in deps]

            if node.arg == "extras_require":
                groups = node.value

                for key, value in zip(groups.keys, groups.values):
                    name = key.value
                    deps = value.elts
                    dependencies["extras"][name] = [dep.value for dep in deps]

    setup_path = package.package / "setup.py"

    with open(setup_path, "r") as setup_file:
        setup = ast.parse(setup_file.read())
        DependenciesVisitor().visit(setup)

    return dependencies


def get_current_version():
    """
    Fetch the current package version.

    We make the version available from two places:

    - For Python code, a __version__ constant in the package top-most
      __init__.py.
    - For other consumers, a plain-text VERSION file.

    We retrieve both, ensure they contain the exact same information, and
    return the value.

    Returns:
        str: The current Python package version.
    """

    with open("src/test_package/__init__.py") as package_init:
        ns = {}
        exec(package_init.read(), ns)

        py_version = ns["__version__"]

    with open("VERSION", "r") as version_file:
        plaintext_version = version_file.read().strip()

    assert py_version == plaintext_version

    return py_version


def get_bumpver_info(package):
    """
    Get all information BumpVer holds.

    We fetch it in the form of a list of environment variables. The exact keys
    can be found in the official documentation:
    https://gitlab.com/mbarkhau/pycalver#command-line

    Args:
        package (Package): The target package.

    Returns:
        dict[str, str]: The information extracted from BumpVer.
    """

    result = run_cmd("bumpver", "show", "-ne", venv=package.venv)
    output = result.stdout.decode("utf-8").strip()

    return dict(line.split("=") for line in output.split("\n"))


def get_license_year():
    """
    Read the copyright year from the LICENSE file.

    Returns:
        str: The license year.
    """

    with open("LICENSE", "r") as license_file:
        license = license_file.read()

    match = re.match(r"^Copyright \(c\) (?P<year>\d{4})", license)

    return match.group("year")
