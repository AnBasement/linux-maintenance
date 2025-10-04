from rich import print
from rich.table import Table
import subprocess

# Script that provides reminders to perform certain regular maintenance
# tasks on a Linux distribution.

# Create table to display maintenance tasks
table = Table(title="Linux Maintenance")

# Add columns for task name, description and command
table.add_column("No.", justify="center", no_wrap=True)
table.add_column("Task", justify="center", no_wrap=True)
table.add_column("Description", justify="center", no_wrap=True)
table.add_column("Command", justify="center", no_wrap=True)

# Add rows for the various tasks
table.add_row(
    "1",
    "Update package lists",
    "Fetches the latest information about available packages and updates.",
    "sudo apt update"
    )
table.add_row(
    "2",
    "Upgrade packages",
    "Installs newer versions of all currently installed packages.",
    "sudo apt upgrade -y"
)
table.add_row(
    "3",
    "Remove unused packages",
    "Cleans up packages that were automatically installed and are no longer "
    "required",
    "sudo apt autoremove -y"
)
table.add_row(
    "4",
    "Clean apt cache",
    "Frees up disk space by deleting cached package files.",
    "sudo apt clean"
)
table.add_row(
    "5",
    "List available updates",
    "Shows packages that can be updated (safe read-only check).",
    "apt list --upgradable"
)


# Subprocess function to update package lists
def update_package_lists() -> None:
    """Function that updates the package lists."""
    subprocess.run(["sudo", "apt", "update"], universal_newlines=True)


def upgrade_packages() -> None:
    """Function that upgrades all packages."""
    subprocess.run(
        ["sudo", "apt", "upgrade", "-y"],
        universal_newlines=True
        )


def remove_unused_packages() -> None:
    """Function that removes unused packages."""
    subprocess.run(
        ["sudo", "apt", "autoremove", "-y"],
        universal_newlines=True
        )


def clean_apt_cache() -> None:
    """Function that cleans the apt cache."""
    subprocess.run(
        ["sudo", "apt", "clean"],
        universal_newlines=True
        )


def list_available_updates() -> None:
    """Function that lists available updates."""
    subprocess.run(
        ["apt", "list", "--upgradable"],
        universal_newlines=True
        )


# Main function, prints the maintenance table.
def main() -> None:
    print(table)
    while True:
        selection = input(
            "Linux Maintenance\n"
            "=================\n"
            "Select which task to perform (1-5) or 'q' to quit: ")
        if selection == "1":
            update_package_lists()
            continue

        elif selection == "2":
            upgrade_packages()
            continue

        elif selection == "3":
            remove_unused_packages()
            continue

        elif selection == "4":
            clean_apt_cache()
            continue

        elif selection == "5":
            list_available_updates()
            continue
        elif selection.lower() == "q":
            print("Exiting the maintenance script.")
            break
        else:
            print("Invalid selection. Please choose a number between 1 and 5.")


# Entry point for the script, runs main() if executed directly
if __name__ == "__main__":
    main()
