# Changelog

All notable changes to the project will be documented here.

The format is based on [Keep a Changelog v1.1.0](https://keepachangelog.com/en/1.1.0/),
and adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1] - 2025-10-04

### Added

* Initial implementation of `maintenance.py`.
* Rich-formatted table displaying key Ubuntu maintenance tasks:
  * Update package lists (`sudo apt update`)
  * Upgrade packages (`sudo apt upgrade -y`)
  * Remove unused packages (`sudo apt autoremove -y`)
  * Clean APT cache (`sudo apt clean`)
  * List available updates (`apt list --upgrade`)
* Project structure with `main()` entry point and CLI-ready layout.

### Notes

* Commands are displayed only; no system actions are executed in this version.
* Serves as the foundation for later stages adding subprocess execution, notifications, and scheduling.
