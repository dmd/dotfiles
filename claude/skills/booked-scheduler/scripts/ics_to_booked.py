#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["requests"]
# ///
"""
Import an ICS event into Booked Scheduler.

Handles:
- DateTime format conversion (ICS to ISO8601 with timezone)
- Resource lookup by name
- User lookup by email for participants
- Custom attribute mapping (e.g., CATEGORIES -> Principal Investigator)
- Scanned Person Initials from SUMMARY lines like "Confirmed-XX/XXX" (attribute id 2)
- Recurrence rule conversion (RRULE -> recurrenceRule)

Usage:
    ./ics_to_booked.py event.ics --resource "P1 Prisma"
    ./ics_to_booked.py event.ics --resource-id 4
    cat event.ics | ./ics_to_booked.py --resource "P1 Prisma"

Environment:
    SCANDIUM_API_KEY: API credentials in format "api_id:api_key"
"""

import argparse
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Import from the same directory
from booked_api import BookedAPI, ics_datetime_to_iso, parse_rrule

SCANNED_INITIALS_ATTRIBUTE_ID = 2


def parse_ics(ics_content: str) -> Dict:
    """Parse an ICS VEVENT into a dictionary.

    Args:
        ics_content: Raw ICS file content

    Returns:
        Dictionary with event properties
    """
    event = {}
    in_vevent = False
    current_key = None
    current_value = ""

    for line in ics_content.split("\n"):
        line = line.rstrip("\r")

        # Handle line continuations (lines starting with space or tab)
        if line.startswith(" ") or line.startswith("\t"):
            current_value += line[1:]
            continue

        # Save previous key-value if exists
        if current_key and in_vevent:
            event[current_key] = current_value

        # Parse new key-value
        if ":" in line:
            key, value = line.split(":", 1)
            # Handle parameters in key (e.g., DTSTART;VALUE=DATE:20260112)
            if ";" in key:
                key = key.split(";")[0]
            current_key = key
            current_value = value
        else:
            current_key = None
            current_value = ""

        if line == "BEGIN:VEVENT":
            in_vevent = True
        elif line == "END:VEVENT":
            if current_key:
                event[current_key] = current_value
            in_vevent = False

    return event


def parse_summary(summary: str) -> Tuple[str, List[Tuple[str, str]], Optional[str]]:
    """Parse SUMMARY field to extract title and participants.

    Expected format: "TITLE\\nName1: email1@example.com\\nName2: email2@example.com"

    Args:
        summary: Raw SUMMARY value (with \\n as literal string or newlines)

    Returns:
        Tuple of (title, [(name, email), ...])
    """
    # Handle escaped newlines
    parts = summary.replace("\\n", "\n").split("\n")

    title = parts[0].strip()
    participants = []
    confirmed_initials: Optional[str] = None

    for part in parts[1:]:
        part = part.strip()
        if part.startswith("Confirmed-"):
            candidate = part[len("Confirmed-") :].strip()
            if candidate.isalpha() and len(candidate) in (2, 3):
                confirmed_initials = candidate
            continue
        if ":" in part and "@" in part:
            # Format: "Name: email@domain.com"
            name_part, email = part.rsplit(":", 1)
            name = name_part.strip()
            email = email.strip()
            participants.append((name, email))

    return title, participants, confirmed_initials


def main():
    parser = argparse.ArgumentParser(
        description="Import an ICS event into Booked Scheduler"
    )
    parser.add_argument(
        "ics_file",
        nargs="?",
        help="Path to ICS file (or - for stdin)",
        default="-",
    )
    parser.add_argument(
        "--resource",
        "-r",
        help="Resource name (partial match)",
    )
    parser.add_argument(
        "--resource-id",
        type=int,
        help="Resource ID (alternative to --resource)",
    )
    parser.add_argument(
        "--attribute-map",
        "-a",
        action="append",
        default=[],
        help="Map CATEGORIES to attribute: 'CATEGORY_FIELD:ATTRIBUTE_ID' (e.g., 'PI:1')",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be created without actually creating",
    )
    parser.add_argument(
        "--pi-attribute-id",
        type=int,
        default=1,
        help="Attribute ID for Principal Investigator (default: 1)",
    )

    args = parser.parse_args()

    # Read ICS content
    if args.ics_file == "-":
        ics_content = sys.stdin.read()
    else:
        with open(args.ics_file, "r") as f:
            ics_content = f.read()

    # Parse ICS
    event = parse_ics(ics_content)

    if not event:
        print("Error: No VEVENT found in ICS content", file=sys.stderr)
        sys.exit(1)

    # Initialize API
    api = BookedAPI()

    # Find resource
    resource_id = args.resource_id
    if not resource_id:
        if not args.resource:
            print("Error: Must specify --resource or --resource-id", file=sys.stderr)
            sys.exit(1)
        resource = api.find_resource_by_name(args.resource)
        if not resource:
            print(f"Error: Resource '{args.resource}' not found", file=sys.stderr)
            print("Available resources:", file=sys.stderr)
            for r in api.list_resources():
                print(f"  {r['resourceId']}: {r['name']}", file=sys.stderr)
            sys.exit(1)
        resource_id = resource["resourceId"]
        print(f"Found resource: {resource['name']} (ID: {resource_id})")

    # Parse datetimes
    start_dt_str = event.get("DTSTART", "")
    end_dt_str = event.get("DTEND", "")

    if not start_dt_str or not end_dt_str:
        print("Error: DTSTART and DTEND are required", file=sys.stderr)
        sys.exit(1)

    start_iso = ics_datetime_to_iso(start_dt_str)
    end_iso = ics_datetime_to_iso(end_dt_str)

    # Parse start datetime for weekday calculation
    start_dt = datetime.strptime(start_dt_str.rstrip("Z"), "%Y%m%dT%H%M%S")

    # Parse SUMMARY for title and participants
    summary = event.get("SUMMARY", "Untitled")
    title, participant_info, confirmed_initials = parse_summary(summary)

    # Look up participants by email
    participant_ids = []
    missing_emails = []

    for name, email in participant_info:
        user = api.find_user_by_email(email)
        if user:
            participant_ids.append(user["id"])
            print(f"Found participant: {name} ({email}) -> User ID {user['id']}")
        else:
            missing_emails.append(f"{name}: {email}")
            print(f"Participant not found: {name} ({email})")

    # Build description with missing participants
    description = event.get("DESCRIPTION", "")
    if missing_emails:
        if description:
            description += "\n\n"
        description += "Unreg participants:\n" + "\n".join(missing_emails)

    # Parse custom attributes (CATEGORIES -> PI)
    custom_attributes = []
    categories = event.get("CATEGORIES", "")
    if categories:
        # Try to match to Principal Investigator attribute
        matched_value = api.find_attribute_value(args.pi_attribute_id, categories)
        if matched_value:
            custom_attributes.append({
                "attributeId": args.pi_attribute_id,
                "attributeValue": matched_value,
            })
            print(f"Matched CATEGORIES '{categories}' -> PI '{matched_value}'")
        else:
            print(f"Warning: CATEGORIES '{categories}' not matched to any PI value")
    if confirmed_initials:
        custom_attributes.append({
            "attributeId": SCANNED_INITIALS_ATTRIBUTE_ID,
            "attributeValue": confirmed_initials,
        })
        print(f"Scanned Person Initials: {confirmed_initials}")

    # Parse recurrence rule
    recurrence_rule = None
    rrule = event.get("RRULE", "")
    if rrule:
        recurrence_rule = parse_rrule(rrule, start_dt)
        print(f"Recurrence: {recurrence_rule['type']} every {recurrence_rule['interval']}")
        if recurrence_rule.get("repeatTerminationDate"):
            print(f"  Until: {recurrence_rule['repeatTerminationDate']}")

    # Summary
    print("\n=== Reservation Details ===")
    print(f"Resource ID: {resource_id}")
    print(f"Title: {title}")
    print(f"Start: {start_iso}")
    print(f"End: {end_iso}")
    if description:
        print(f"Description: {description[:100]}...")
    if participant_ids:
        print(f"Participants: {participant_ids}")
    if custom_attributes:
        print(f"Attributes: {custom_attributes}")
    if recurrence_rule:
        print(f"Recurrence: {recurrence_rule}")

    if args.dry_run:
        print("\n[DRY RUN] Would create reservation with above details")
        return

    # Create reservation
    print("\nCreating reservation...")
    result = api.create_reservation(
        resource_id=resource_id,
        start_datetime=start_iso,
        end_datetime=end_iso,
        title=title,
        description=description if description else None,
        participants=participant_ids if participant_ids else None,
        custom_attributes=custom_attributes if custom_attributes else None,
        recurrence_rule=recurrence_rule,
    )

    if result.get("referenceNumber"):
        ref_num = result["referenceNumber"]
        print(f"Created reservation: {ref_num}")

        # Check if participants were added
        res = api.get_reservation(ref_num)
        if participant_ids and not res.get("participants"):
            print("Participants not added on creation, updating...")
            api.update_reservation(
                reference_number=ref_num,
                resource_id=resource_id,
                start_datetime=start_iso,
                end_datetime=end_iso,
                title=title,
                update_scope="full",
                description=description,
                participants=participant_ids,
                custom_attributes=custom_attributes,
                recurrence_rule=recurrence_rule,
            )
            print("Participants added via update")

        print(f"\nSuccess! Reference: {ref_num}")
    else:
        print(f"Error: {result.get('errors', result)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
