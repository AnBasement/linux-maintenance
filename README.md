# Linux Maintenance Reminder

This is a simple program that sends scheduled reminders to perform certain actions when running a Linux distribution.

## Shell template

```sh
#!/bin/bash
# Activate virtual environment
source /home/your/path/to/venv/bin/activate

# Run the maintenance script using the venv’s Python
/home/path/to/maintenance.py >> /home/path/to/maintenance.log 2>&1
```
