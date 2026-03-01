#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
# ]
# ///

"""
List all studies for a patient with detailed information.

Usage:
    ./list_patient_studies.py --mrn 219306
    ./list_patient_studies.py --mrn 219306 --verbose
    ./list_patient_studies.py --mrn 219306 --show-series
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
        "time": main_tags.get("StudyTime", all_tags.get("StudyTime", "")),
        "accession_number": main_tags.get("AccessionNumber", all_tags.get("AccessionNumber", "")),
        "study_description": main_tags.get("StudyDescription", all_tags.get("StudyDescription", "")),
        "patient_id": patient_tags.get("PatientID", all_tags.get("PatientID", "")),
        "patient_name": patient_tags.get("PatientName", all_tags.get("PatientName", "")),
        "patient_birth_date": patient_tags.get("PatientBirthDate", all_tags.get("PatientBirthDate", "")),
        "series_count": len(study.get("Series", []))
    }


def get_series_details(study_id):
    """Get all series for a study with image counts."""
    r = requests.get(f"{SERVER}/studies/{study_id}")
    r.raise_for_status()
    study = r.json()

    series_ids = study.get("Series", [])

    series_details = []
    for series_id in series_ids:
        series_r = requests.get(f"{SERVER}/series/{series_id}")
        series_r.raise_for_status()
        series = series_r.json()

        main_tags = series.get("MainDicomTags", {})
        series_number = main_tags.get("SeriesNumber", "Unknown")
        series_desc = main_tags.get("SeriesDescription", "No description")
        modality = main_tags.get("Modality", "Unknown")

        instances = series.get("Instances", [])
        image_count = len(instances)

        series_details.append({
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


def format_date(dicom_date):
    """Convert YYYYMMDD to MM/DD/YYYY for display."""
    if len(dicom_date) == 8:
        try:
            dt = datetime.strptime(dicom_date, "%Y%m%d")
            return dt.strftime("%m/%d/%Y")
        except ValueError:
            return dicom_date
    return dicom_date


def format_time(dicom_time):
    """Convert HHMMSS or HHMMSS.ffffff to HH:MM:SS for display."""
    if not dicom_time:
        return ""
    # Remove fractional seconds if present
    time_str = dicom_time.split('.')[0]
    if len(time_str) >= 6:
        return f"{time_str[0:2]}:{time_str[2:4]}:{time_str[4:6]}"
    return time_str


def main():
    parser = argparse.ArgumentParser(
        description="List all studies for a patient with detailed information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --mrn 219306
  %(prog)s --mrn 219306 --verbose
  %(prog)s --mrn 219306 --show-series
        """
    )
    parser.add_argument("--mrn", required=True, help="Patient MRN")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show verbose patient information")
    parser.add_argument("--show-series", action="store_true",
                        help="Show series details for each study")

    args = parser.parse_args()

    try:
        # Search for studies
        print(f"Searching for MRN: {args.mrn}", file=sys.stderr)
        studies = search_by_mrn(args.mrn)

        if not studies:
            print("No studies found", file=sys.stderr)
            return

        print(f"Found {len(studies)} study(ies)\n", file=sys.stderr)

        # Get patient info from first study
        if studies and args.verbose:
            first_info = get_study_info(studies[0].get("ID"))
            print("=" * 80)
            print("PATIENT INFORMATION")
            print("=" * 80)
            print(f"Patient ID (MRN): {first_info['patient_id']}")
            print(f"Patient Name: {first_info['patient_name']}")
            if first_info['patient_birth_date']:
                print(f"Birth Date: {format_date(first_info['patient_birth_date'])}")
            print()

        # Sort studies by date
        study_details = []
        for study in studies:
            study_id = study.get("ID")
            if study_id:
                info = get_study_info(study_id)
                study_details.append(info)

        # Sort by date
        study_details.sort(key=lambda x: x['date'], reverse=True)

        # Display studies
        print("=" * 80)
        print("STUDIES")
        print("=" * 80)

        for i, info in enumerate(study_details, 1):
            print(f"\nStudy {i}:")
            print(f"  Date: {format_date(info['date'])} ({info['date']})")
            if info['time']:
                print(f"  Time: {format_time(info['time'])}")
            print(f"  Accession: {info['accession_number'] or 'N/A'}")
            print(f"  Description: {info['study_description'] or 'N/A'}")
            print(f"  Series Count: {info['series_count']}")

            if args.verbose:
                print(f"  Study ID: {info['study_id']}")

            if args.show_series and info['series_count'] > 0:
                print(f"\n  Series:")
                series_list = get_series_details(info['study_id'])
                for j, series in enumerate(series_list, 1):
                    print(f"    {j}. #{series['series_number']}: {series['description']}")
                    print(f"       Modality: {series['modality']}, Images: {series['image_count']}")

        print("\n" + "=" * 80)
        print(f"Total: {len(study_details)} studies")
        print("=" * 80)

    except requests.exceptions.RequestException as e:
        print(f"Error querying Orthanc: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
