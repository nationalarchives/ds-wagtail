import os
import subprocess

from shlex import quote

from invoke import run as local
from invoke.tasks import task

LOCAL_DATABASE_NAME = "postgres"
LOCAL_DATABASE_USERNAME = "postgres"


# Process .env file
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f.readlines():
            if not line or line.startswith("#") or "=" not in line:
                continue
            var, value = line.strip().split("=", 1)
            os.environ.setdefault(var, value)

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def container_exec(cmd, container_name="web"):
    return local(f"docker-compose exec -T {container_name} bash -c {quote(cmd)}")


def db_exec(cmd):
    return container_exec(cmd, "db")


def web_exec(cmd):
    return container_exec(cmd, "web")


# -----------------------------------------------------------------------------
# Container management
# -----------------------------------------------------------------------------


@task
def build(c):
    """
    Build local containers
    """
    local("docker-compose build")


@task
def start(c):
    """
    Start the development environment
    """
    local("docker-compose up -d")


@task
def stop(c):
    """
    Start the development environment
    """
    local("docker-compose stop")


@task
def restart(c):
    """
    Restart the development environment
    """
    start(c)
    stop(c)


@task
def sh(c):
    """
    Run bash in a local container (with access to dependencies)
    """
    subprocess.run(["docker-compose", "exec", "web", "poetry", "run", "bash"])


# -----------------------------------------------------------------------------
# Database operations
# -----------------------------------------------------------------------------


def delete_db(c):
    db_exec(f"dropdb --if-exists --host db --username={LOCAL_DATABASE_USERNAME} {LOCAL_DATABASE_NAME}")
    db_exec(f"createdb --host db --username={LOCAL_DATABASE_USERNAME} {LOCAL_DATABASE_NAME}")


@task
def dump_db(c, filename):
    """Snapshot the database, files will be stored in the db container"""
    if not filename.endswith(".psql"):
        filename += '.psql'
    db_exec(f"pg_dump -d {LOCAL_DATABASE_NAME} -U {LOCAL_DATABASE_USERNAME} > {filename}")
    print(f"Database dumped to: {filename}")


@task
def restore_db(c, filename):
    """Restore the database from a snapshot in the db container"""
    print("Stopping 'web' to sever DB connection")
    local("docker-compose stop web")
    if not filename.endswith(".psql"):
        filename += '.psql'
    delete_db(c)
    db_exec(f"psql -d {LOCAL_DATABASE_NAME} -U {LOCAL_DATABASE_USERNAME} < {filename}")
    print(f"Database restored from: {filename}")
    local("docker-compose start web")
