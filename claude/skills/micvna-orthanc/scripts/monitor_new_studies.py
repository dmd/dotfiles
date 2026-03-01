#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
# ]
# ///

"""
Monitor Orthanc for new DICOM studies in real-time.

Usage:
    ./monitor_new_studies.py
    ./monitor_new_studies.py --filter "MRI"
    ./monitor_new_studies.py --interval 5
"""

import sys
import argparse
import requests
from time import sleep
from datetime import datetime

SERVER = "http://micvna.mclean.harvard.edu:8042"


def monitor_changes(interval=1, filter_text=None):
    """
    Monitor for new DICOM instances as they arrive.

    Args:
        interval: Seconds to wait between checks
        filter_text: Optional text to filter study descriptions
    """
    # Reset changes feed to start from now
    print(f"Resetting changes feed...", file=sys.stderr)
    requests.delete(f"{SERVER}/changes")
    since = 0

    print(f"Monitoring for new studies (Ctrl+C to stop)...", file=sys.stderr)
    if filter_text:
        print(f"Filter: showing only studies matching '{filter_text}'", file=sys.stderr)
    print()

    try:
        while True:
            sleep(interval)

            result = requests.get(f"{SERVER}/changes", params={"since": since}).json()
            since = result["Last"]

            new_instances = [
                x["Path"] for x in result["Changes"]
                if x["ChangeType"] == "NewInstance"
            ]

            for instance in new_instances:
                try:
                    tags = requests.get(f"{SERVER}{instance}/tags?simplify").json()

                    study_desc = tags.get("StudyDescription", "Unknown")
                    patient_id = tags.get("PatientID", "Unknown")
                    study_date = tags.get("StudyDate", "Unknown")
                    accession = tags.get("AccessionNumber", "Unknown")

                    # Apply filter if specified
                    if filter_text and filter_text.lower() not in study_desc.lower():
                        continue

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[{timestamp}] New study:")
                    print(f"  Description: {study_desc}")
                    print(f"  Patient ID: {patient_id}")
                    print(f"  Study Date: {study_date}")
                    print(f"  Accession: {accession}")
                    print()

                except KeyError:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[{timestamp}] New study - no description available")
                    print()
                except Exception as e:
                    print(f"Error processing instance: {e}", file=sys.stderr)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Monitor Orthanc for new DICOM studies in real-time",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --filter "MRI"
  %(prog)s --interval 5
        """
    )
    parser.add_argument("--interval", type=int, default=1,
                        help="Seconds between checks (default: 1)")
    parser.add_argument("--filter", help="Only show studies matching this text in description")

    args = parser.parse_args()

    try:
        monitor_changes(interval=args.interval, filter_text=args.filter)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Orthanc: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
