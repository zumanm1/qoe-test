import subprocess
import sys
import os

# ==============================================================================
# Robust, Cross-Platform Startup Script for Mobile Network QoE Tool
# ==============================================================================
# This script uses a programmatic setup approach to avoid CLI-related issues.
# ==============================================================================

class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'

def run_command(command, description, env=None):
    """Runs a shell command and handles errors."""
    cmd_env = os.environ.copy()
    if env:
        cmd_env.update(env)
    try:
        is_windows = sys.platform == "win32"
        subprocess.run(command, check=True, shell=is_windows, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=cmd_env)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"{Colors.RED}Error during: {description}{Colors.NC}")
        print(f"{Colors.RED}Command failed: {' '.join(command)}{Colors.NC}")
        stderr = e.stderr.decode('utf-8').strip() if hasattr(e, 'stderr') and e.stderr else 'Command not found or execution failed.'
        print(f"{Colors.RED}{stderr}{Colors.NC}")
        sys.exit(1)

def main():
    """Orchestrates the entire setup and launch process."""
    python_executable = 'python3' if sys.platform != 'win32' else 'python'
    flask_env = {'FLASK_APP': 'run.py'}

    print(f"{Colors.YELLOW}--- Step 1: Installing Dependencies ---{Colors.NC}")
    run_command([python_executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 'Dependency Installation')
    print(f"{Colors.GREEN}Dependencies are up to date.{Colors.NC}\n")

    print(f"{Colors.YELLOW}--- Step 2: Running Database Migrations ---{Colors.NC}")
    if not os.path.isdir('migrations'):
        print("Migrations directory not found. Initializing...")
        run_command(['flask', 'db', 'init'], 'Database Initialization', env=flask_env)
        run_command(['flask', 'db', 'migrate', '-m', 'Initial database setup'], 'Initial Migration', env=flask_env)
    run_command(['flask', 'db', 'upgrade'], 'Database Migration', env=flask_env)
    print(f"{Colors.GREEN}Database schema is up to date.{Colors.NC}\n")

    print(f"{Colors.YELLOW}--- Step 3: Seeding Database Programmatically ---{Colors.NC}")
    run_command([python_executable, 'setup.py'], 'Programmatic Data Seeding')
    print(f"{Colors.GREEN}Database is seeded.{Colors.NC}\n")

    print(f"{Colors.YELLOW}--- Step 4: Launching Application ---{Colors.NC}")
    print("You can access the application at http://127.0.0.1:5000")
    print("Press CTRL+C to stop the server.")
    try:
        subprocess.call([python_executable, 'run.py'])
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Server stopped.{Colors.NC}")
        sys.exit(0)

if __name__ == '__main__':
    main()

