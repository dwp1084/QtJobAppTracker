import importlib.util
import os
import sys

from packaging.version import Version, InvalidVersion


def load_version_string(version_file: str) -> str:
    if not os.path.isfile(version_file):
        print(f"ERROR: Could not find version file {version_file}")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("project_version", version_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    try:
        return module.CURRENT_APP_VERSION
    except AttributeError:
        print(f"ERROR: Could not find CURRENT_APP_VERSION in {version_file}")
        sys.exit(1)


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: python check_rel_version.py <path_to_version_file>")
        sys.exit(1)

    version_file = sys.argv[1]
    version_str = load_version_string(version_file)
    print(f"Found version {version_str}")

    try:
        version = Version(version_str)
    except InvalidVersion:
        print(f"ERROR: Version {version_str} is an invalid version string")
        sys.exit(1)

    if version.is_devrelease or version.is_prerelease:
        print(
            f"ERROR: Version '{version_str}' is a dev/pre-release build "
            f"(dev={version.dev}, pre={version.pre}). Bump to a release "
            "version before merging to main."
        )
        sys.exit(1)

    print(f"Version '{version_str}' is a clean release build. OK.")


if __name__ == "__main__":
    main()