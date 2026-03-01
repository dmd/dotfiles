# IRIS (XNAT) Helper Scripts

This directory contains ready-to-use command-line tools for common IRIS (XNAT) operations.

## Prerequisites

All scripts use `uv` for dependency management. No manual installation needed - dependencies are handled automatically.

## Scripts

### query_experiment.py

Query IRIS for an experiment by label or accession number.

```bash
./query_experiment.py <identifier>
./query_experiment.py E62622361
```

**Output:** JSON with experiment details

### get_scan_details.py

Get scan details with **accurate file counts** for an experiment.

**IMPORTANT:** This script queries scan resources to get real file counts, since the `frames` field is unreliable.

```bash
./get_scan_details.py <identifier>
./get_scan_details.py E62622361
```

**Output:** JSON with scan details including accurate file counts

### check_project.py

Check if an experiment is in or shared to a specific project.

```bash
./check_project.py <identifier> <project-id>
./check_project.py E62622361 webb_k23
```

**Exit codes:**
- 0 = Experiment is in the project
- 1 = Experiment is not in the project or not found

### share_experiment.py

Share a single experiment to another project.

**Automatically shares the subject first** (required by XNAT).

```bash
./share_experiment.py <identifier> <target-project>
./share_experiment.py E62622361 webb_k23
```

**Exit codes:**
- 0 = Successfully shared (or already shared)
- 1 = Error occurred

### batch_share_experiments.py

Share multiple experiments to a project (batch processing).

Reads identifiers from a file or stdin, provides progress tracking and summary statistics.

```bash
./batch_share_experiments.py <target-project> <identifiers-file>
./batch_share_experiments.py webb_k23 identifiers.txt

# Or from stdin
cat identifiers.txt | ./batch_share_experiments.py webb_k23 -
```

**Input file format:**
- One identifier (label or ID) per line
- Empty lines and lines starting with # are ignored

**Example input file:**
```
# Experiments to share
E62622361
E15182899
E48130001
```

### list_project_experiments.py

List all experiments in a project.

```bash
./list_project_experiments.py <project-id>
./list_project_experiments.py webb_k23
```

**Output:** JSON with list of experiments in the project

## Common Usage Patterns

### Quick check if experiment exists and is shared

```bash
./query_experiment.py E62622361 && \
./check_project.py E62622361 webb_k23
```

### Get experiment info and share if not already shared

```bash
./check_project.py E62622361 webb_k23 || \
./share_experiment.py E62622361 webb_k23
```

### Share multiple experiments from a list

```bash
# Create list
cat > identifiers.txt <<EOF
E62622361
E15182899
E48130001
EOF

# Share all
./batch_share_experiments.py webb_k23 identifiers.txt
```

### Get scan details for quality check

```bash
./get_scan_details.py E62622361 | jq '.scans[] | {scan_id, file_count, type}'
```

## Important Notes

### Accession vs Label

**CRITICAL:** What looks like an "accession number" (e.g., E62622361) is often stored as the experiment **label**, not in the accession field. All scripts search by label first (most reliable).

### File Counts

The `frames` field in XNAT scan summaries is often 0 or incorrect. The `get_scan_details.py` script queries scan **resources** to get accurate file counts.

### Sharing Requirements

When sharing an experiment, you **must** share the subject first. The sharing scripts handle this automatically.

## Script Output

- Progress/status messages → stderr
- Structured data (JSON) → stdout

This allows you to capture JSON output while still seeing progress:

```bash
./query_experiment.py E62622361 > output.json
# Progress messages appear on screen
# JSON data goes to output.json
```

## Troubleshooting

### Permission denied

Make scripts executable:

```bash
chmod +x scripts/*.py
```

### uv not found

Install uv: https://github.com/astral-sh/uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Authentication errors

Check credentials in the scripts (search for `auth = `).
