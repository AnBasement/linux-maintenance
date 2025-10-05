from rich import print
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
import subprocess

__version__ = "0.1.0"

console = Console()

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


def run_command(cmd: list[str]) -> int:
    """Execute a command and handle errors if any. Returns exit code."""
    try:
        subprocess.run(cmd, check=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(Panel.fit(
            f"[red]✗ Error: Command failed, exit code {e.returncode}[/red]",
            border_style="red"
            )
        )
        return e.returncode
    except FileNotFoundError:
        print(Panel.fit(
            f"[red]✗ Command not found:[/red] {cmd[0]}",
            border_style="red"
            ))
        return 1


def main() -> None:
    """Main function. Prints table and takes user input. Runs commands based
    on input."""
    print(table)
    while True:
        print(Panel.fit(
            "[yellow]Most tasks require sudo privileges.[/yellow]",
            border_style="yellow"
        ))
        selection = input(
            "Linux Maintenance\n"
            "=================\n"
            "Select which task to perform (1-5) or 'q' to quit: ")
        commands = {
            "1": ["sudo", "apt", "update"],
            "2": ["sudo", "apt", "upgrade"],
            "3": ["sudo", "apt", "autoremove"],
            "4": ["sudo", "apt", "clean"],
            "5": ["apt", "list", "--upgradable"],
        }

        if selection in commands:
            exit_code = run_command(commands[selection])
            if exit_code == 0:
                print(Panel.fit(
                    "[green]✓ Task completed successfully.[/green]",
                    border_style="green"
                ))
            else:
                print(Panel.fit("[yellow]Task encountered an error.[/yellow]",
                                border_style="yellow"))
        elif selection.lower() == "q":
            print(Panel.fit("Exiting..."))
            break
        elif selection == "test":
            print(Panel.fit(
                "\n[cyan]  Running error handling tests...  [/cyan]\n"
                ))

            print(Panel.fit("1. Testing success (exit 0):"))
            exit_code = run_command(["true"])
            print(Panel.fit(f"Returned: {exit_code}"))

            print(Panel.fit("2. Testing failure (exit 1):"))
            exit_code = run_command(["false"])
            print(Panel.fit(f"Returned: {exit_code}"))

            print(Panel.fit("3. Testing FileNotFoundError:"))
            exit_code = run_command(["this-does-not-exist"])
            print(Panel.fit(f"Returned: {exit_code}"))

            print(Panel.fit(
                "[green]✓ Tests complete![/green]",
                border_style="green"
            ))
        else:
            print(
                "Invalid selection, please choose a number between 1 and 5 "
                "or type q to quit."
                )


# Entry point for the script, runs main() if executed directly
if __name__ == "__main__":
    main()
