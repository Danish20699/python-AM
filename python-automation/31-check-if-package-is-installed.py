import sys
import shutil



def check_package(package_name):
    """Checks if a given package/executable exists on the system."""
    path = shutil.which(package_name)
    
    if path:
        print(f"\n[FOUND] 🟢 '{package_name}' is installed!")
        print(f"Location: {path}\n")
        return True
    else:
        print(f"\n[MISSING] 🔴 '{package_name}' is NOT installed on this system.\n")
        return False

def main():
    if len(sys.argv) < 2:
        print("Error: No package name provided.")
        print("Usage: python 31-check-if-package-is-installed.py <package_name>")
        sys.exit(1)
    pkg = sys.argv[1]
    check_package(pkg)
if __name__ == "__main__":
    main()

