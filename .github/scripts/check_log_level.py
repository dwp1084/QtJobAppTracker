import sys
from pathlib import Path

import yaml

desired_log_levels = {
    "console": "WARNING",
    "file": "INFO"
}

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python check_log_levels.py <path-to-logging-config.yaml>")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    if not config_path.is_file():
        print(f"ERROR: Could not find {config_path}")
        sys.exit(1)

    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    handlers = config.get("handlers", {})

    if not handlers:
        print(f"ERROR: No handlers found in {config_path} - check the file is well-formed.")
        sys.exit(1)

    for handler_name, handler_config in handlers.items():
        if handler_name in desired_log_levels:
            level = str(handler_config.get("level", "")).strip().upper()
            if level != desired_log_levels[handler_name]:
                print(f"ERROR: Handler '{handler_name}' not set to the correct log level ({level} != {desired_log_levels[handler_name]}).",
                      "Please set all log handlers to the desired log levels as shown below before merging:",
                      sep="\n")
                for handler, level in desired_log_levels.items():
                    print(f"{handler} should be set to {level}")

                sys.exit(1)

    print(f"Log levels in {config_path} are set to the desired configuration. Ready for release.")


if __name__ == "__main__":
    main()