# Linux Maintenance Reminder

This maintenance script started as a personal project to re-acquaint myself with Linux systems and to further expand my Python knowledge.

It currently automates some common system maintenance tasks, like updating packages and clearing caches. Further options are planned for the future.

I want to stress that I wont take responsibility for anything going wrong if you test this out. While the script itself should be entirely safe, the automated nature of it does mean you will not be presented with a list of packages to be updated, for instance, as all tasks requiring input have a `-y` flag. You'll have to check the logs to see what packages were upgraded.

## What it does

- **Interactive menu**: Pretty terminal interface (using Rich library) where you can pick tasks manually
- **Auto mode**: Run everything at once with `python maintenance.py --auto` - good for scheduling
- **Desktop notifications**: Pops up notifications when stuff finishes (or breaks)
- **Basic logging**: Saves what happened to `logs/maintenance.log` so you can see what went wrong
- **Works with anacron/cron**: I set it up to run automatically on my laptop

## Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd linux-maintenance
   ```

2. **Set up a virtual environment (recommended):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Make the script executable:**

   ```bash
   chmod +x maintenance.py
   ```

## Usage

### Manual Execution

**Interactive Mode:**

```bash
python maintenance.py
```

This opens an interactive menu where you can select individual tasks or run all maintenance operations.

**Automated Mode:**

```bash
python maintenance.py --auto
```

This runs all maintenance tasks without any user interaction, perfect for automation.

### Setting up Anacron

If you know your system will always be powered on at certain times, a cron job will do the job. However, if you're like me using a laptop a lot at very varying times, you'll have to set up an anacron job for automated running of the script.

1. **Create a wrapper script** (e.g., `run_maintenance.sh`):

   ```bash
   #!/bin/bash
   
   # Set env variables
   export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
   export HOME="/home/username"
   
   # Activate virtual environment
   source /home/username/path/to/linux-maintenance/venv/bin/activate
   
   # Change to script directory
   cd /home/username/path/to/linux-maintenance
   
   # Run maintenance script in auto mode
   ./maintenance.py --auto >> logs/maintenance.log 2>&1
   ```

2. **Make the wrapper executable:**

   ```bash
   chmod +x run_maintenance.sh
   ```

3. **Configure sudoers for passwordless execution**

   This step is required for automated runs. **WARNING**: This gives your user passwordless sudo access for these specific commands. Only do this if you understand the security implications and are okay with the risk.

   ```bash
   sudo visudo
   ```

   Add this line (replace `username` with your actual username):

   ```text
   yourusername ALL=(ALL) NOPASSWD: /usr/bin/apt update -y, /usr/bin/apt upgrade -y, /usr/bin/apt autoremove -y, /usr/bin/apt autoclean -y
   ```

4. **Add anacron job:**

   ```bash
   sudo nano /etc/anacrontab
   ```

   Add this line to run maintenance every 7 days:

   ```text
   7    10    maintenance    /home/yourusername/path/to/run_maintenance.sh
   ```

   Format: `period_days  delay_minutes  job_name  command`

5. **Test the anacron job:**

   ```bash
   sudo anacron -f -n
   ```

### Setting up Cron

If you prefer cron or have a system that's always running:

1. **Edit your crontab:**

   ```bash
   crontab -e
   ```

2. **Add a weekly job** (this example runs every Sunday at 2 AM):

   ```bash
   0 2 * * 0 /home/username/path/to/run_maintenance.sh
   ```

## What it actually does

The script runs these maintenance tasks:

1. **Update package lists** - `sudo apt update -y`
2. **Upgrade packages** - `sudo apt upgrade -y`  
3. **Remove unused packages** - `sudo apt autoremove -y`
4. **Clean package cache** - `sudo apt autoclean -y`

## Sudo acess

The script needs sudo access for package management. For automated runs, you need to set up passwordless sudo for specific commands. **I want to stress this is somewhat risky** - you're giving your user passwordless sudo access for these commands. Only do this if you understand what that means and you're okay with the security implications:

Instead of editing `/etc/sudoers` directly, you can add your rule to a new file in `/etc/sudoers.d/`

```bash
sudo nano /etc/sudoers.d/linux-maintenance
```

Add this line (replace `username` with your actual username):

```text
username ALL=(ALL) NOPASSWD: /usr/bin/apt update -y, /usr/bin/apt upgrade -y, /usr/bin/apt autoremove -y, /usr/bin/apt autoclean -y
```

Now set permissions:

```bash
sudo chmod 0440 /etc/sudoers.d/linux-maintenance
```

This keeps your configuration clean and separate from the main sudoers file.

## Logging

Logs get saved to the `logs/` directory:

- `logs/maintenance.log` - Everything that happened with timestamps
- Includes what commands ran, their output, and any errors
- The log folder gets created automatically if it doesn't exist

**Note:** The log rotation in `maintenance.py` is hardcoded to every Wednesday at midnight by default.  
If you set up your anacron  for a different day, youcan change the log rotation weekday (`when="W2"`) in the script to match your schedule.  
See the [Python logging documentation](https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler) for information.

## Requirements

- Python 3.9 or newer
- Ubuntu/Debian-based Linux distribution (uses `apt` package manager)
- `sudo` access for package management operations

## Troubleshooting

### Permission Issues

If you get permission errors when running automated tasks:

1. Double-check your sudoers configuration
2. Make sure the sudoers file has correct permissions: `sudo chmod 0440 /etc/sudoers`
3. Verify your username matches exactly in the sudoers file

### Desktop Notifications Not Working

If you're running this through anacron/cron, desktop notifications might not work because there's no display session. This is normal - check the logs instead.

### Anacron Job Not Running

- Check if anacron is running: `sudo systemctl status anacron`
- Look at anacron logs: `sudo journalctl -u anacron`
- Test manually: `sudo anacron -f -n`
