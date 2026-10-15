
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_git(command):
    """Run a Git command and return its output."""
    result = subprocess.run(
        ["git", *command],
        text=True,
        capture_output=True
    )

    if result.returncode != 0:
        print(f"\nGit error: {result.stderr.strip()}")
        return None

    return result.stdout.strip()


def main():
    print("\n=== GitHub Activity Assistant ===")
    print(f"Time: {datetime.now():%Y-%m-%d %H:%M:%S}")

    # Confirm we are inside a Git repository.
    root = run_git(["rev-parse", "--show-toplevel"])

    if root is None:
        print("Open this script inside an existing Git repository.")
        sys.exit(1)

    print(f"Repository: {root}")

    # Show current branch.
    branch = run_git(["branch", "--show-current"])
    print(f"Branch: {branch or '(detached HEAD)'}")

    # Display genuine changes.
    status = run_git(["status", "--short"])

    if not status:
        print("\nNo file changes detected.")
        print("Work on your project and run this tool again.")
        return

    print("\nActual working-tree changes:")
    print(status)

    # Validate whitespace and conflict-marker issues.
    check = subprocess.run(
        ["git", "diff", "--check"],
        text=True,
        capture_output=True
    )

    if check.returncode != 0:
        print("\nPlease fix these issues before committing:")
        print(check.stdout)
        print(check.stderr)
        return

    # Display a summary of tracked changes.
    summary = run_git(["diff", "--stat"])
    if summary:
        print("\nChange summary:")
        print(summary)

    print("\nChoose an action:")
    print("1. Review detailed changes")
    print("2. Stage selected changes interactively")
    print("3. Exit")

    choice = input("Enter 1, 2, or 3: ").strip()

    if choice == "1":
        subprocess.run(["git", "diff", "--"])
        return

    if choice == "2":
        print("\nGit will let you choose which changes to stage.")
        result = subprocess.run(["git", "add", "-p"])

        if result.returncode != 0:
            print("Staging cancelled or unsuccessful.")
            return

        staged = run_git(["diff", "--cached", "--stat"])

        if not staged:
            print("No changes staged.")
            return

        print("\nChanges selected for commit:")
        print(staged)

        # Check staged changes for whitespace problems.
        if run_git(["diff", "--cached", "--check"]) is None:
            return

        if not input("\nCreate a commit with these changes? (yes/no): ").strip().lower() == "yes":
            print("Commit cancelled. Staged changes remain staged.")
            return

        message = input("Enter a meaningful commit message: ").strip()

        if not message:
            print("Commit message cannot be empty.")
            return

        commit = subprocess.run(
            ["git", "commit", "-m", message]
        )

        if commit.returncode != 0:
            print("Commit failed. Review the Git output.")
            return

        print("\nCommit created successfully.")

        push = input("Push this commit to the configured remote? (yes/no): ")
        if push.strip().lower() == "yes":
            result = subprocess.run(["git", "push"])

            if result.returncode == 0:
                print("Push completed successfully.")
            else:
                print("Push failed. Check the remote and branch settings.")

        return

    print("Exited without making changes.")


if __name__ == "__main__":
    main()
