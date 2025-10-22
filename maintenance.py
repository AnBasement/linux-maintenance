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
import json
import os

# Setup argument parser
version_file = Path(__file__).parent / "VERSION"
if version_file.exists():
    with open(version_file) as vf:
        version_str = vf.read().strip()
else:
    version_str = "unknown"

parser = argparse.ArgumentParser(description="Linux Maintenance Script")
parser.add_argument(
    "--version",
    action="version",
    version=f"Linux Maintenance Script version {version_str}",
)
parser.add_argument(
    "--auto",
    action="store_true",
    help="Run all maintenance tasks automatically without prompts",
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
        when="W2",  # Rotate every Wednesday
        backupCount=4,  # Keep 4 backups
        encoding="utf-8",
    )
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)

logger.propagate = False

__version__ = "0.6.1"

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
    "sudo apt update",
)
table.add_row(
    "2",
    "Upgrade packages",
    "Installs newer versions of all currently installed packages.",
    "sudo apt upgrade -y",
)
table.add_row(
    "3",
    "Remove unused packages",
    (
        "Cleans up packages that were automatically installed and are no "
        "longer required"
    ),
    "sudo apt autoremove -y",
)
table.add_row(
    "4",
    "Clean apt cache",
    "Frees up disk space by deleting cached package files.",
    "sudo apt autoclean -y",
)
table.add_row(
    "5",
    "List available updates",
    "Shows packages that can be updated (safe read-only check).",
    "apt list --upgradable",
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
        asyncio.run(notifier.send(title=title, message=message, urgency=urgency))
    except RuntimeError as e:
        logger.warning(f"Notification failed: {e}")


def load_tasks_from_json(file_path: Path) -> list[dict]:
    """Load tasks from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            raw_tasks = data.get('tasks', [])

            valid_tasks = []
            for idx, task in enumerate(raw_tasks):
                is_valid, error_msg = validate_task(task)
                if is_valid:
                    valid_tasks.append(task)
                else:
                    logger.error(f"Invalid task at index {idx} in {file_path.name}: {error_msg}")
                    logger.debug(f"Problematic task data: {task}")

            logger.info(f"Loaded {len(valid_tasks)}/{len(raw_tasks)} valid tasks from {file_path.name}")
            return valid_tasks

    except FileNotFoundError:
        logger.warning(f"Task file not found: {file_path}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        return []


def load_all_tasks() -> list[dict]:
    """Load all applicable task files."""
    tasks_dir = Path(__file__).parent / "tasks"
    all_tasks = []

    base_tasks = load_tasks_from_json(tasks_dir / "base.json")
    all_tasks.extend(base_tasks)

    pkg_manager = detect_package_manager()
    if pkg_manager:
        pkg_tasks_file = tasks_dir / f"{pkg_manager}.json"
        if pkg_tasks_file.exists():
            pkg_tasks = load_tasks_from_json(pkg_tasks_file)
            all_tasks.extend(pkg_tasks)
            logger.info(f"Loaded {len(pkg_tasks)} {pkg_manager} tasks")

    optional_tasks = load_tasks_from_json(tasks_dir / "optional.json")
    all_tasks.extend(optional_tasks)
    
    logger.info(f"Total tasks loaded: {len(all_tasks)}")
    return all_tasks


def detect_package_manager() -> str | None:
    """Detect which package manager is available."""
    managers = {
        "apt": ["apt", "--version"],
        "dnf": ["dnf", "--version"],
        "pacman": ["pacman", "--version"],
        "zypper": ["zypper", "--version"]
    }

    for name, check_cmd in managers.items():
        try:
            result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info(f"Detected package manager: {name}")
                return name
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            continue

    logger.warning("No supported package manager detected")
    return None


def validate_task(task: dict) -> tuple[bool, str]:
    """
    Validate that a task has all required fields with correct types.

    Returns:
        (is_valid, error_message)
    """
    required_fields = ['name', 'description', 'command']
    for field in required_fields:
        if field not in task:
            return (False, f"Missing required field: {field}")

    if not isinstance(task['name'], str) or not task['name'].strip():
        return (False, "Field 'name' must be a non-empty string")

    if not isinstance(task['description'], str) or not task['description'].strip():
        return (False, "Field 'description' must be a non-empty string")

    if not isinstance(task['command'], list) or len(task['command']) == 0:
        return (False, "Field 'command' must be a non-empty list")

    for idx, item in enumerate(task['command']):
        if not isinstance(item, str):
            return (False, f"Command item at index {idx} must be a string, got {type(item).__name__}")

    if 'auto_safe' in task and not isinstance(task['auto_safe'], bool):
        return (False, "Field 'auto_safe' must be a boolean")

    if 'requires_sudo' in task and not isinstance(task['requires_sudo'], bool):
        return (False, "Field 'requires_sudo' must be a boolean")

    if 'risk_level' in task:
        valid_levels = ['low', 'medium', 'high']
        if task['risk_level'] not in valid_levels:
            return (False, f"Field 'risk_level' must be one of {valid_levels}")

    if 'check_command' in task:
        if not isinstance(task['check_command'], list):
            return (False, "Field 'check_command' must be a list")

    return (True, "")


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """Execute a command and handle errors if any. Returns exit code."""
    logger.info(f"Executing: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

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
    """Run all maintenance tasks."""
    all_tasks = load_all_tasks()

    if not all_tasks:
        logger.error("No tasks loaded!")
        print(
            Panel.fit("[red]Error: No tasks could be loaded.[/red]", border_style="red")
        )
        return

    auto_tasks = [task for task in all_tasks if task.get("auto_safe", False)]

    if not auto_tasks:
        logger.warning("No auto-safe tasks found")
        return

    logger.info(f"Starting automated run with {len(auto_tasks)} tasks")
    results_list = []

    send_notification(
        "Maintenance Started", f"Running {len(auto_tasks)} automated tasks"
    )

    with console.status(
        "[bold green]Starting maintenance tasks...[/bold green]"
    ) as status:
        for task_counter, task in enumerate(auto_tasks, start=1):
            task_name = task["name"]
            command_list = task["command"]

            # Sudo check
            requires_sudo = task.get('requires_sudo', False)

            if requires_sudo and os.geteuid() != 0:
                logger.warning(f"Task '{task_name}' requires sudo but not running as root")
                print(Panel.fit(
                    f"[red]Task '{task_name}' requires sudo but script is not running as root.[/red]",
                    border_style="red"
                ))
                continue

            status.update(f"Task {task_counter} of {len(auto_tasks)}: {task_name}")
            logger.info(f"Running task {task_counter}/{len(auto_tasks)}: {task_name}")

            exit_code, output, error = run_command(command_list)

            if "update" in task_name.lower():
                processed_output = summarize_update_output(output)
            elif "upgrade" in task_name.lower():
                processed_output = summarize_upgrade_output(output)
            elif "remove" in task_name.lower():
                processed_output = summarize_remove_output(output)
            else:
                processed_output = output if output else "-"

            results_list.append(
                {
                    "command": task_name,
                    "exit_code": (
                        "[bold green]✓[/bold green]"
                        if exit_code == 0
                        else "[bold red]✗[/bold red]"
                    ),
                    "output": processed_output,
                    "error": error if exit_code != 0 else "",
                }
            )

            if exit_code != 0:
                logger.error(f"Task '{task_name}' failed: {error}")
                send_notification(
                    "Maintenance Error",
                    f"Task '{task_name}' encountered an error.",
                    Urgency.Critical,
                )
                print(
                    Panel.fit(
                        "[red]✖ Task failed, cancelling action.[/red]",
                        border_style="red",
                    )
                )
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
            result["error"] if result["error"] else "-",
        )

    send_notification("Maintenance Complete", f"{len(results_list)} tasks processed.")
    print(all_tasks_table)


def main() -> None:
    """Main function. Prints table and takes user input."""
    # Load all available tasks
    all_tasks = load_all_tasks()

    if not all_tasks:
        print(
            Panel.fit("[red]Error: No tasks could be loaded.[/red]", border_style="red")
        )
        return

    # Build menu table from loaded tasks
    menu_table = Table(title="Linux Maintenance")
    menu_table.add_column("No.", justify="center", no_wrap=True)
    menu_table.add_column("Task", justify="center", no_wrap=True)
    menu_table.add_column("Description", justify="center", no_wrap=True)
    menu_table.add_column("Command", justify="center", no_wrap=True)

    for idx, task in enumerate(all_tasks, start=1):
        menu_table.add_row(
            str(idx), task["name"], task["description"], " ".join(task["command"])
        )

    print(menu_table)
    first_run = True

    while True:
        if first_run:
            print(
                Panel.fit(
                    "[yellow]Most tasks require sudo privileges.[/yellow]",
                    border_style="yellow",
                )
            )
            first_run = False

        max_choice = len(all_tasks)
        selection = input(
            f"Linux Maintenance\n"
            f"=================\n"
            f"Select task (1-{max_choice}), 'all' for full suite, or 'q' to quit: "
        )

        # Handle numeric selection
        if selection.isdigit():
            choice_num = int(selection)
            if 1 <= choice_num <= max_choice:
                task = all_tasks[choice_num - 1]
                requires_sudo = task.get('requires_sudo', False)

                if requires_sudo and os.geteuid() != 0:
                    logger.warning(f"Task '{task['name']}' requires sudo but not running as root")
                    print(Panel.fit(
                        f"[red]Task '{task['name']}' requires sudo but script is not running as root.[/red]",
                        border_style="red"
                    ))
                    return

                exit_code, output, error = run_command(task["command"])

                # Summarize output
                task_name = task["name"].lower()
                if "update" in task_name:
                    summary = summarize_update_output(output)
                elif "upgrade" in task_name:
                    summary = summarize_upgrade_output(output)
                elif "remove" in task_name:
                    summary = summarize_remove_output(output)
                else:
                    summary = output if output else "-"

                if exit_code == 0:
                    send_notification(
                        "Task Completed", f"'{task['name']}' completed successfully."
                    )
                    print(
                        Panel.fit(
                            f"[green]✓ Task completed successfully.[/green]\n[white]{summary}[/white]",
                            border_style="green",
                        )
                    )
                else:
                    send_notification(
                        "Task Error",
                        f"'{task['name']}' encountered an error.",
                        Urgency.Critical,
                    )
                    print(
                        Panel.fit(
                            "[yellow]Task encountered an error.[/yellow]",
                            border_style="yellow",
                        )
                    )
            else:
                print(f"Invalid selection. Please choose 1-{max_choice}.")

        elif selection == "all":
            run_all_tasks()
        elif selection.lower() == "q":
            print(Panel.fit("Exiting..."))
            break
        elif selection == "test":
            print(Panel.fit("\n[cyan]  Running error handling tests...  [/cyan]\n"))

            print(Panel.fit("1. Testing success (exit 0):"))
            exit_code, output, error = run_command(["true"])
            send_notification(
                "Test Completed",
                "Test command 'true' completed successfully.",
                Urgency.Normal,
            )
            print(Panel.fit(f"Returned: {exit_code}"))

            print(Panel.fit("2. Testing failure (exit 1):"))
            exit_code, output, error = run_command(["false"])
            send_notification(
                "Test Completed", "Test command 'false' failed.", Urgency.Critical
            )
            print(Panel.fit(f"Returned: {exit_code}"))

            print(Panel.fit("3. Testing FileNotFoundError:"))
            exit_code, output, error = run_command(["this-does-not-exist"])
            print(Panel.fit(f"Returned: {exit_code}"))
            send_notification(
                "Test Completed",
                "Test command 'this-does-not-exist' failed.",
                Urgency.Critical,
            )

            print(Panel.fit("[green]✓ Tests complete![/green]", border_style="green"))
        else:
            print(f"Invalid selection. Please choose 1-{max_choice} or 'q' to quit.")


# Entry point for the script, runs main() if executed directly
if __name__ == "__main__":
    if args.auto:
        run_all_tasks()
    else:
        main()
