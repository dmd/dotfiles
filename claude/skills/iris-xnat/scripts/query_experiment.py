#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
# ]
# ///

"""
Query IRIS (XNAT) for experiments by label or accession number.

Usage:
    ./query_experiment.py <identifier>
    ./query_experiment.py E62622361
    ./query_experiment.py 00048130

Examples:
    # Query by session label
    ./query_experiment.py E62622361

    # Query by accession (less reliable)
    ./query_experiment.py 00048130

Returns experiment details as JSON if found.
"""

import requests
import sys
import json

server = "https://iris.mclean.harvard.edu"
auth = ("zabbix", "iliketoeatcats")


def find_experiment_by_identifier(identifier):
    """
    Find experiment by identifier (tries label first, then accession).

    IMPORTANT: The 'accession' parameter is unreliable - it often returns
    ALL experiments. Always search by label first.
    """
    # First, try searching by label (most reliable)
    r = requests.get(f"{server}/data/experiments", auth=auth)
    r.raise_for_status()

    data = r.json()
    results = data.get("ResultSet", {}).get("Result", [])

    # Search for matching label
    for exp in results:
        if exp.get("label") == identifier:
            return exp

    # If not found by label, check actual accession fields
    for exp in results:
        exp_id = exp.get("ID")
        detail_r = requests.get(
            f"{server}/data/experiments/{exp_id}?format=json",
            auth=auth
        )
        if detail_r.status_code == 200:
            detail_data = detail_r.json()
            if detail_data.get("items"):
                fields = detail_data["items"][0]["data_fields"]
                if fields.get("accession") == identifier:
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


def main():
    if len(sys.argv) != 2:
        print("Usage: query_experiment.py <identifier>", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  query_experiment.py E62622361  # Query by session label", file=sys.stderr)
        print("  query_experiment.py 00048130   # Query by accession", file=sys.stderr)
        sys.exit(1)

    identifier = sys.argv[1]

    print(f"Searching for identifier: {identifier}", file=sys.stderr)

    # Find the experiment
    exp = find_experiment_by_identifier(identifier)
    if not exp:
        print(f"ERROR: Identifier '{identifier}' not found in IRIS", file=sys.stderr)
        sys.exit(1)

    experiment_id = exp["ID"]
    project = exp["project"]
    label = exp.get("label", "")

    print(f"Found experiment: {experiment_id}", file=sys.stderr)
    print(f"  Project: {project}", file=sys.stderr)
    print(f"  Label: {label}", file=sys.stderr)

    # Get detailed information
    details = get_experiment_details(experiment_id)
    if details:
        subject_id = details.get("subject_ID", "")
        date = details.get("date", "")
        print(f"  Subject: {subject_id}", file=sys.stderr)
        print(f"  Date: {date}", file=sys.stderr)

    # Output full experiment data as JSON to stdout
    print("\n" + "="*80, file=sys.stderr)
    combined = {**exp, "details": details}
    print(json.dumps(combined, indent=2))


if __name__ == "__main__":
    main()
