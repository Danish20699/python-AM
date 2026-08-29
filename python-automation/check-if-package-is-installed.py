import os
import shutil
import subprocess
import sys

# Ensure WinGet's links folder is in PATH so newly installed tools are detected immediately
winget_links = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links")
if winget_links not in os.environ.get("PATH", ""):
    os.environ["PATH"] = winget_links + os.pathsep + os.environ.get("PATH", "")

# WinGet package IDs (PostgreSQL requires a version number like .17)
PACKAGES = {
    "git": "Git.Git",
    "nano": "GNU.Nano",
    "psql": "PostgreSQL.PostgreSQL.17"
}

def get_missing_packages():
    missing = []
    for cmd, pkg in PACKAGES.items():
        if shutil.which(cmd) is None:
            print(f"[MISSING] '{cmd}' is not installed.")
            missing.append(pkg)
        else:
            print(f"[FOUND]   '{cmd}' is already installed.")
    return missing

def install_packages(packages):
    if not packages:
        print("\nAll packages are already installed!")
        return

    print(f"\nInstalling missing packages: {', '.join(packages)}...")

    for pkg in packages:
        print(f"\n--- Installing {pkg} via winget ---")
        install_cmd = [
            "winget", "install",
            "--id", pkg,
            "-e",
            "--accept-source-agreements",
            "--accept-package-agreements"
        ]

        result = subprocess.run(install_cmd)
        
        # 0 = Success, 2316632107 / -1978335189 = Already installed / up to date
        if result.returncode in (0, 2316632107, -1978335189):
            print(f"[SUCCESS] {pkg} is installed.")
        else:
            print(f"[FAILED] Could not install {pkg} (exit code: {result.returncode})")

    print("\nInstallation finished!")

if __name__ == "__main__":
    missing_packages = get_missing_packages()
    if missing_packages:
        install_packages(missing_packages)





        