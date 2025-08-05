import os
import sys

def is_package_installed_in_site_packages(site_packages_path, package_name):
    # Check for both: package folders (e.g., pandas/) or .dist-info directories
    candidates = os.listdir(site_packages_path)
    package_name = package_name.lower()
    for item in candidates:
        if item.lower() == package_name or item.lower().startswith(package_name + "-") and item.endswith(".dist-info"):
            return True
    return False

def search_package(package_name):
    base_dirs = [
        os.path.expanduser("~"),
        os.path.join(os.environ.get("USERPROFILE", ""), ".virtualenvs"),
        os.path.join(os.environ.get("USERPROFILE", ""), "Envs"),
        os.path.join(os.environ.get("USERPROFILE", ""), "Desktop", "projects"),
    ]

    print(f"\n🔍 Searching for package '{package_name}'...\n")
    found_envs = dict()

    for base in base_dirs:
        if not os.path.exists(base):
            continue
        for root, dirs, files in os.walk(base):
            if "site-packages" in root:
                if is_package_installed_in_site_packages(root, package_name):
                    # Go back to the venv root by trimming after "Lib" or "lib"
                    parts = root.split(os.sep)
                    if "Lib" in parts:
                        lib_index = parts.index("Lib")
                    elif "lib" in parts:
                        lib_index = parts.index("lib")
                    else:
                        continue
                    env_path = os.sep.join(parts[:lib_index])
                    normalized_env = os.path.normcase(env_path)
                    if normalized_env not in found_envs:
                        found_envs[normalized_env] = env_path

    if found_envs:
        print(f"✅ Package '{package_name}' found at:\n")
        for env in sorted(found_envs.values()):
            print(f"→ {env}")
    else:
        print(f"❌ Package '{package_name}' not found in known virtual environments.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:\n  python -m findpkg <package_name>")
    else:
        search_package(sys.argv[1])