import subprocess
import sys


def get_diff():
    """
    Gets the file diff between the current branch (your branch) and the
    main working branch.
    """
    subprocess.run(
        ["git", "fetch", "origin"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    output = [
        f"./{file_path}"
        for file_path in subprocess.check_output(
            ["git", "diff", "--name-only", "origin/main"]
        )
        .decode()
        .splitlines()
    ]
    return output


def check_migration_file(file):
    """
    Checks if a migration file contains any of the keywords listed
    in the `keywords` list that may be potentially harmful to our
    data.

    While AlterField is generally safe, it can be harmful if the
    field is being changed to a type that does not support the
    current data type. For example, changing a CharField to an
    IntegerField will result in a loss of data.
    """
    try:
        with open(file) as f:
            contents = f.read()
    except FileNotFoundError:
        print(f"Migration file {file} not found - likely deleted, skipping.")
        return False

    keywords = ["DeleteModel", "RenameModel", "RemoveField", "AlterField"]
    for keyword in keywords:
        if keyword in contents and f"# etna:allow{keyword}" not in contents:
            print(f"Warning: {file} contains a migration that may cause data loss.")
            return True


def main():
    file_diff = get_diff()

    migration_alert = False
    for file in file_diff:
        if "/migrations/" in file and file.endswith(".py"):
            if check_migration_file(file):
                migration_alert = True
    if migration_alert:
        print("Please review the migrations before pushing, to ensure no loss of data.")
        sys.exit(1)


if __name__ == "__main__":
    main()
