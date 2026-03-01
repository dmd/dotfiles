---
name: iris-xnat
description: Use when working with IRIS (XNAT imaging database), querying experiments, managing projects, or sharing studies between projects. Essential for XNAT workflows.
---

# IRIS (XNAT) Imaging Database Skill

## When to Use This Skill

Use this skill when:
- Querying IRIS (XNAT) for imaging experiments
- Looking up experiments by accession number or session label
- Checking if experiments exist in specific projects
- Sharing studies between XNAT projects
- Managing XNAT subjects and experiments
- Creating scripts that interact with XNAT

## Quick Start

This skill provides ready-to-use helper scripts for common tasks:

```bash
# Query an experiment
./scripts/query_experiment.py E62622361

# Get scan details with accurate file counts
./scripts/get_scan_details.py E62622361

# Check if experiment is in a project
./scripts/check_project.py E62622361 webb_k23

# Share single experiment to a project
./scripts/share_experiment.py E62622361 webb_k23

# Share multiple experiments (batch processing)
./scripts/batch_share_experiments.py webb_k23 identifiers.txt

# List all experiments in a project
./scripts/list_project_experiments.py webb_k23
```

All scripts are executable and use uv for dependency management. Run any script without arguments to see detailed usage information.

## Server Configuration

```python
server = "https://iris.mclean.harvard.edu"
auth = ("zabbix", "iliketoeatcats")
```

**All requests require authentication.**

**API Documentation:** https://wiki.xnat.org/xnat-api/xnat-rest-api-directory

## ⚠️ CRITICAL: Common Pitfalls

### Accession vs Label Confusion

**IMPORTANT:** What appears to be an "accession number" (like E62622361) is often stored as the experiment **label**, NOT in the accession field!

- The `accession` query parameter is **UNRELIABLE** - it may return ALL experiments instead of filtering
- Always try searching by **label** first when looking for an identifier
- If searching by label fails, then check the actual accession field in experiment details

### Getting Accurate Image/File Counts

**DO NOT** rely on the `frames` field in scan summaries - it's often 0 or incorrect!

**MUST** query scan **resources** to get accurate file counts:

```python
# ❌ WRONG - frames field is unreliable
scans = get_scans(experiment_id)
for scan in scans:
    image_count = scan.get('frames', 0)  # Often returns 0!

# ✅ CORRECT - query scan resources
for scan in scans:
    resources_r = requests.get(
        f"{server}/data/experiments/{exp_id}/scans/{scan['ID']}/resources",
        auth=auth
    )
    resources = resources_r.json().get("ResultSet", {}).get("Result", [])
    file_count = sum(int(r.get('file_count', 0)) for r in resources)
```

## Key Endpoints

### Query Endpoints
- `GET /data/experiments` - Query experiments (supports filters)
- `GET /data/experiments/{id}` - Get experiment details
- `GET /data/experiments/{id}?format=json` - Get detailed JSON data
- `GET /data/subjects` - Query subjects
- `GET /data/projects/{project}/experiments` - List experiments in project

### Project Access Endpoints
- `GET /data/projects/{project}/experiments/{id}` - Check if experiment is in project

### Sharing Endpoints
- `PUT /data/projects/{src}/subjects/{subject_id}/projects/{target}` - Share subject
- `PUT /data/projects/{src}/subjects/{subject_id}/experiments/{exp_id}/projects/{target}` - Share experiment

## Helper Scripts

This skill includes ready-to-use helper scripts in the `scripts/` directory:

- **query_experiment.py** - Query experiments by label or accession
- **get_scan_details.py** - Get scan details with accurate file counts
- **check_project.py** - Check if experiment is in a project
- **share_experiment.py** - Share single experiment to a project
- **batch_share_experiments.py** - Share multiple experiments from a file
- **list_project_experiments.py** - List all experiments in a project

All scripts use the proper uv shebang and can be run directly:

```bash
# Query an experiment
./scripts/query_experiment.py E62622361

# Get scan details with accurate file counts
./scripts/get_scan_details.py E62622361

# Check if experiment is in a project
./scripts/check_project.py E62622361 webb_k23

# Share experiment to a project
./scripts/share_experiment.py E62622361 webb_k23

# Share multiple experiments from a file
./scripts/batch_share_experiments.py webb_k23 identifiers.txt

# List all experiments in a project
./scripts/list_project_experiments.py webb_k23
```

See individual script help with `-h` or no arguments for usage details.

## Common Patterns

### 1. Query Experiment by Identifier (Label or Accession)

**Use the helper script:**

```bash
./scripts/query_experiment.py E62622361
```

**Or implement in your own code** (always try by label first):

```python
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
```

**Returns:** Dict with keys: `ID`, `project`, `label`, `date`, etc.

### 2. Query Experiment by Session Label (Recommended)

```python
def find_experiment_by_label(session_label):
    """Find experiment by session label across all projects."""
    r = requests.get(f"{server}/data/experiments", auth=auth)
    r.raise_for_status()

    data = r.json()
    results = data.get("ResultSet", {}).get("Result", [])

    # Find matching experiment
    for exp in results:
        if exp.get("label") == session_label:
            return exp

    return None
```

### 3. Get Detailed Experiment Information

```python
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
```

**Returns:** Dict with keys like: `subject_ID`, `project`, `date`, `label`, etc.

### 4. Get Scan Details with Accurate File Counts

**CRITICAL:** The `frames` field is unreliable. Always query scan resources for accurate counts!

**Use the helper script:**

```bash
./scripts/get_scan_details.py E62622361
```

**Or implement in your own code:**

```python
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
        if resources_r.status_code == 200:
            resources_data = resources_r.json()
            resources = resources_data.get("ResultSet", {}).get("Result", [])

            # Sum file counts across all resources (DICOM, NIFTI, etc.)
            for resource in resources:
                file_count += int(resource.get("file_count", 0))

        total_files += file_count

        scan_details.append({
            "scan_id": scan_id,
            "type": scan_type,
            "series_description": series_desc,
            "file_count": file_count
        })

    return scan_details, total_files
```

**Returns:** Tuple of (list of scan dicts, total file count across all scans)

### 5. Check if Experiment is in a Project

**Use the helper script:**

```bash
./scripts/check_project.py E62622361 webb_k23
```

**Or implement in your own code:**

```python
def is_in_project(experiment_id, project_id):
    """Check if an experiment is in or shared to a specific project."""
    r = requests.get(
        f"{server}/data/projects/{project_id}/experiments/{experiment_id}",
        auth=auth
    )

    # 200 = experiment exists in/is shared to this project
    # 404 = experiment is not in this project
    return r.status_code == 200
```

**Important:** A 404 response is normal and expected when an experiment is not in a project.

### 6. Share Experiment to Another Project

**CRITICAL:** You MUST share the subject BEFORE sharing the experiment.

**Use the helper script:**

```bash
# Share single experiment
./scripts/share_experiment.py E62622361 webb_k23

# Share multiple experiments from a file
./scripts/batch_share_experiments.py webb_k23 identifiers.txt
```

**Or implement in your own code:**

```python
def share_to_project(experiment_id, source_project, target_project):
    """Share an experiment (and its subject) to another project."""

    # First, get the subject ID
    r = requests.get(
        f"{server}/data/experiments/{experiment_id}?format=json",
        auth=auth
    )
    r.raise_for_status()
    data = r.json()
    subject_id = data["items"][0]["data_fields"]["subject_ID"]

    # Step 1: Share subject first (REQUIRED)
    subject_url = (
        f"{server}/data/projects/{source_project}/subjects/{subject_id}"
        f"/projects/{target_project}"
    )
    r = requests.put(subject_url, auth=auth)

    # HTTP 409 = already exists, which is OK
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
```

## HTTP Status Codes

### Expected Status Codes

- **200** - Success (resource exists/operation succeeded)
- **201** - Created (new resource created)
- **404** - Not Found (normal when checking project membership)
- **409** - Conflict (resource already exists - treat as success for sharing)

### Error Status Codes

- **401** - Unauthorized (check authentication)
- **403** - Forbidden (check permissions)
- **500** - Server Error

## Common Workflows

### Workflow 1: Verify Experiment is in Target Project

**Using helper scripts:**

```bash
./scripts/check_project.py E62622361 webb_k23
```

**Or in Python:**

```python
# Find experiment
exp = find_experiment_by_identifier("00048130")
if not exp:
    print("Experiment not found")
    exit(1)

experiment_id = exp["ID"]
source_project = exp["project"]

# Check if in target project
if is_in_project(experiment_id, "webb_k23"):
    print(f"✓ Experiment is in webb_k23")
else:
    print(f"✗ Experiment is NOT in webb_k23")
```

### Workflow 2: Share Multiple Experiments to Project

**Using helper script (recommended):**

```bash
# Create a file with identifiers (one per line)
cat > identifiers.txt <<EOF
E62622361
E15182899
E48130001
EOF

# Share all at once with progress tracking
./scripts/batch_share_experiments.py webb_k23 identifiers.txt
```

**Or in Python:**

```python
identifiers = ["00048130", "00027353", "00048131"]
target_project = "webb_k23"

for identifier in identifiers:
    exp = find_experiment_by_identifier(identifier)
    if not exp:
        print(f"✗ {identifier}: Not found")
        continue

    experiment_id = exp["ID"]
    source_project = exp["project"]

    if is_in_project(experiment_id, target_project):
        print(f"✓ {identifier}: Already in {target_project}")
    else:
        share_to_project(experiment_id, source_project, target_project)
        print(f"✓ {identifier}: Shared to {target_project}")
```

### Workflow 3: Get All Experiments in a Project

**Using helper script:**

```bash
./scripts/list_project_experiments.py webb_k23
```

**Or in Python:**

```python
def get_project_experiments(project_id):
    """Get all experiments in a specific project."""
    r = requests.get(
        f"{server}/data/projects/{project_id}/experiments",
        auth=auth
    )
    r.raise_for_status()

    data = r.json()
    return data.get("ResultSet", {}).get("Result", [])

experiments = get_project_experiments("webb_k23")
print(f"Found {len(experiments)} experiments in webb_k23")

for exp in experiments:
    print(f"  {exp['label']} - {exp['ID']}")
```

### Workflow 4: Get Scan Details for Quality Check

**Using helper script:**

```bash
./scripts/get_scan_details.py E62622361
```

This will return JSON with scan information including accurate file counts queried from resources.

## Error Handling

### Handle JSON Decode Errors

Some XNAT endpoints return empty responses:

```python
try:
    data = r.json()
except requests.exceptions.JSONDecodeError:
    # Some endpoints return empty body on success
    if r.status_code in (200, 201, 204):
        return True
    raise
```

### Treat 409 (Conflict) as Success for Sharing

```python
r = requests.put(share_url, auth=auth)

if r.status_code == 409:
    # Resource already exists - this is fine
    return True
elif r.status_code in (200, 201):
    return True
else:
    r.raise_for_status()
```

### Handle 404 When Checking Project Membership

```python
r = requests.get(
    f"{server}/data/projects/{project}/experiments/{exp_id}",
    auth=auth
)

# 404 is expected and normal
if r.status_code == 404:
    return False  # Not in project
elif r.status_code == 200:
    return True   # In project
else:
    r.raise_for_status()
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
```

## Best Practices

### ✅ DO: Search by label first when looking for experiments

Identifiers like "E62622361" are typically stored as labels, not accession numbers

### ✅ DO: Query scan resources for accurate file counts

The `frames` field in scan summaries is unreliable - always query resources

### ✅ DO: Share subject before experiment

XNAT requires the subject to exist in the target project first

### ✅ DO: Treat HTTP 409 as success for sharing operations

409 means the resource already exists, which is the desired outcome

### ✅ DO: Use status code checking for project membership

Don't rely on JSON parsing for 404 responses

### ✅ DO: Print progress for batch operations

```python
print(f"Processing {i}/{total}: {name}", file=sys.stderr)
```

### ✅ DO: Handle missing experiments gracefully

Not all accession numbers may exist in IRIS

### ✅ DO: Provide summary statistics at the end

```python
print(f"\nSUMMARY:")
print(f"Found: {found_count}")
print(f"Not found: {not_found_count}")
print(f"Already shared: {shared_count}")
```

### ❌ DON'T: Use the `accession` query parameter

It's unreliable and may return ALL experiments instead of filtering

### ❌ DON'T: Use the `frames` field for file counts

This field is often 0 or incorrect - always query scan resources instead

### ❌ DON'T: Assume identifiers are stored as accession numbers

They're usually stored as labels - always search by label first

### ❌ DON'T: Try to parse JSON from 404 responses

404 responses may not have JSON bodies

### ❌ DON'T: Skip sharing the subject

You WILL get an error if you try to share an experiment without sharing the subject first

## Summary

**IRIS is an XNAT server that:**
- Manages imaging research data in projects
- Organizes data as: Projects → Subjects → Experiments
- Requires authentication for all operations
- Allows sharing experiments between projects
- **Stores identifiers as labels, NOT accession numbers** (critical!)
- **Requires querying scan resources for accurate file counts** (frames field is unreliable!)
- Returns data in JSON format with ResultSet structure
- Requires subject sharing before experiment sharing
- Treats HTTP 409 as success for duplicate sharing operations

**Key Mistakes to Avoid:**
1. Using the `accession` query parameter (unreliable)
2. Using the `frames` field for image counts (often wrong)
3. Assuming identifiers are accession numbers (they're usually labels)
