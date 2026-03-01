#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
# ]
# ///

"""
List all experiments in an IRIS (XNAT) project.

Usage:
    ./list_project_experiments.py <project-id>
    ./list_project_experiments.py webb_k23

Examples:
    # List all experiments in webb_k23
    ./list_project_experiments.py webb_k23

    # List experiments in JSON format
    ./list_project_experiments.py my_project

Returns experiment list as JSON.
"""

import requests
import sys
import json

server = "https://iris.mclean.harvard.edu"
auth = ("zabbix", "iliketoeatcats")


def get_project_experiments(project_id):
    """Get all experiments in a specific project."""
    r = requests.get(
        f"{server}/data/projects/{project_id}/experiments",
        auth=auth
    )
    r.raise_for_status()

    data = r.json()
    return data.get("ResultSet", {}).get("Result", [])


def main():
    if len(sys.argv) != 2:
        print("Usage: list_project_experiments.py <project-id>", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  list_project_experiments.py webb_k23", file=sys.stderr)
        print("  list_project_experiments.py my_project", file=sys.stderr)
        sys.exit(1)

    project_id = sys.argv[1]

    print(f"Fetching experiments for project: {project_id}", file=sys.stderr)

    try:
        experiments = get_project_experiments(project_id)
        print(f"Found {len(experiments)} experiments in {project_id}", file=sys.stderr)
        print("="*80, file=sys.stderr)

        # Output as JSON to stdout
        result = {
            "project": project_id,
            "count": len(experiments),
            "experiments": experiments
        }
        print(json.dumps(result, indent=2))

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"ERROR: Project '{project_id}' not found", file=sys.stderr)
        else:
            print(f"ERROR: HTTP {e.response.status_code}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
