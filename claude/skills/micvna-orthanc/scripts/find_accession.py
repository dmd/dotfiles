#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
# ]
# ///

"""
Find accession numbers for studies by MRN and date.

Supports single queries or batch processing from a file.

Usage:
    # Single query
    ./find_accession.py --mrn 219306 --date 01/16/2016

    # Batch from file (tab-delimited with MRN and Date columns)
    ./find_accession.py --input patients.txt --output results.txt
"""

import sys
import argparse
import requests
import csv
from datetime import datetime

SERVER = "http://micvna.mclean.harvard.edu:8042"


def search_patient(patient_id):
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

    # Get detailed tags if needed
    tags_response = requests.get(f"{SERVER}/studies/{study_id}/tags?simplify")
    if tags_response.ok:
        all_tags = tags_response.json()
    else:
        all_tags = {}

    return {
        "date": main_tags.get("StudyDate", all_tags.get("StudyDate", "")),
        "accession_number": main_tags.get("AccessionNumber", all_tags.get("AccessionNumber", "")),
        "study_description": main_tags.get("StudyDescription", all_tags.get("StudyDescription", ""))
    }


def parse_date(date_str):
    """Convert MM/DD/YYYY to YYYYMMDD for DICOM comparison."""
    dt = datetime.strptime(date_str.strip(), "%m/%d/%Y")
    return dt.strftime("%Y%m%d")


def find_accession_for_date(mrn, target_date_yyyymmdd):
    """Find accession number for specific MRN and study date."""
    studies = search_patient(mrn)

    for study in studies:
        study_id = study.get("ID")
        if not study_id:
            continue

        info = get_study_info(study_id)
        if info.get("date") == target_date_yyyymmdd:
            return info.get("accession_number", "")

    return ""  # Not found


def process_single(mrn, date_str):
    """Process a single MRN/date combination."""
    try:
        dicom_date = parse_date(date_str)
        print(f"Searching for MRN {mrn} on {date_str} ({dicom_date})...", file=sys.stderr)

        accession = find_accession_for_date(mrn, dicom_date)

        if accession:
            print(f"✓ Found accession: {accession}", file=sys.stderr)
            print(accession)
        else:
            print(f"✗ No matching study found", file=sys.stderr)

    except requests.exceptions.RequestException as e:
        print(f"Error querying patient {mrn}: {e}", file=sys.stderr)
    except ValueError as e:
        print(f"Error parsing date {date_str}: {e}", file=sys.stderr)


def process_batch(input_file, output_file):
    """Process multiple MRN/date combinations from a file."""
    try:
        # Read input file
        with open(input_file, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            rows = list(reader)

        if 'MRN' not in rows[0] or 'Date' not in rows[0]:
            print("Error: Input file must have 'MRN' and 'Date' columns", file=sys.stderr)
            sys.exit(1)

        print(f"Processing {len(rows)} patients...\n", file=sys.stderr)

        results = []
        for i, row in enumerate(rows, 1):
            mrn = row.get('MRN', '').strip()
            date = row.get('Date', '').strip()

            print(f"{i}/{len(rows)}: Processing MRN {mrn}", file=sys.stderr)

            if not mrn or not date:
                print(f"  ⚠ Skipping - missing MRN or date", file=sys.stderr)
                results.append({
                    "MRN": mrn,
                    "Date": date,
                    "Accession": ""
                })
                continue

            try:
                # Convert date format
                dicom_date = parse_date(date)

                # Search for study
                print(f"  Searching for date {date} ({dicom_date})...", file=sys.stderr)
                studies = search_patient(mrn)
                print(f"    Found {len(studies)} studies", file=sys.stderr)

                # Find matching study
                accession = ""
                for study in studies:
                    info = get_study_info(study["ID"])
                    if info["date"] == dicom_date:
                        accession = info["accession_number"]
                        print(f"    ✓ Match found: {accession}", file=sys.stderr)
                        break

                if not accession:
                    print(f"    ✗ No matching study found", file=sys.stderr)

                results.append({
                    "MRN": mrn,
                    "Date": date,
                    "Accession": accession
                })

            except ValueError as e:
                print(f"  ✗ Error parsing date: {e}", file=sys.stderr)
                results.append({
                    "MRN": mrn,
                    "Date": date,
                    "Accession": ""
                })
            except requests.exceptions.RequestException as e:
                print(f"  ✗ Error querying: {e}", file=sys.stderr)
                results.append({
                    "MRN": mrn,
                    "Date": date,
                    "Accession": ""
                })

        # Write output
        with open(output_file, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=["MRN", "Date", "Accession"], delimiter='\t')
            writer.writeheader()
            writer.writerows(results)

        found_count = sum(1 for r in results if r["Accession"])
        print(f"\n✓ Complete: {found_count}/{len(results)} accessions found", file=sys.stderr)
        print(f"✓ Output written to {output_file}", file=sys.stderr)

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Find accession numbers for studies by MRN and date",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single query
  %(prog)s --mrn 219306 --date 01/16/2016

  # Batch processing
  %(prog)s --input patients.txt --output results.txt

Input file format (tab-delimited):
  MRN\tDate
  219306\t01/16/2016
  220464\t02/02/2016
        """
    )
    parser.add_argument("--mrn", help="Patient MRN")
    parser.add_argument("--date", help="Study date in MM/DD/YYYY format")
    parser.add_argument("--input", help="Input file with MRN and Date columns (tab-delimited)")
    parser.add_argument("--output", help="Output file for results (tab-delimited)")

    args = parser.parse_args()

    # Validate arguments
    if args.input or args.output:
        if not (args.input and args.output):
            parser.error("Both --input and --output are required for batch processing")
        if args.mrn or args.date:
            parser.error("Cannot use --mrn/--date with --input/--output")
        process_batch(args.input, args.output)
    elif args.mrn and args.date:
        process_single(args.mrn, args.date)
    else:
        parser.error("Must provide either (--mrn and --date) or (--input and --output)")


if __name__ == "__main__":
    main()
