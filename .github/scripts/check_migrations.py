import subprocess
import sys


def get_diff():
    subprocess.run(
        ["git", "fetch", "origin"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    output = [
        f"./{file_path}"
        for file_path in subprocess.check_output(
            ["git", "diff", "--name-only", "origin/develop"]
        )
        .decode()
        .splitlines()
    ]
    if not output:
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
    with open(file) as f:
        contents = f.read()

    keywords = ["DeleteModel", "RenameModel", "RemoveField", "RenameField"]
    for keyword in keywords:
        if keyword in contents and f"etna:allow{keyword}" not in contents:
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
