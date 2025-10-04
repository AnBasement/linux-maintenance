from rich import print
from rich.table import Table
# Script that provides reminders to perform certain regular maintenance
# tasks on a Linux distribution.

# Create table to display maintenance tasks
table = Table(title="Linux Maintenance")

# Add columsn for task name, description and command
table.add_column("Task", justify="center", no_wrap=True)
table.add_column("Description", justify="center", no_wrap=True)
table.add_column("Command", justify="center", no_wrap=True)

# Add rows for the various tasks
table.add_row(
    "Update package lists",
    "Fetches the latest information about available packages and updates.",
    "sudo apt update"
    )
table.add_row(
    "Upgrade packages",
    "Installs newer versions of all currently installed packages.",
    "sudo apt upgrade -y"
)
table.add_row(
    "Remove unused packages",
    "Cleans up packages that were automatically installed and are no longer "
    "required",
    "sudo apt autoremove -y"
)
table.add_row(
    "Clean apt cache",
    "Frees up disk space by deleting cached package files.",
    "sudo apt clean"
)
table.add_row(
    "List available updates",
    "Shows packages that can be updated (safe read-only check).",
    "apt list --upgrade"
)


# Main function, prints the maintenance table.
def main() -> None:
    print(table)


# Entry point for the script, runs main() if executed directly
if __name__ == "__main__":
    main()
