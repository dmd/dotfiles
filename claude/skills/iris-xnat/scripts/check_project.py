#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
# ]
# ///

"""
Check if an IRIS (XNAT) experiment is in a specific project.

Usage:
    ./check_project.py <identifier> <project-id>
    ./check_project.py E62622361 webb_k23
    ./check_project.py XNAT_E12345 webb_k23

Examples:
    # Check if experiment is in webb_k23 project
    ./check_project.py E62622361 webb_k23

    # Check experiment by ID
    ./check_project.py XNAT_E12345 my_project

Exit codes:
    0 - Experiment is in the project
    1 - Experiment is not in the project or not found
"""

import requests
import sys

server = "https://iris.mclean.harvard.edu"
auth = ("zabbix", "iliketoeatcats")


def find_experiment_by_identifier(identifier):
    """Find experiment by identifier (label or ID)."""
    r = requests.get(f"{server}/data/experiments", auth=auth)
    r.raise_for_status()

    data = r.json()
    results = data.get("ResultSet", {}).get("Result", [])

    # Search for matching label or ID
    for exp in results:
        if exp.get("label") == identifier or exp.get("ID") == identifier:
            return exp

    return None


def is_in_project(experiment_id, project_id):
    """Check if an experiment is in or shared to a specific project."""
    r = requests.get(
        f"{server}/data/projects/{project_id}/experiments/{experiment_id}",
        auth=auth
    )

    # 200 = experiment exists in/is shared to this project
    # 404 = experiment is not in this project
    return r.status_code == 200


def main():
    if len(sys.argv) != 3:
        print("Usage: check_project.py <identifier> <project-id>", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  check_project.py E62622361 webb_k23", file=sys.stderr)
        print("  check_project.py XNAT_E12345 my_project", file=sys.stderr)
        print("\nExit codes:", file=sys.stderr)
        print("  0 - Experiment is in the project", file=sys.stderr)
        print("  1 - Experiment is not in the project or not found", file=sys.stderr)
        sys.exit(1)

    identifier = sys.argv[1]
    project_id = sys.argv[2]

    print(f"Searching for identifier: {identifier}", file=sys.stderr)

    # Find the experiment
    exp = find_experiment_by_identifier(identifier)
    if not exp:
        print(f"ERROR: Identifier '{identifier}' not found in IRIS", file=sys.stderr)
        sys.exit(1)

    experiment_id = exp["ID"]
    source_project = exp["project"]
    label = exp.get("label", "")

    print(f"Found experiment: {experiment_id} (label: {label})", file=sys.stderr)
    print(f"Source project: {source_project}", file=sys.stderr)

    # Check if in target project
    if source_project == project_id:
        print(f"\n✓ Experiment's primary project is {project_id}")
        sys.exit(0)
    elif is_in_project(experiment_id, project_id):
        print(f"\n✓ Experiment is shared to project {project_id}")
        sys.exit(0)
    else:
        print(f"\n✗ Experiment is NOT in project {project_id}")
        sys.exit(1)


if __name__ == "__main__":
    main()
