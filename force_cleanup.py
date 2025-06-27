import os
import shutil

# ==============================================================================
# Force Cleanup Script
# ==============================================================================
# This script forcefully removes all database-related artifacts to ensure a
# clean slate for application startup. It is designed to be run when the
# database or migration history is in a corrupted state.
# ==============================================================================

class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'

def force_delete(path):
    """Forcefully deletes a file or directory, ignoring if it doesn't exist."""
    try:
        if os.path.isfile(path) or os.path.islink(path):
            os.unlink(path)
            print(f"{Colors.GREEN}Deleted file: {path}{Colors.NC}")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            print(f"{Colors.GREEN}Deleted directory: {path}{Colors.NC}")
    except Exception as e:
        print(f"{Colors.RED}Error deleting {path}: {e}{Colors.NC}")

def main():
    """Finds and deletes all specified artifacts."""
    print(f"{Colors.YELLOW}--- Starting Force Cleanup ---{Colors.NC}")
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Artifacts to delete
    artifacts_to_delete = [
        'migrations',
        'instance',
        'Mobile_qoe.db',
        'mtn_qoe.db',
        'app.db' # Just in case
    ]

    # Also find any other .db files and backups
    for item in os.listdir(project_root):
        if item.endswith('.db') or item.startswith('mtn_qoe.db.backup'):
            if item not in artifacts_to_delete:
                artifacts_to_delete.append(item)

    for artifact in artifacts_to_delete:
        path = os.path.join(project_root, artifact)
        if os.path.exists(path):
            force_delete(path)
        else:
            print(f"{Colors.YELLOW}Artifact not found, skipping: {path}{Colors.NC}")
            
    print(f"\n{Colors.GREEN}--- Cleanup Complete ---{Colors.NC}")

if __name__ == '__main__':
    main()
