import datetime
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

PLATFORM_PROJECT_ID = "rasrzs7pi6sd4"
PRODUCTION_APP_INSTANCE = "main"
STAGING_APP_INSTANCE = "demo"

LOCAL_MEDIA_DIR = "media"
LOCAL_IMAGES_DIR = LOCAL_MEDIA_DIR + "/original_images"
LOCAL_DB_DUMP_DIR = "database_dumps"

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def container_exec(cmd, container_name="web"):
    return subprocess.run(["docker-compose", "exec", "-T", container_name, "bash", "-c", cmd])


def db_exec(cmd):
    "Execute something in the 'db' Docker container."
    return container_exec(cmd, "db")


def web_exec(cmd):
    "Execute something in the 'web' Docker container."
    return container_exec(cmd, "web")


@task
def run_management_command(c, cmd):
    """
    Run a Django management command in the 'web' Docker container
    with access to Django and other Python dependencies.
    """
    return container_exec(f"poetry run ./manage.py {cmd}", "web")


# -----------------------------------------------------------------------------
# Container management
# -----------------------------------------------------------------------------


@task
def build(c):
    """
    Build (or rebuild) local development containers.
    """
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
def test(c):
    """
    Run python tests in the web container
    """
    subprocess.call(
        [
            "docker-compose",
            "exec",
            "web",
            "poetry",
            "run",
            "./manage.py",
            "test",
            "--parallel",
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


def delete_local_renditions(c):
    psql(c, "TRUNCATE wagtailimages_rendition;")


def delete_db(c):
    db_exec(
        f"dropdb --if-exists --host db --username={LOCAL_DATABASE_USERNAME} {LOCAL_DATABASE_NAME}"
    )
    db_exec(
        f"createdb --host db --username={LOCAL_DATABASE_USERNAME} {LOCAL_DATABASE_NAME}"
    )


@task
def dump_db(c, filename):
    """Snapshot the database, files will be stored in the db container"""
    if not filename.endswith(".psql"):
        filename += ".psql"
    db_exec(
        f"pg_dump -d {LOCAL_DATABASE_NAME} -U {LOCAL_DATABASE_USERNAME} > {filename}"
    )
    print(f"Database dumped to: {filename}")


@task
def restore_db(c, filename):
    """Restore the database from a snapshot in the db container"""
    print("Stopping 'web' to sever DB connection")
    stop(c, "web")
    if not filename.endswith(".psql"):
        filename += ".psql"
    delete_db(c)
    db_exec(f"psql -d {LOCAL_DATABASE_NAME} -U {LOCAL_DATABASE_USERNAME} < {filename}")
    print(f"Database restored from: {filename}")
    start(c, "web")


# -----------------------------------------------------------------------------
# Pull from Production
# -----------------------------------------------------------------------------


@task
def pull_production_data(c):
    """Pull database from the production platform.sh env"""
    pull_database_from_platform(c, PRODUCTION_APP_INSTANCE)


@task
def pull_production_media(c):
    """Pull all media from the production platform.sh env"""
    pull_all_media_from_platform(c, PRODUCTION_APP_INSTANCE)


@task
def pull_production_images(c):
    """Pull ONLY images from the production platform.sh env"""
    pull_images_from_platform(c, PRODUCTION_APP_INSTANCE)


# -----------------------------------------------------------------------------
# Pull from Staging
# -----------------------------------------------------------------------------


@task
def pull_staging_data(c):
    """Pull database from the staging platform.sh env"""
    pull_database_from_platform(c, STAGING_APP_INSTANCE)


@task
def pull_staging_media(c):
    """Pull all media from the staging platform.sh env"""
    pull_all_media_from_platform(c, STAGING_APP_INSTANCE)


@task
def pull_staging_images(c):
    """Pull ONLY images from the staging platform.sh env"""
    pull_images_from_platform(c, STAGING_APP_INSTANCE)


# -----------------------------------------------------------------------------
# Platform.sh helpers
# -----------------------------------------------------------------------------


def enable_platform_ssh(c):
    known_hosts = os.path.expanduser("~/.ssh/known_hosts")
    for hostname in ('ssh.uk-1.platform.sh', 'git.uk-1.platform.sh'):
        # Remove existing keys for this hostname
        local(f"ssh-keygen -q -R {hostname}")
        # Add new ones
        local(f"ssh-keyscan {hostname} >> {known_hosts}")


def pull_database_from_platform(c, environment_name):
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    print("Stopping 'web' to sever DB connection")
    stop(c, "web")

    print("Fetching data from platform.sh")
    enable_platform_ssh(c)
    local(
        f"platform db:dump -e {environment_name} -p {PLATFORM_PROJECT_ID} -f {timestamp}.psql -d {LOCAL_DB_DUMP_DIR}"
    )

    print("Replacing local database with downloaded version")
    delete_db(c)
    restore_db(c, f"app/{LOCAL_DB_DUMP_DIR}/{timestamp}.psql")
    local(f"rm {LOCAL_DB_DUMP_DIR}/{timestamp}.psql")

    print("Applying migrations from local environment")
    run_management_command(c, "migrate")

    print("Anonymising downloaded data")
    run_management_command(c, "run_birdbath")

    print("Database updated successfully")
    print(
        "NOTE: Any Django users you were using before will no longer exist. "
        "You may want to run `python manage.py createsuperuser` from a container "
        "shell to create yourself a new one."
    )


def pull_files_from_platform(c, environment_name, source, destination):
    enable_platform_ssh(c)
    return local(
        "rsync -az --delete "
        f'"$(platform ssh -e {environment_name} -p {PLATFORM_PROJECT_ID} --pipe)"'
        f":{source}/ ./{destination}/"
    )


def pull_all_media_from_platform(
    c,
    environment_name,
):
    """
    Copies the entire 'media' folder from a platform.sh environment
    to a local one (including images, documents, videos, and audio)
    """
    pull_files_from_platform(c, environment_name, "media", LOCAL_MEDIA_DIR)
    delete_local_renditions(c)


def pull_images_from_platform(
    c,
    environment_name,
):
    """
    Copies only the 'media/original_images' folder from a platform.sh
    environment to a local one.

    To copy all media (including documents, videos and audio), use
    `pull_all_media_from_platform()`
    """
    pull_files_from_platform(
        c, environment_name, "media/original_images", LOCAL_IMAGES_DIR
    )
    delete_local_renditions(c)
