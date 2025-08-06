# SPDX-FileCopyrightText: 2025 Florian Obersteiner / KIT
# SPDX-FileContributor: Florian Obersteiner <f.obersteiner@kit.edu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import tomllib

PYPROJECT_PATH = "pyproject.toml"  # assume script runs in root


def get_version() -> str:
    """
    Reads the version from the pyproject.toml file.
    Supports both the standard [project] section and [tool.poetry].
    """
    try:
        with open(PYPROJECT_PATH, "rb") as fd:
            data = tomllib.load(fd)

            # Try the standard [project] section first (PEP 621)
            if "project" in data and "version" in data["project"]:
                return data["project"]["version"]

            # Then try the [tool.poetry] section (if using Poetry)
            elif (
                "tool" in data and "poetry" in data["tool"] and "version" in data["tool"]["poetry"]
            ):
                return data["tool"]["poetry"]["version"]

            else:
                print(
                    f"Error: Could not find version field in [project] or [tool.poetry] in {PYPROJECT_PATH}",
                    file=sys.stderr,
                )
                sys.exit(1)

    except FileNotFoundError:
        print(f"Error: {PYPROJECT_PATH} not found.", file=sys.stderr)
        sys.exit(1)
    except tomllib.TOMLDecodeError as e:
        print(f"Error parsing {PYPROJECT_PATH}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    version = get_version()
    if version:
        print(version)
