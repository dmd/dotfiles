#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
# ]
# ///

"""
Get series details with image counts for a study.

Usage:
    ./get_series_details.py --accession E62622361
    ./get_series_details.py --study-id <orthanc-study-id>
    ./get_series_details.py --mrn 219306 --date 01/16/2016
"""

import sys
import argparse
import requests
from datetime import datetime

SERVER = "http://micvna.mclean.harvard.edu:8042"


def search_by_accession(accession_number):
    """Search for studies by accession number in Orthanc."""
    query = {
        "Level": "Study",
        "Query": {
            "AccessionNumber": accession_number
        },
        "Expand": True
    }

    r = requests.post(f"{SERVER}/tools/find", json=query)
    r.raise_for_status()
    return r.json()


def search_by_mrn(patient_id):
    """Search for studies by patient ID (MRN) in Orthanc."""
    query = {
        "Level": "Study",
        "Query": {
            "PatientID": patient_id
        },
        "Expand": True
    }

    r = requests.post(f"{SERVER}/tools/find", json=query)
    r.raise_for_status()
    return r.json()


def parse_date(date_str):
    """Convert MM/DD/YYYY to YYYYMMDD for DICOM comparison."""
    dt = datetime.strptime(date_str.strip(), "%m/%d/%Y")
    return dt.strftime("%Y%m%d")


def get_study_date(study_id):
    """Get the study date from a study ID."""
    r = requests.get(f"{SERVER}/studies/{study_id}")
    r.raise_for_status()
    study = r.json()

    main_tags = study.get("MainDicomTags", {})
    return main_tags.get("StudyDate", "")


def get_series_details(study_id):
    """
    Get all series for a study with image counts.

    IMPORTANT:
    - Call /studies/{id} to get the study, which includes Series IDs
    - Then call /series/{id} for each series to get details
    - Do NOT use /studies/{id}/series?expand=True (not supported)
    """
    # Get study details which includes Series array
    r = requests.get(f"{SERVER}/studies/{study_id}")
    r.raise_for_status()
    study = r.json()

    series_ids = study.get("Series", [])

    series_details = []
    for series_id in series_ids:
        # Get detailed series information
        series_r = requests.get(f"{SERVER}/series/{series_id}")
        series_r.raise_for_status()
        series = series_r.json()

        main_tags = series.get("MainDicomTags", {})
        series_number = main_tags.get("SeriesNumber", "Unknown")
        series_desc = main_tags.get("SeriesDescription", "No description")
        modality = main_tags.get("Modality", "Unknown")

        # Get image count from Instances array
        instances = series.get("Instances", [])
        image_count = len(instances)

        series_details.append({
            "series_id": series_id,
            "series_number": series_number,
            "description": series_desc,
            "modality": modality,
            "image_count": image_count
        })

    # Sort by series number
    series_details.sort(key=lambda x: (
        int(x["series_number"]) if str(x["series_number"]).isdigit() else 999999,
        x["series_number"]
    ))

    return series_details


def main():
    parser = argparse.ArgumentParser(
        description="Get series details with image counts for a study",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --accession E62622361
  %(prog)s --study-id a1b2c3d4-e5f6-7890-abcd-ef1234567890
  %(prog)s --mrn 219306 --date 01/16/2016
        """
    )
    parser.add_argument("--accession", help="Accession number to search for")
    parser.add_argument("--study-id", help="Orthanc study ID")
    parser.add_argument("--mrn", help="Patient MRN")
    parser.add_argument("--date", help="Study date in MM/DD/YYYY format (required with --mrn)")

    args = parser.parse_args()

    # Validate arguments
    if not args.accession and not args.study_id and not args.mrn:
        parser.error("Must provide --accession, --study-id, or --mrn with --date")

    if args.mrn and not args.date:
        parser.error("--date is required when using --mrn")

    try:
        # Find the study
        study_id = None

        if args.study_id:
            study_id = args.study_id
            print(f"Using study ID: {study_id}", file=sys.stderr)

        elif args.accession:
            print(f"Searching for accession: {args.accession}", file=sys.stderr)
            studies = search_by_accession(args.accession)

            if not studies:
                print("No studies found with that accession number", file=sys.stderr)
                sys.exit(1)

            study_id = studies[0].get("ID")
            print(f"Found study ID: {study_id}", file=sys.stderr)

        elif args.mrn:
            print(f"Searching for MRN: {args.mrn}", file=sys.stderr)
            studies = search_by_mrn(args.mrn)

            if not studies:
                print("No studies found for that MRN", file=sys.stderr)
                sys.exit(1)

            # Find study matching the date
            target_date = parse_date(args.date)
            print(f"Looking for study on {args.date} ({target_date})", file=sys.stderr)

            for study in studies:
                sid = study.get("ID")
                if sid:
                    study_date = get_study_date(sid)
                    if study_date == target_date:
                        study_id = sid
                        break

            if not study_id:
                print(f"No study found for MRN {args.mrn} on {args.date}", file=sys.stderr)
                sys.exit(1)

            print(f"Found study ID: {study_id}", file=sys.stderr)

        # Get series details
        print(f"\nRetrieving series details...", file=sys.stderr)
        series_list = get_series_details(study_id)

        print(f"\nNumber of series: {len(series_list)}\n")
        print("Series details:")
        print("-" * 80)

        for i, series_info in enumerate(series_list, 1):
            print(f"{i}. Series #{series_info['series_number']}: {series_info['description']}")
            print(f"   Modality: {series_info['modality']}")
            print(f"   Images: {series_info['image_count']}")
            print(f"   Series ID: {series_info['series_id']}")
            print()

    except requests.exceptions.RequestException as e:
        print(f"Error querying Orthanc: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
