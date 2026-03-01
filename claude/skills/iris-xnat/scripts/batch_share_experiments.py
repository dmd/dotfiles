#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
# ]
# ///

"""
Share multiple IRIS (XNAT) experiments to a project (batch processing).

Reads identifiers from a file (one per line) or stdin and shares them to
the specified project. Provides progress tracking and summary statistics.

Usage:
    ./batch_share_experiments.py <target-project> <identifiers-file>
    ./batch_share_experiments.py webb_k23 identifiers.txt
    cat identifiers.txt | ./batch_share_experiments.py webb_k23 -

Examples:
    # Share from file
    ./batch_share_experiments.py webb_k23 identifiers.txt

    # Share from stdin
    cat identifiers.txt | ./batch_share_experiments.py webb_k23 -
    echo "E62622361" | ./batch_share_experiments.py webb_k23 -

Input file format:
    One identifier (label or ID) per line
    Empty lines and lines starting with # are ignored

Output:
    Progress messages to stderr
    Summary statistics at the end
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
    """Share an experiment (and its subject) to another project."""
    # Step 1: Share subject first (REQUIRED)
    subject_url = (
        f"{server}/data/projects/{source_project}/subjects/{subject_id}"
        f"/projects/{target_project}"
    )
    r = requests.put(subject_url, auth=auth)
    if r.status_code not in (200, 201, 409):
        r.raise_for_status()

    # Step 2: Share experiment
    exp_url = (
        f"{server}/data/projects/{source_project}/subjects/{subject_id}"
        f"/experiments/{experiment_id}/projects/{target_project}"
    )
    r = requests.put(exp_url, auth=auth)
    if r.status_code not in (200, 201, 409):
        r.raise_for_status()

    return True


def main():
    if len(sys.argv) != 3:
        print("Usage: batch_share_experiments.py <target-project> <identifiers-file>", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  batch_share_experiments.py webb_k23 identifiers.txt", file=sys.stderr)
        print("  cat identifiers.txt | batch_share_experiments.py webb_k23 -", file=sys.stderr)
        print("\nInput file format:", file=sys.stderr)
        print("  One identifier (label or ID) per line", file=sys.stderr)
        print("  Empty lines and lines starting with # are ignored", file=sys.stderr)
        sys.exit(1)

    target_project = sys.argv[1]
    identifiers_file = sys.argv[2]

    # Read identifiers
    if identifiers_file == "-":
        lines = sys.stdin.readlines()
    else:
        with open(identifiers_file, 'r') as f:
            lines = f.readlines()

    # Parse identifiers (skip empty lines and comments)
    identifiers = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            identifiers.append(line)

    if not identifiers:
        print("ERROR: No identifiers found in input", file=sys.stderr)
        sys.exit(1)

    print(f"Processing {len(identifiers)} identifiers...", file=sys.stderr)
    print(f"Target project: {target_project}", file=sys.stderr)
    print("="*80, file=sys.stderr)

    # Track results
    results = {
        "found": 0,
        "not_found": 0,
        "already_shared": 0,
        "newly_shared": 0,
        "errors": 0
    }

    # Process each identifier
    for i, identifier in enumerate(identifiers, 1):
        print(f"\n[{i}/{len(identifiers)}] Processing: {identifier}", file=sys.stderr)

        # Find experiment
        try:
            exp = find_experiment_by_identifier(identifier)
            if not exp:
                print(f"  ✗ Not found in IRIS", file=sys.stderr)
                results["not_found"] += 1
                continue

            experiment_id = exp["ID"]
            source_project = exp["project"]
            label = exp.get("label", "")

            print(f"  Found: {experiment_id} (label: {label})", file=sys.stderr)
            print(f"  Source project: {source_project}", file=sys.stderr)
            results["found"] += 1

            # Get subject information
            details = get_experiment_details(experiment_id)
            subject_id = details.get("subject_ID")

            if not subject_id:
                print(f"  ✗ Could not determine subject ID", file=sys.stderr)
                results["errors"] += 1
                continue

            # Check if already shared
            if source_project == target_project or is_in_project(experiment_id, target_project):
                print(f"  ✓ Already in/shared to {target_project}", file=sys.stderr)
                results["already_shared"] += 1
                continue

            # Share to target project
            share_to_project(experiment_id, source_project, target_project, subject_id)
            print(f"  ✓ Shared to {target_project}", file=sys.stderr)
            results["newly_shared"] += 1

        except Exception as e:
            print(f"  ✗ ERROR: {e}", file=sys.stderr)
            results["errors"] += 1

    # Print summary
    print("\n" + "="*80, file=sys.stderr)
    print("SUMMARY:", file=sys.stderr)
    print("="*80, file=sys.stderr)
    print(f"Total identifiers processed: {len(identifiers)}", file=sys.stderr)
    print(f"Found in IRIS: {results['found']}", file=sys.stderr)
    print(f"Not found in IRIS: {results['not_found']}", file=sys.stderr)
    print(f"Already in/shared to {target_project}: {results['already_shared']}", file=sys.stderr)
    print(f"Newly shared to {target_project}: {results['newly_shared']}", file=sys.stderr)
    print(f"Errors: {results['errors']}", file=sys.stderr)
    print("="*80, file=sys.stderr)

    # Exit with error code if there were any errors
    if results["errors"] > 0 or results["not_found"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
