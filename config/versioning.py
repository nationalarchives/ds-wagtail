import os


def get_git_sha():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    head_path = os.path.join(base_dir, ".git", "HEAD")

    with open(head_path, "r") as fp:
        head = fp.read().strip()

    if head.startswith("ref: "):
        head = head[5:]
        revision_file = os.path.join(base_dir, ".git", *head.split("/"))
    else:
        return head

    if not os.path.exists(revision_file):
        # Check for Raven .git/packed-refs' file since a `git gc` may have run
        # https://git-scm.com/book/en/v2/Git-Internals-Maintenance-and-Data-Recovery
        packed_file = os.path.join(base_dir, ".git", "packed-refs")
        if os.path.exists(packed_file):
            with open(packed_file) as fh:
                for line in fh:
                    line = line.rstrip()
                    if line and line[:1] not in ("#", "^"):
                        try:
                            revision, ref = line.split(" ", 1)
                        except ValueError:
                            continue
                        if ref == head:
                            return revision

    with open(revision_file) as fh:
        return fh.read().strip()
