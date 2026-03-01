#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
# ]
# ///

"""
Share an IRIS (XNAT) experiment to another project.

CRITICAL: This script automatically shares the subject first, as required by XNAT.

Usage:
    ./share_experiment.py <identifier> <target-project>
    ./share_experiment.py E62622361 webb_k23
    ./share_experiment.py XNAT_E12345 my_project

Examples:
    # Share experiment to webb_k23 project
    ./share_experiment.py E62622361 webb_k23

    # Share by experiment ID
    ./share_experiment.py XNAT_E12345 my_project

Exit codes:
    0 - Successfully shared (or already shared)
    1 - Error occurred
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


def get_experiment_details(experiment_id):
    """Get detailed information about an experiment."""
    r = requests.get(
        f"{server}/data/experiments/{experiment_id}?format=json",
        auth=auth
    )
    r.raise_for_status()

    data = r.json()
    if not data.get("items"):
        return None

    return data["items"][0]["data_fields"]


def is_in_project(experiment_id, project_id):
    """Check if an experiment is in or shared to a specific project."""
    r = requests.get(
        f"{server}/data/projects/{project_id}/experiments/{experiment_id}",
        auth=auth
    )
    return r.status_code == 200


def share_to_project(experiment_id, source_project, target_project, subject_id):
    """
    Share an experiment (and its subject) to another project.

    CRITICAL: Shares subject first, as required by XNAT.
    """
    # Step 1: Share subject first (REQUIRED)
    print(f"  Sharing subject {subject_id} to {target_project}...", file=sys.stderr)
    subject_url = (
        f"{server}/data/projects/{source_project}/subjects/{subject_id}"
        f"/projects/{target_project}"
    )
    r = requests.put(subject_url, auth=auth)

    # HTTP 409 = already exists, which is OK
    if r.status_code not in (200, 201, 409):
        print(f"  ERROR: Failed to share subject: {r.status_code}", file=sys.stderr)
        r.raise_for_status()

    if r.status_code == 409:
        print(f"  Subject already exists in {target_project}", file=sys.stderr)
    else:
        print(f"  ✓ Subject shared successfully", file=sys.stderr)

    # Step 2: Share experiment
    print(f"  Sharing experiment {experiment_id} to {target_project}...", file=sys.stderr)
    exp_url = (
        f"{server}/data/projects/{source_project}/subjects/{subject_id}"
        f"/experiments/{experiment_id}/projects/{target_project}"
    )
    r = requests.put(exp_url, auth=auth)

    if r.status_code not in (200, 201, 409):
        print(f"  ERROR: Failed to share experiment: {r.status_code}", file=sys.stderr)
        r.raise_for_status()

    if r.status_code == 409:
        print(f"  Experiment already exists in {target_project}", file=sys.stderr)
    else:
        print(f"  ✓ Experiment shared successfully", file=sys.stderr)

    return True


def main():
    if len(sys.argv) != 3:
        print("Usage: share_experiment.py <identifier> <target-project>", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  share_experiment.py E62622361 webb_k23", file=sys.stderr)
        print("  share_experiment.py XNAT_E12345 my_project", file=sys.stderr)
        sys.exit(1)

    identifier = sys.argv[1]
    target_project = sys.argv[2]

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

    # Get subject information
    details = get_experiment_details(experiment_id)
    subject_id = details.get("subject_ID")

    if not subject_id:
        print(f"ERROR: Could not determine subject ID", file=sys.stderr)
        sys.exit(1)

    print(f"Subject: {subject_id}", file=sys.stderr)

    # Check if already shared
    if source_project == target_project:
        print(f"\n✓ Experiment's primary project is already {target_project}")
        sys.exit(0)
    elif is_in_project(experiment_id, target_project):
        print(f"\n✓ Experiment is already shared to {target_project}")
        sys.exit(0)

    # Share to target project
    print(f"\nSharing to {target_project}...")
    try:
        share_to_project(experiment_id, source_project, target_project, subject_id)
        print(f"\n✓ SUCCESS: Experiment {label} is now shared to {target_project}")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ ERROR: Failed to share experiment: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
