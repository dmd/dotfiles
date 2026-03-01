#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
# ]
# ///

"""
Query Orthanc for studies by MRN or accession number.

Usage:
    ./query_study.py --mrn 219306
    ./query_study.py --accession E62622361
    ./query_study.py --mrn 219306 --verbose
"""

import sys
import argparse
import requests
from datetime import datetime

SERVER = "http://micvna.mclean.harvard.edu:8042"


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


def get_study_info(study_id):
    """Get detailed study information including accession number and date."""
    r = requests.get(f"{SERVER}/studies/{study_id}")
    r.raise_for_status()
    study = r.json()

    # Get main tags
    main_tags = study.get("MainDicomTags", {})
    patient_tags = study.get("PatientMainDicomTags", {})

    # Get detailed tags if needed
    tags_response = requests.get(f"{SERVER}/studies/{study_id}/tags?simplify")
    if tags_response.ok:
        all_tags = tags_response.json()
    else:
        all_tags = {}

    return {
        "study_id": study_id,
        "date": main_tags.get("StudyDate", all_tags.get("StudyDate", "")),
        "accession_number": main_tags.get("AccessionNumber", all_tags.get("AccessionNumber", "")),
        "study_description": main_tags.get("StudyDescription", all_tags.get("StudyDescription", "")),
        "patient_id": patient_tags.get("PatientID", all_tags.get("PatientID", "")),
        "patient_name": patient_tags.get("PatientName", all_tags.get("PatientName", "")),
        "series_count": len(study.get("Series", []))
    }


def format_date(dicom_date):
    """Convert YYYYMMDD to MM/DD/YYYY for display."""
    if len(dicom_date) == 8:
        try:
            dt = datetime.strptime(dicom_date, "%Y%m%d")
            return dt.strftime("%m/%d/%Y")
        except ValueError:
            return dicom_date
    return dicom_date


def main():
    parser = argparse.ArgumentParser(
        description="Query Orthanc for studies by MRN or accession number",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --mrn 219306
  %(prog)s --accession E62622361
  %(prog)s --mrn 219306 --verbose
        """
    )
    parser.add_argument("--mrn", help="Patient MRN to search for")
    parser.add_argument("--accession", help="Accession number to search for")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed information")

    args = parser.parse_args()

    if not args.mrn and not args.accession:
        parser.error("Must provide either --mrn or --accession")

    try:
        # Search for studies
        if args.mrn:
            print(f"Searching for MRN: {args.mrn}", file=sys.stderr)
            studies = search_by_mrn(args.mrn)
        else:
            print(f"Searching for accession: {args.accession}", file=sys.stderr)
            studies = search_by_accession(args.accession)

        if not studies:
            print("No studies found", file=sys.stderr)
            return

        print(f"Found {len(studies)} study(ies)\n", file=sys.stderr)

        # Get details for each study
        for i, study in enumerate(studies, 1):
            study_id = study.get("ID")
            if not study_id:
                continue

            info = get_study_info(study_id)

            print(f"Study {i}:")
            print(f"  Study ID: {info['study_id']}")
            print(f"  Date: {format_date(info['date'])} ({info['date']})")
            print(f"  Accession: {info['accession_number']}")
            print(f"  Description: {info['study_description']}")
            print(f"  Patient ID: {info['patient_id']}")
            print(f"  Series Count: {info['series_count']}")

            if args.verbose:
                print(f"  Patient Name: {info['patient_name']}")

            print()

    except requests.exceptions.RequestException as e:
        print(f"Error querying Orthanc: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
