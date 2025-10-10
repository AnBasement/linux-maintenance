<!-- markdownlint-disable MD024 -->
# Changelog

All notable changes to the project will be documented here.

The format is based on [Keep a Changelog v1.1.0](https://keepachangelog.com/en/1.1.0/),
and adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.5] - 2025-10-10

### Added

- Implemented flags for command-line arguments and updated README accordingly.

### Changed

- Changing from `clean` to `autoclean` with the `-y` flag.
- Function run_all_tasks() now uses the output helper functions on all relevant tasks.
- Updated README to require Python 3.9 or newer.
- Removed some unused dependencies: loguru, schedule, questionary, rich-click
- Updated wrapper scripts instructions

### Fixed

- Notification urgency bug fixed in the function run_all_tasks().
- Tweak README to match sudoers entries with actual commands being run.

## [0.4.4] - 2025-10-10

### Added

- Implemented log rotation with 4 backups. Hardcoded to wednesdays, with instructions on how to change to fit personal preference.

---

## [0.4.3] - 2025-10-10

### Added

- Helper functions for parsing and summarizing apt command output

### Changed

- Improved output summaries for Update, Upgrade, and Remove tasks
- Downgraded apt CLI stability warnings from WARNING to INFO level to reduce log noise

### Fixed

- Resolved subprocess crashes when running individual tasks that require confirmation by adding `-y` flags to relevant commands

---

## [0.4.2] - 2025-10-09

### Fixed

- Prevent duplicated log entries by ensuring a single FileHandler is attached to the logger.
- Creates fresh desktop notifier every time to avoid `RuntimeError` when running all tasks.

---

## [0.4.1] - 2025-10-08

### Fixed

- Fixed duplicated log entries; cleaned up command success/error logging.

## [0.4.0] - 2025-10-08

### Added

- Logging system for maintenance operations
  - Logs are saved to `logs/maintenance.log`
  - Command execution, outputs, and errors are logged with timestamps
  - Separate log levels for info, warnings, and errors
- Script prepared for automated execution
  - Script can be run with `auto` argument to skip interactive menu
  - Designed for anacron/cron scheduling with minimal user interaction
  - Made script executable with proper shebang for direct execution
- Shell script template for anacron/cron integration
  - Basic template added to README for virtual environment activation

---

## [0.3.0] - 2025-10-07

### Added

- Desktop notification system using desktop-notifier library
  - Success notifications when maintenance tasks complete successfully
  - Error notifications with critical urgency for failed tasks
  - Start/completion notifications for full maintenance suite execution
  - Critical urgency for full suite run success in case user is AFK
  - Test command notifications for error handling validation

---

## [0.2.2] - 2025-10-07

### Fixed

- Fixed loop in main menu that led to not accepting user input more than once

---

## [0.2.1] - 2025-10-07

### Fixed

- Fixed incorrect error handling of run_command() that returned error even on successfull completions

---

## [0.2.0] - 2025-10-07

### Added

- You can now run the entire maintenance suite with the `all` command
  - Command is styled with Rich progress spinner throughout
  - Summary table shows information about performed tasks and any errors that might occur
  - Command outputs are filtered to only show relevant information
- UI has been updated with Rich Panel styling
- Added a warning about requiring sudo privileges

### Changed

- Error handling has been enhanced with Rich styling
- Better formatting and more options for user input
- Command execution now captures and returns output, errors and exit codes
- Added the `all` option to the menu
- Improved visual feedback throughout application
- `run_command()` has been modified to return stdout, exit codes and stderr for better error handling
- Implemented output processing logic for different maintenance tasks

---

## [0.1.0] - 2025-10-04

### Added

- Error handling for command execution (catches `CalledProcessError` and `FileNotFoundError`)
- Unified `run_command()` function to execute all maintenance commands

### Changed

- Refactored individual command functions into a single reusable function
- Commands now stored in a dictionary for better maintainability

### Removed

- Individual functions for each maintenance task (`update_package_lists()`, `upgrade_packages()`, etc.)

---

## [0.0.2] - 2025-10-04

### Fixed

- Fixed incorrect `--upgrade` flag to `--upgradable` in `list_available_updates()` function

### Added

- Version management system with bump-my-version
- Automated bump script for patch/minor/major releases
- VERSION file for version tracking

## [0.1] - 2025-10-04

### Features

- Initial implementation of `maintenance.py`.
- Rich-formatted table displaying key Ubuntu maintenance tasks:
  - Update package lists (`sudo apt update`)
  - Upgrade packages (`sudo apt upgrade -y`)
  - Remove unused packages (`sudo apt autoremove -y`)
  - Clean APT cache (`sudo apt clean`)
  - List available updates (`apt list --upgrade`)
- Project structure with `main()` entry point and CLI-ready layout.

### Notes

- Commands are displayed only; no system actions are executed in this version.
- Serves as the foundation for later stages adding subprocess execution, notifications, and scheduling.
