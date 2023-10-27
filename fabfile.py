import os
import subprocess

from invoke import run as local
from invoke.tasks import task

# Process .env file
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f.readlines():
            if not line or line.startswith("#") or "=" not in line:
                continue
            var, value = line.strip().split("=", 1)
            os.environ.setdefault(var, value)


LOCAL_DATABASE_NAME = os.getenv("DATABASE_NAME")
LOCAL_DATABASE_USERNAME = os.getenv("DATABASE_USER")

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def container_exec(cmd, container_name="web", check_returncode=False):
    result = subprocess.run(
        ["docker-compose", "exec", "-T", container_name, "bash", "-c", cmd]
    )
    if check_returncode:
        result.check_returncode()
    return result


def db_exec(cmd, check_returncode=False):
    "Execute something in the 'db' Docker container."
    return container_exec(cmd, "db", check_returncode)


def web_exec(cmd, check_returncode=False):
    "Execute something in the 'web' Docker container."
    return container_exec(cmd, "web", check_returncode)


def dev_exec(cmd, check_returncode=False):
    "Execute something in the 'dev' Docker container."
    return container_exec(cmd, "dev", check_returncode)


def cli_exec(cmd, check_returncode=False):
    return container_exec(cmd, "cli", check_returncode)


@task
def run_management_command(c, cmd, check_returncode=False):
    """
    Run a Django management command in the 'web' Docker container
    with access to Django and other Python dependencies.
    """
    return web_exec(f"poetry run python manage.py {cmd}", check_returncode)


# -----------------------------------------------------------------------------
# Container management
# -----------------------------------------------------------------------------


@task
def build(c):
    """
    Build (or rebuild) local development containers.
    """
    # bash copy .env.example .env if .env does not exist
    if not os.path.exists(".env"):
        local("cp .env.example .env")
    local("docker-compose build")


@task
def start(c, container_name=None):
    """
    Start the local development environment.
    """
    cmd = "docker-compose up -d"
    if container_name:
        cmd += f" {container_name}"
    local(cmd)


@task
def stop(c, container_name=None):
    """
    Stop the local development environment.
    """
    cmd = "docker-compose stop"
    if container_name:
        cmd += f" {container_name}"
    local(cmd)


@task
def update_deps(c):
    """
    Update npm and poetry dependencies through Docker containers
    """
    local("docker-compose --profile update up -d")


@task
def restart(c):
    """
    Restart the local development environment.
    """
    start(c)
    stop(c)


@task
def sh(c):
    """
    Run bash in a local container (with access to dependencies)
    """
    subprocess.run(["docker-compose", "exec", "web", "poetry", "run", "bash"])


@task
def dev(c):
    """
    Run bash in the local development helper container (with access to dependencies)
    """
    subprocess.run(["docker", "exec", "-it", "dev", "/bin/bash"])


@task
def format(c):
    """
    Apply formatters to code python code
    """
    start(c, "dev")
    dev_exec("format")


@task
def test(c, lint=False, parallel=False):
    """
    Run python tests in the web container
    """
    start(c, "dev")
    if lint:
        print("Checking isort compliance...")
        dev_exec("isort . --check --diff")
        print("Checking Black compliance...")
        dev_exec("black . --check --diff --color --fast")
        print("Checking flake8 compliance...")
        dev_exec("flake8 .")
        print("Running Django tests...")
    cmd = "manage test"
    if parallel:
        cmd += " --parallel"
    dev_exec(cmd)


# -----------------------------------------------------------------------------
# Database operations
# -----------------------------------------------------------------------------


@task
def create_superuser(c):
    """
    Run bash in a local container (with access to dependencies)
    """
    subprocess.run(
        [
            "docker-compose",
            "exec",
            "web",
            "poetry",
            "run",
            "python",
            "manage.py",
            "createsuperuser",
            "--noinput",
        ]
    )


# -----------------------------------------------------------------------------
# Database operations
# -----------------------------------------------------------------------------


@task
def psql(c, command=None):
    """
    Connect to the local postgres DB using psql
    """
    cmd_list = [
        "docker-compose",
        "exec",
        "db",
        "psql",
        *["-d", LOCAL_DATABASE_NAME],
        *["-U", LOCAL_DATABASE_USERNAME],
    ]
    if command:
        cmd_list.extend(["-c", command])

    subprocess.run(cmd_list)
