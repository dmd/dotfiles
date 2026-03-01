#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
# ]
# ///

"""
Get scan details with accurate file counts for an IRIS (XNAT) experiment.

CRITICAL: The 'frames' field in scan summaries is unreliable (often 0).
This script queries scan resources to get accurate file counts.

Usage:
    ./get_scan_details.py <identifier>
    ./get_scan_details.py E62622361
    ./get_scan_details.py XNAT_E12345

Examples:
    # Get scan details for an experiment by label
    ./get_scan_details.py E62622361

    # Get scan details for an experiment by ID
    ./get_scan_details.py XNAT_E12345

Returns scan details with accurate file counts as JSON.
"""

import requests
import sys
import json

server = "https://iris.mclean.harvard.edu"
auth = ("zabbix", "iliketoeatcats")


def find_experiment_by_identifier(identifier):
    """Find experiment by identifier (label or accession)."""
    r = requests.get(f"{server}/data/experiments", auth=auth)
    r.raise_for_status()

    data = r.json()
    results = data.get("ResultSet", {}).get("Result", [])

    # Search for matching label or ID
    for exp in results:
        if exp.get("label") == identifier or exp.get("ID") == identifier:
            return exp

    return None


def get_scan_details_with_file_counts(experiment_id):
    """
    Get all scans for an experiment with accurate file counts.

    IMPORTANT: Do NOT use the 'frames' field - it's often 0 or incorrect!
    Always query scan resources to get actual file counts.
    """
    # Get scans summary
    scans_r = requests.get(
        f"{server}/data/experiments/{experiment_id}/scans",
        auth=auth
    )
    scans_r.raise_for_status()

    scans_data = scans_r.json()
    scans = scans_data.get("ResultSet", {}).get("Result", [])

    scan_details = []
    total_files = 0

    for scan in scans:
        scan_id = scan.get("ID")
        scan_type = scan.get("type", "Unknown")
        series_desc = scan.get("series_description", "Unknown")

        # Get resources for accurate file count
        resources_r = requests.get(
            f"{server}/data/experiments/{experiment_id}/scans/{scan_id}/resources",
            auth=auth
        )

        file_count = 0
        resources_info = []
        if resources_r.status_code == 200:
            resources_data = resources_r.json()
            resources = resources_data.get("ResultSet", {}).get("Result", [])

            # Sum file counts across all resources (DICOM, NIFTI, etc.)
            for resource in resources:
                resource_file_count = int(resource.get("file_count", 0))
                file_count += resource_file_count
                resources_info.append({
                    "label": resource.get("label", "Unknown"),
                    "format": resource.get("format", "Unknown"),
                    "file_count": resource_file_count
                })

        total_files += file_count

        scan_details.append({
            "scan_id": scan_id,
            "type": scan_type,
            "series_description": series_desc,
            "file_count": file_count,
            "resources": resources_info
        })

    return scan_details, total_files


def main():
    if len(sys.argv) != 2:
        print("Usage: get_scan_details.py <identifier>", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  get_scan_details.py E62622361    # By session label", file=sys.stderr)
        print("  get_scan_details.py XNAT_E12345  # By experiment ID", file=sys.stderr)
        sys.exit(1)

    identifier = sys.argv[1]

    print(f"Searching for identifier: {identifier}", file=sys.stderr)

    # Find the experiment
    exp = find_experiment_by_identifier(identifier)
    if not exp:
        print(f"ERROR: Identifier '{identifier}' not found in IRIS", file=sys.stderr)
        sys.exit(1)

    experiment_id = exp["ID"]
    label = exp.get("label", "")

    print(f"Found experiment: {experiment_id} (label: {label})", file=sys.stderr)
    print("Querying scan resources for accurate file counts...", file=sys.stderr)

    # Get scan details with accurate file counts
    scan_details, total_files = get_scan_details_with_file_counts(experiment_id)

    print(f"\nFound {len(scan_details)} scans with {total_files} total files", file=sys.stderr)
    print("="*80, file=sys.stderr)

    # Output detailed results as JSON to stdout
    result = {
        "experiment_id": experiment_id,
        "label": label,
        "total_scans": len(scan_details),
        "total_files": total_files,
        "scans": scan_details
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
