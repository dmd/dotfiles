# Orthanc Helper Scripts

This directory contains reusable helper scripts for common Orthanc DICOM server workflows.

## Prerequisites

All scripts use `uv` for dependency management. Make sure `uv` is installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Available Scripts

### list_patient_studies.py

List all studies for a patient with comprehensive details, sorted by date.

**Usage:**
```bash
./list_patient_studies.py --mrn 219306
./list_patient_studies.py --mrn 219306 --verbose
./list_patient_studies.py --mrn 219306 --show-series
```

**Features:**
- Lists all studies for a patient sorted by date (newest first)
- Shows study date, time, accession, description, and series count
- Verbose mode displays patient demographics
- Show-series option displays detailed series information for each study
- Clean, formatted output with patient and study summaries

---

### query_study.py

Query Orthanc for studies by MRN or accession number.

**Usage:**
```bash
./query_study.py --mrn 219306
./query_study.py --accession E62622361
./query_study.py --mrn 219306 --verbose
```

**Features:**
- Search by patient MRN or accession number
- Display study details (date, accession, description, series count)
- Verbose mode shows additional patient information

---

### get_series_details.py

Get detailed series information with image counts for a study.

**Usage:**
```bash
./get_series_details.py --accession E62622361
./get_series_details.py --study-id <orthanc-study-id>
./get_series_details.py --mrn 219306 --date 01/16/2016
```

**Features:**
- Query by accession number, Orthanc study ID, or MRN+date
- Shows series number, description, modality, and image count
- Automatically sorts series by series number

---

### find_accession.py

Find accession numbers for studies by MRN and date. Supports both single queries and batch processing.

**Single Query:**
```bash
./find_accession.py --mrn 219306 --date 01/16/2016
```

**Batch Processing:**
```bash
./find_accession.py --input patients.txt --output results.txt
```

**Input file format (tab-delimited):**
```
MRN	Date
219306	01/16/2016
220464	02/02/2016
```

**Features:**
- Single or batch processing
- Automatic date format conversion (MM/DD/YYYY to DICOM YYYYMMDD)
- Progress reporting for batch operations
- Tab-delimited output compatible with Excel/spreadsheets

---

### monitor_new_studies.py

Monitor Orthanc for new DICOM studies in real-time.

**Usage:**
```bash
./monitor_new_studies.py
./monitor_new_studies.py --filter "MRI"
./monitor_new_studies.py --interval 5
```

**Features:**
- Real-time monitoring of new studies
- Optional text filtering by study description
- Configurable polling interval
- Displays study description, patient ID, date, and accession

---

## Common Use Cases

### 1. Review all studies for a patient
```bash
./list_patient_studies.py --mrn 219306 --show-series
```

### 2. Look up a patient's studies
```bash
./query_study.py --mrn 219306
```

### 3. Get details for a specific study
```bash
./get_series_details.py --accession E62622361
```

### 4. Find accession for a specific visit date
```bash
./find_accession.py --mrn 219306 --date 01/16/2016
```

### 5. Process a list of patients from a file
```bash
./find_accession.py --input patient_list.txt --output accessions.txt
```

### 6. Monitor for new MRI studies
```bash
./monitor_new_studies.py --filter "MRI"
```

## Date Format

All scripts expect dates in **MM/DD/YYYY** format (e.g., `01/16/2016`) and automatically convert to DICOM's YYYYMMDD format internally.

## Authentication

Authentication is handled automatically via `~/.netrc` file. No explicit credentials needed in scripts.

## Server Configuration

All scripts default to: `http://micvna.mclean.harvard.edu:8042`

To use a different server, edit the `SERVER` variable at the top of each script.
