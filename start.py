import subprocess
import sys
import os

# ==============================================================================
# Intelligent, Cross-Platform Startup Script for Mobile Network QoE Tool
# ==============================================================================
# This Python script automates the setup and launch process, ensuring that all
# dependencies, database migrations, and initial data are in place before
# starting the application. It is designed to run on Windows, macOS, and Linux.
#
# It is idempotent, meaning it can be run safely multiple times.
# ==============================================================================

# --- Configuration ---
# Define colors for better output readability
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color

def run_command(command, description):
    """Runs a shell command and handles errors."""
    try:
        # Use shell=True for Windows compatibility with commands like 'flask'
        # On Unix, the command is passed as a list to avoid shell injection
        is_windows = sys.platform == "win32"
        subprocess.run(command, check=True, shell=is_windows, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"{Colors.RED}Error during: {description}{Colors.NC}")
        print(f"{Colors.RED}Command failed: {' '.join(command)}{Colors.NC}")
        # Decode stderr if it exists, otherwise provide a generic error
        stderr = e.stderr.decode('utf-8').strip() if hasattr(e, 'stderr') and e.stderr else 'Command not found or execution failed.'
        print(f"{Colors.RED}{stderr}{Colors.NC}")
        sys.exit(1)

def main():
    """Main function to orchestrate the startup process."""
    # Use 'python3' or 'python' depending on the OS
    python_executable = 'python3' if sys.platform != 'win32' else 'python'

    # --- Step 1: Check for and install dependencies ---
    print(f"{Colors.YELLOW}Step 1: Checking and installing dependencies...{Colors.NC}")
    run_command([python_executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 'Dependency Installation')
    print(f"{Colors.GREEN}Dependencies are up to date.{Colors.NC}\n")

    # --- Step 2: Initialize and migrate the database ---
    print(f"{Colors.YELLOW}Step 2: Setting up the database...{Colors.NC}")
    if not os.path.isdir('migrations'):
        print("Migrations directory not found. Initializing database...")
        run_command(['flask', 'db', 'init'], 'Database Initialization')
        run_command(['flask', 'db', 'migrate', '-m', 'Initial database setup'], 'Initial Migration')
    
    run_command(['flask', 'db', 'upgrade'], 'Database Migration')
    print(f"{Colors.GREEN}Database is up to date.{Colors.NC}\n")

    # --- Step 3: Seed database and ensure admin user exists ---
    print(f"{Colors.YELLOW}Step 3: Seeding data and ensuring default admin user exists...{Colors.NC}")
    run_command(['flask', 'setup-all'], 'Data Seeding')
    print(f"{Colors.GREEN}Initial data is in place.{Colors.NC}\n")

    # --- Step 4: Start the application ---
    print(f"{Colors.YELLOW}Step 4: Launching the Mobile Network QoE Tool...{Colors.NC}")
    print("You can access the application at http://127.0.0.1:5000")
    print("Press CTRL+C to stop the server.")
    
    try:
        # Use subprocess.call to run flask and wait for it to complete
        is_windows = sys.platform == "win32"
        subprocess.call(['flask', 'run'], shell=is_windows)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Server stopped.{Colors.NC}")
        sys.exit(0)

if __name__ == '__main__':
    main()
