#!/usr/bin/env python3

from rich import print
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
import subprocess
import asyncio
from desktop_notifier import DesktopNotifier, Urgency
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import argparse

# Setup argument parser
version_file = Path(__file__).parent / "VERSION"
if version_file.exists():
    with open(version_file) as vf:
        version_str = vf.read().strip()
else:
    version_str = "unknown"

parser = argparse.ArgumentParser(
    description="Linux Maintenance Script"
)
parser.add_argument(
    "--version", action="version",
    version=f"Linux Maintenance Script version {version_str}"
)
parser.add_argument(
    "--auto", action="store_true",
    help="Run all maintenance tasks automatically without prompts"
)
args = parser.parse_args()

# Setup logging
log_path = Path(__file__).parent / "logs" / "maintenance.log"
log_path.parent.mkdir(exist_ok=True)

logger = logging.getLogger("maintenance")
logger.setLevel(logging.INFO)

# Only add handler if one doesn't already exist
if not any(isinstance(h, TimedRotatingFileHandler) for h in logger.handlers):
    handler = TimedRotatingFileHandler(
        log_path,
        when="W2",           # Rotate every Wednesday
        backupCount=4,       # Keep 4 backups
        encoding="utf-8"
    )
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    ))
    logger.addHandler(handler)

logger.propagate = False

__version__ = "0.4.5"

console = Console()

notifier = DesktopNotifier(app_name="Linux Maintenance")

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
    ("Cleans up packages that were automatically installed and are no "
     "longer required"),
    "sudo apt autoremove -y"
)
table.add_row(
    "4",
    "Clean apt cache",
    "Frees up disk space by deleting cached package files.",
    "sudo apt autoclean -y"
)
table.add_row(
    "5",
    "List available updates",
    "Shows packages that can be updated (safe read-only check).",
    "apt list --upgradable"
)


def summarize_update_output(output: str) -> str:
    lines = output.splitlines()
    for line in lines:
        if "packages can be upgraded" in line.lower():
            return line.strip()
        if "all packages are up to date" in line.lower():
            return line.strip()

    return lines[-1].strip() if lines else "-"


def summarize_upgrade_output(output: str) -> str:
    """Extracts summary lines from apt upgrade output."""
    lines = output.splitlines()

    for line in lines:
        if "upgraded," in line.lower() and "newly installed" in line.lower():
            return line.strip()
        if "no packages will be upgraded" in line.lower():
            return line.strip()

    return lines[-1].strip() if lines else "-"


def summarize_remove_output(output: str) -> str:
    lines = output.splitlines()
    relevant = [line for line in lines if "removed" in line.lower()]
    return "\n".join(relevant) if relevant else "-"


def send_notification(title, message, urgency=Urgency.Normal):
    """Send a desktop notification."""
    try:
        notifier = DesktopNotifier(app_name="Linux Maintenance")
        asyncio.run(
            notifier.send(title=title, message=message, urgency=urgency)
            )
    except RuntimeError as e:
        logger.warning(f"Notification failed: {e}")


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """Execute a command and handle errors if any. Returns exit code."""
    logger.info(f"Executing: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True
            )

        output = result.stdout.strip()
        error = result.stderr.strip()

        if output:
            logger.info(f"Output: {output}")
        if error:
            apt_warning = "apt does not have a stable CLI interface"
            if apt_warning in error:
                logger.info(f"Error Output: {error}")
            else:
                logger.warning(f"Error Output: {error}")

        logger.info(f"Command succeeded: {' '.join(cmd)}")
        return (0, output, error)

    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {' '.join(cmd)}\n{e.stderr.strip()}")
        return (e.returncode, e.stdout.strip(), e.stderr.strip())

    except FileNotFoundError:
        error = f"Command not found: {cmd[0]}"
        logger.error(error)
        return (127, "", error)


def run_all_tasks() -> None:
    """Runs all maintenance tasks in sequence and displays a summary.
    Stops if any task fails."""
    tasks = {
        "Update": ["sudo", "apt", "update"],
        "Upgrade": ["sudo", "apt", "upgrade", "-y"],
        "Remove": ["sudo", "apt", "autoremove", "-y"],
        "Clean": ["sudo", "apt", "autoclean", "-y"]
    }

    results_list = []

    send_notification("Maintenance Started", "Running all maintenance tasks.")
    logger.info("Maintenance started.")

    with console.status(
            "[bold green]Starting maintenance tasks...[/bold green]"
            ) as status:

        for task_counter, (task_name, command_list) in enumerate(
                tasks.items(), start=1):
            status.update(f"Task {task_counter} of {len(tasks)}: {task_name}")
            logger.info(
                f"Running task {task_counter}/{len(tasks)}: {task_name}"
                )

            exit_code, output, error = run_command(command_list)

            if task_name == "Update":
                processed_output = summarize_update_output(output)
            elif task_name == "Upgrade":
                processed_output = summarize_upgrade_output(output)
            elif task_name == "Remove":
                processed_output = summarize_remove_output(output)
            elif task_name == "Clean":
                processed_output = "-"

            results_list.append({
                "command": task_name,
                "exit_code": ("[bold green]✓[/bold green]" if exit_code == 0
                              else "[bold red]✗[/bold red]"),
                "output": processed_output,
                "error": error if exit_code != 0 else ""
                })

            if exit_code != 0:
                logger.error(f"Task '{task_name}' failed: {error}")
                send_notification(
                    "Maintenance Error",
                    f"Task '{task_name}' encountered an error.",
                    Urgency.Critical
                    )
                print(Panel.fit(
                    "[red]✖ Task failed, cancelling action.[/red]",
                    border_style="red"))
                break

    all_tasks_table = Table(title="Maintenance Summary")

    all_tasks_table.add_column("Task", justify="left", no_wrap=True)
    all_tasks_table.add_column("Exit Code", justify="center", no_wrap=True)
    all_tasks_table.add_column("Details", justify="left")
    all_tasks_table.add_column("Error", justify="center")

    for result in results_list:
        all_tasks_table.add_row(
            result["command"],
            str(result["exit_code"]),
            result["output"] if result["output"] else "-",
            result["error"] if result["error"] else "-"
        )

    send_notification(
        "Maintenance Complete",
        f"{len(results_list)} tasks have been processed.",
        Urgency.Critical
        )
    print(all_tasks_table)


def main() -> None:
    """Main function. Prints table and takes user input. Runs commands based
    on input."""
    print(table)
    first_run = True
    while True:
        if first_run:
            print(Panel.fit(
                "[yellow]Most tasks require sudo privileges.[/yellow]",
                border_style="yellow"
            ))
            first_run = False

        selection = input(
            "Linux Maintenance\n"
            "=================\n"
            "Select which task to perform (1-5), 'all' "
            "to run full suite or 'q' to quit: ")
        commands = {
            "1": ["sudo", "apt", "update"],
            "2": ["sudo", "apt", "upgrade", "-y"],
            "3": ["sudo", "apt", "autoremove", "-y"],
            "4": ["sudo", "apt", "autoclean", "-y"],
            "5": ["apt", "list", "--upgradable"],
        }

        if selection in commands:
            exit_code, output, error = run_command(commands[selection])
            # Use summary helpers for upgrade/remove
            if selection == "1":
                summary = summarize_update_output(output)
            elif selection == "2":
                summary = summarize_upgrade_output(output)
            elif selection == "3":
                summary = summarize_remove_output(output)
            else:
                summary = output
            if exit_code == 0:
                send_notification(
                    "Task Completed",
                    f"Command '{' '.join(commands[selection])}' "
                    f"completed successfully."
                )
                print(Panel.fit(
                    f"[green]✓ Task completed successfully.[/green]\n"
                    f"[white]{summary}[/white]",
                    border_style="green"
                ))
            else:
                send_notification(
                    "Task Error",
                    f"Command '{' '.join(commands[selection])}' "
                    f"encountered an error.",
                    Urgency.Critical
                )
                print(Panel.fit(
                    "[yellow]Task encountered an error.[/yellow]",
                    border_style="yellow"))

        elif selection == "all":
            run_all_tasks()
            continue
        elif selection.lower() == "q":
            print(Panel.fit("Exiting..."))
            break
        elif selection == "test":
            print(Panel.fit(
                "\n[cyan]  Running error handling tests...  [/cyan]\n"
                ))

            print(Panel.fit("1. Testing success (exit 0):"))
            exit_code, output, error = run_command(["true"])
            send_notification(
                "Test Completed",
                "Test command 'true' completed successfully.",
                Urgency.Normal
                )
            print(Panel.fit(f"Returned: {exit_code}"))

            print(Panel.fit("2. Testing failure (exit 1):"))
            exit_code, output, error = run_command(["false"])
            send_notification(
                "Test Completed",
                "Test command 'false' failed.",
                Urgency.Critical
                )
            print(Panel.fit(f"Returned: {exit_code}"))

            print(Panel.fit("3. Testing FileNotFoundError:"))
            exit_code, output, error = run_command(["this-does-not-exist"])
            print(Panel.fit(f"Returned: {exit_code}"))
            send_notification(
                "Test Completed",
                "Test command 'this-does-not-exist' failed.",
                Urgency.Critical
                )

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
    if args.auto:
        run_all_tasks()
    else:
        main()
