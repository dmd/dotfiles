---
name: micvna-orthanc
description: Use when querying micvna (Orthanc DICOM server) for medical imaging data, looking up studies by MRN, accession numbers, or study dates. Essential for DICOM data workflows.
---

# micvna (Orthanc) DICOM Server Skill

## When to Use This Skill

Use this skill when:
- Querying DICOM data from micvna
- Looking up studies by MRN (Patient ID)
- Finding accession numbers for specific study dates
- Retrieving DICOM metadata (study descriptions, dates, etc.)
- Creating scripts that query Orthanc

## Quick Start: Helper Scripts

The `scripts/` directory contains ready-to-use helper scripts for common tasks. These scripts handle all the API details for you:

- **`list_patient_studies.py`** - List all studies for a patient (sorted by date)
- **`query_study.py`** - Query studies by MRN or accession number
- **`get_series_details.py`** - Get series details with image counts
- **`find_accession.py`** - Find accession numbers by MRN and date (single or batch)
- **`monitor_new_studies.py`** - Monitor for new studies in real-time

**Quick examples:**
```bash
# Review all studies for a patient
./scripts/list_patient_studies.py --mrn 219306 --show-series

# Look up a patient's studies
./scripts/query_study.py --mrn 219306

# Get series details for a study
./scripts/get_series_details.py --accession E62622361

# Find accession for a specific date
./scripts/find_accession.py --mrn 219306 --date 01/16/2016

# Batch process from a file
./scripts/find_accession.py --input patients.txt --output results.txt
```

See `scripts/README.md` for full documentation.

For custom scripts or advanced usage, continue reading below to understand the API patterns.

## Server Configuration

```python
server = "http://micvna.mclean.harvard.edu:8042"
# Authentication is handled automatically via ~/.netrc
```

**API Documentation:** https://orthanc.uclouvain.be/book/users/rest.html

**Authentication:** Credentials are automatically read from `~/.netrc` file by the requests library. No explicit auth parameter needed in the code.

## Key Endpoints

- `POST /tools/find` - Query studies/patients/series/instances
- `GET /studies/{id}` - Get study details (includes Series array with series IDs)
- `GET /studies/{id}/tags?simplify` - Get simplified DICOM tags
- `GET /series/{id}` - Get series details (includes Instances array with image IDs)
- `GET /patients/{id}` - Get patient details
- `GET /changes` - Monitor new instances (for real-time monitoring)

**Note:** The `/studies/{id}/series` endpoint exists but does NOT support the `expand=True` parameter. Use `/studies/{id}` to get series IDs, then fetch each series individually.

## Common Patterns

### 1. Query Studies by MRN (Patient ID)

```python
def search_patient(patient_id):
    """Search for studies by patient ID (MRN) in Orthanc."""
    query = {
        "Level": "Study",
        "Query": {
            "PatientID": patient_id
        },
        "Expand": True
    }

    r = requests.post(f"{server}/tools/find", json=query)
    r.raise_for_status()
    return r.json()
```

**Returns:** List of studies for that patient

### 2. Get Study Details

```python
def get_study_info(study_id):
    """Get detailed study information including accession number and date."""
    r = requests.get(f"{server}/studies/{study_id}")
    r.raise_for_status()
    study = r.json()

    # Get main tags
    main_tags = study.get("MainDicomTags", {})

    # Get detailed tags if needed
    tags_response = requests.get(f"{server}/studies/{study_id}/tags?simplify")
    if tags_response.ok:
        all_tags = tags_response.json()
    else:
        all_tags = {}

    return {
        "date": main_tags.get("StudyDate", all_tags.get("StudyDate", "")),
        "accession_number": main_tags.get("AccessionNumber", all_tags.get("AccessionNumber", "")),
        "study_description": main_tags.get("StudyDescription", all_tags.get("StudyDescription", ""))
    }
```

### 3. Get Series (Scans) for a Study

**IMPORTANT:** Do NOT use the `expand=True` parameter with the series endpoint - it's not supported!

```python
def get_series_details(study_id):
    """
    Get all series for a study with image counts.

    IMPORTANT:
    - Call /studies/{id} to get the study, which includes Series IDs
    - Then call /series/{id} for each series to get details
    - Do NOT use /studies/{id}/series?expand=True (not supported)
    """
    # Get study details which includes Series array
    r = requests.get(f"{server}/studies/{study_id}")
    r.raise_for_status()
    study = r.json()

    series_ids = study.get("Series", [])

    series_details = []
    for series_id in series_ids:
        # Get detailed series information
        series_r = requests.get(f"{server}/series/{series_id}")
        series_r.raise_for_status()
        series = series_r.json()

        main_tags = series.get("MainDicomTags", {})
        series_number = main_tags.get("SeriesNumber", "Unknown")
        series_desc = main_tags.get("SeriesDescription", "No description")

        # Get image count from Instances array
        instances = series.get("Instances", [])
        image_count = len(instances)

        series_details.append({
            "series_id": series_id,
            "series_number": series_number,
            "description": series_desc,
            "image_count": image_count
        })

    return series_details
```

**Returns:** List of dicts with series_id, series_number, description, and image_count

### 4. Find Accession Number by MRN and Date

```python
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
```

## Date Handling

**IMPORTANT:** DICOM StudyDate is in YYYYMMDD format (e.g., "20160116")

### Converting from User Input

```python
from datetime import datetime

def parse_date(date_str):
    """Convert MM/DD/YYYY to YYYYMMDD for DICOM comparison."""
    dt = datetime.strptime(date_str.strip(), "%m/%d/%Y")
    return dt.strftime("%Y%m%d")

# Example
user_date = "01/16/2016"
dicom_date = parse_date(user_date)  # "20160116"
```

## DICOM Tag Reference

Common tags returned by Orthanc:

### MainDicomTags (Study Level)
- `StudyDate` - Date of study (YYYYMMDD)
- `StudyTime` - Time of study (HHMMSS)
- `AccessionNumber` - Unique identifier for the study
- `StudyDescription` - Description of study
- `StudyInstanceUID` - DICOM unique identifier

### PatientMainDicomTags
- `PatientID` - MRN/Patient identifier
- `PatientName` - Patient's name
- `PatientBirthDate` - Birth date (YYYYMMDD)

## Error Handling

### Missing Accession Numbers

Not all studies have accession numbers:

```python
accession = info.get("accession_number", "")
if not accession:
    print(f"Warning: No accession number for study {study_id}")
```

### Failed Queries

```python
try:
    studies = search_patient(mrn)
except requests.exceptions.RequestException as e:
    print(f"Error querying patient {mrn}: {e}")
    studies = []
```

## Common Workflows

**Note:** For most workflows, use the helper scripts in `scripts/` directory. These examples show how to build custom scripts using the API.

### Workflow 1: Get All Studies for Multiple MRNs

**Using helper script:**
```bash
./scripts/query_study.py --mrn 219306
./scripts/query_study.py --mrn 220464
```

**Custom script example:**
```python
mrns = ["219306", "220464", "206655"]

for mrn in mrns:
    print(f"Searching MRN: {mrn}")
    studies = search_patient(mrn)
    print(f"  Found {len(studies)} studies")

    for study in studies:
        info = get_study_info(study["ID"])
        print(f"    Date: {info['date']}, Accession: {info['accession_number']}")
```

### Workflow 2: Find Specific Studies by Date

**Using helper script:**
```bash
./scripts/find_accession.py --mrn 219306 --date 01/16/2016
```

**Custom script example:**
```python
# User provides dates in MM/DD/YYYY format
target_dates = {
    "219306": ["01/16/2016", "04/09/2016"],
    "220464": ["02/02/2016", "04/30/2016"]
}

for mrn, dates in target_dates.items():
    studies = search_patient(mrn)

    for user_date in dates:
        dicom_date = parse_date(user_date)

        for study in studies:
            info = get_study_info(study["ID"])
            if info["date"] == dicom_date:
                print(f"Match: MRN {mrn}, Date {user_date}, Accession {info['accession_number']}")
```

### Workflow 3: Get Series Details for a Study by Accession

**Using helper script:**
```bash
./scripts/get_series_details.py --accession E62622361
```

**Custom script example:**
```python
accession = "E62622361"

# Find the study
query = {
    "Level": "Study",
    "Query": {
        "AccessionNumber": accession
    },
    "Expand": True
}

r = requests.post(f"{server}/tools/find", json=query)
studies = r.json()

if not studies:
    print(f"Study with accession {accession} not found")
else:
    study = studies[0]
    study_id = study.get("ID")

    print(f"Found study: {study_id}")

    # Get series details
    series_list = get_series_details(study_id)

    print(f"\nNumber of series: {len(series_list)}")
    print("\nSeries details:")
    print("-" * 80)

    for i, series_info in enumerate(series_list, 1):
        print(f"{i}. Series #{series_info['series_number']}: {series_info['description']}")
        print(f"   Images: {series_info['image_count']}")
```

### Workflow 4: Process Data from File with Progress Reporting

**Using helper script:**
```bash
./scripts/find_accession.py --input patients.txt --output results.txt
```

**Custom script example:**
```python
import csv
from pathlib import Path

# Read input file with MRNs and dates
with open("input.txt", 'r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    rows = list(reader)

print(f"Processing {len(rows)} patients...\n", file=sys.stderr)

results = []
for i, row in enumerate(rows, 1):
    mrn = row.get('MRN', '')
    date = row.get('Date', '')

    print(f"{i}/{len(rows)}: Processing MRN {mrn}", file=sys.stderr)

    if not mrn or not date:
        continue

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
        "mrn": mrn,
        "date": date,
        "accession": accession
    })

# Write output
with open("output.txt", 'w') as f:
    writer = csv.DictWriter(f, fieldnames=["mrn", "date", "accession"], delimiter='\t')
    writer.writeheader()
    writer.writerows(results)

print(f"\n✓ Output written to output.txt", file=sys.stderr)
```

## Script Dependencies

Use uv with inline script metadata:

```python
#!/usr/bin/env python3
# /// script
# dependencies = [
#   "requests",
# ]
# ///

import requests
import sys
import csv
from pathlib import Path
from datetime import datetime
```

## Best Practices

### ✅ DO: Use the simplified tags endpoint

`/studies/{id}/tags?simplify` is easier to work with than raw DICOM tags

### ✅ DO: Handle missing data gracefully

Not all DICOM fields are guaranteed to be present

### ✅ DO: Print progress for batch operations

```python
print(f"Searching for MRN {mrn}...", file=sys.stderr)
print(f"  Found {len(studies)} studies", file=sys.stderr)
```

### ✅ DO: Query by PatientID, then filter results

More reliable than trying to query by multiple fields

### ✅ DO: Check both MainDicomTags and detailed tags

Some information may only be in one or the other

### ❌ DON'T: Assume all studies have accession numbers

Always check if the field exists before using it

### ❌ DON'T: Compare dates as strings without formatting

Convert user dates to YYYYMMDD format first

### ❌ DON'T: Make excessive requests

Cache study information when processing multiple MRNs

### ❌ DON'T: Use expand=True with series endpoints

The `/studies/{id}/series?expand=True` endpoint is NOT supported and will fail. Always get the study first, then fetch each series individually.

## Real-Time Monitoring

**Using helper script:**
```bash
./scripts/monitor_new_studies.py
./scripts/monitor_new_studies.py --filter "MRI"
```

**Custom script example:**
For monitoring new DICOM instances as they arrive:

```python
# Reset changes feed to start from now
requests.delete(f"{server}/changes")
since = 0

while True:
    sleep(1)
    result = requests.get(f"{server}/changes", params={"since": since}).json()
    since = result["Last"]

    new_instances = [
        x["Path"] for x in result["Changes"]
        if x["ChangeType"] == "NewInstance"
    ]

    for instance in new_instances:
        try:
            tags = requests.get(f"{server}{instance}/tags?simplify").json()
            study_desc = tags.get("StudyDescription", "Unknown")
            print(f"{datetime.now()}: New study - {study_desc}")
        except KeyError:
            print(f"{datetime.now()}: New study - no description")
```

## Summary

**micvna is an Orthanc DICOM server that:**
- Stores medical imaging studies
- Allows queries by Patient ID (MRN)
- Returns DICOM metadata including dates and accession numbers
- Uses YYYYMMDD date format
- Requires no authentication for queries
- Provides both simple and detailed tag access
- Supports real-time monitoring of new studies
