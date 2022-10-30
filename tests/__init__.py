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
    Context manager to run code from a given path. When done, go back to the
    original working directory.
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
    """

    shutil.rmtree(package.package, ignore_errors=True)
    shutil.rmtree(package.venv, ignore_errors=True)


def create_package(target, **context):
    """
    Create a Python package from the current Cookiecutter template, create a
    virtual environment, and bootstrap it.
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
        result = run_cmd("./scripts/bootstrap.sh", venv=package.venv)
        print(result)

    return package


def gen_requirements(package):
    """
    Generate the pinned requirements files, with pip-tools, for the given
    Python package.
    """

    run_cmd("./scripts/gen_requirements.sh", venv=package.venv)


def install_dev_requirements(package):
    """
    Install all package dependencies, from its pinned dev requirements file,
    and the package itself, in editable mode.
    """

    run_cmd("pip-sync", "requirements/dev.txt", venv=package.venv)
    run_cmd("pip", "install", "-e", ".[dev]", venv=package.venv)


def add_dependency(dependency, package):
    """
    Given a Python package, add a new dependency to its "install_requires"
    field in setup.py.
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
    Given a Python package, with a dependency listed in its "install requires"
    field in setup.py, replace it with a new version.
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
    Add a new dependency to setup.py, generated the pinned requirements files,
    and install the dev requirements.
    """

    add_dependency(dependency, package)
    gen_requirements(package)
    install_dev_requirements(package)


def update_and_install_dependency(old, new, package):
    """
    Update a dependency in setup.py, then in the pinned requirements files, and
    install the dev requirements.
    """

    update_dependency(old, new, package)
    run_cmd("./scripts/update_requirements.sh", new, venv=package.venv)
    install_dev_requirements(package)


def get_meta(package):
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
    """

    result = run_cmd("bumpver", "show", "-ne", venv=package.venv)
    output = result.stdout.decode("utf-8").strip()

    return dict(line.split("=") for line in output.split("\n"))


def get_license_year():
    """
    Return the copyright year from the LICENSE file.
    """

    with open("LICENSE", "r") as license_file:
        license = license_file.read()

    match = re.match(r"^Copyright \(c\) (?P<year>\d{4})", license)

    return match.group("year")
