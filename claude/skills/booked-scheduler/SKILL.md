---
name: booked-scheduler
description: Use when working with Booked Scheduler (scandium.mclean.harvard.edu), managing reservations, querying resources/schedules, or automating room bookings via API.
---

# Booked Scheduler API Skill

## Overview

Booked Scheduler is a resource reservation system. This skill covers the API at **scandium.mclean.harvard.edu**.

**Official API Documentation:** https://www.bookedscheduler.com/help/api/

> **IMPORTANT: Always Use the Helper Scripts**
>
> This skill includes a Python library at `scripts/booked_api.py` that handles API quirks
> automatically (e.g., participants not being added on creation, datetime field name
> differences between create and get responses).
>
> **DO NOT write raw API calls.** Always use `BookedAPI` from the scripts:
>
> ```python
> import sys
> sys.path.insert(0, "/Users/dmd/.claude/skills/booked-scheduler/scripts")
> from booked_api import BookedAPI, ics_datetime_to_iso, parse_rrule
>
> api = BookedAPI()
> ```
>
> The reference documentation below is for understanding the API, not for making direct calls.

## Server Configuration

```python
import os

server = "https://scandium.mclean.harvard.edu"
api_id, api_key = os.environ["SCANDIUM_API_KEY"].split(":")

headers = {
    "X-Booked-ApiId": api_id,
    "X-Booked-ApiKey": api_key,
}
```

**All API requests require authentication headers (except where noted).**

---

## Authentication

### Method 1: API Key Authentication (Preferred)

Use `X-Booked-ApiId` and `X-Booked-ApiKey` headers:

```python
headers = {
    "X-Booked-ApiId": api_id,
    "X-Booked-ApiKey": api_key,
}
response = requests.get(f"{server}/Services/Accounts/", headers=headers)
```

### Method 2: Session Authentication

```python
# POST /Services/Authentication/Authenticate
auth_response = requests.post(
    f"{server}/Services/Authentication/Authenticate",
    json={"username": "user", "password": "pass"}
)
session = auth_response.json()
# Returns: sessionToken, sessionExpires, userId, isAuthenticated

# Use session token for subsequent requests
headers = {
    "X-Booked-SessionToken": session["sessionToken"],
    "X-Booked-UserId": str(session["userId"]),
}

# Sign out when done
# POST /Services/Authentication/SignOut (requires auth)
```

---

## Accounts API

Manage the currently authenticated user's account.

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/Services/Accounts/` | Get current user account info | Yes |
| POST | `/Services/Accounts/` | Update current user account | Yes |
| POST | `/Services/Accounts/Password/` | Update current user password | Yes |
| POST | `/Services/Accounts/Registration` | Register new account | **No** |

### Get Current User

```python
r = requests.get(f"{server}/Services/Accounts/", headers=headers)
user = r.json()
# Returns: userId, firstName, lastName, emailAddress, userName, timezone, phone, organization, position, customAttributes, icsUrl
```



---

## Reservations API

Create, read, update, and delete reservations.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/Services/Reservations/` | List reservations (filterable) |
| GET | `/Services/Reservations/:referenceNumber` | Get single reservation |
| POST | `/Services/Reservations/` | Create reservation |
| POST | `/Services/Reservations/:referenceNumber` | Update reservation |
| DELETE | `/Services/Reservations/:referenceNumber` | Delete reservation |
| POST | `/Services/Reservations/:referenceNumber/Approval` | Approve reservation |
| POST | `/Services/Reservations/:referenceNumber/CheckIn` | Check in |
| POST | `/Services/Reservations/:referenceNumber/CheckOut` | Check out |

### Query Parameters for Listing

| Parameter | Description |
|-----------|-------------|
| `userId` | Filter by user ID |
| `resourceId` | Filter by resource ID |
| `scheduleId` | Filter by schedule ID |
| `startDateTime` | Start of date range (YYYY-MM-DD or ISO 8601) |
| `endDateTime` | End of date range |

### List Reservations

```python
from datetime import datetime, timedelta

params = {
    "startDateTime": datetime.now().strftime("%Y-%m-%d"),
    "endDateTime": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
    # Optional filters:
    # "resourceId": 1,
    # "userId": 1,
    # "scheduleId": 1,
}

r = requests.get(f"{server}/Services/Reservations/", headers=headers, params=params)
reservations = r.json().get("reservations", [])

for res in reservations:
    print(f"{res['referenceNumber']}: {res['title']} ({res['startDate']} - {res['endDate']})")
```

### Get Single Reservation

```python
ref_num = "abc123def"
r = requests.get(f"{server}/Services/Reservations/{ref_num}", headers=headers)
reservation = r.json()
```

### Create Reservation

> **CRITICAL: DateTime Format**
>
> DateTimes MUST include timezone offset in ISO8601 format:
> - ✅ `"2026-01-15T09:00:00+0000"` (UTC)
> - ✅ `"2026-01-15T09:00:00-0500"` (EST)
> - ❌ `"2026-01-15T09:00:00"` (will fail validation)
> - ❌ `"2026-01-15 09:00:00"` (will fail validation)
>
> **CRITICAL: userId is Required**
>
> You MUST include `userId` in the reservation. Get it from `/Services/Accounts/`.

```python
# First, get the current user ID
r = requests.get(f"{server}/Services/Accounts/", headers=headers)
user_id = r.json().get('userId')

reservation = {
    "resourceId": 1,
    "userId": user_id,  # REQUIRED!
    "startDateTime": "2026-01-15T14:00:00+0000",  # UTC with timezone offset
    "endDateTime": "2026-01-15T15:00:00+0000",
    "title": "Team Meeting",
    "description": "Weekly sync",
    # Optional fields:
    # "invitees": [2, 3],  # User IDs to invite
    # "participants": [4, 5],  # User IDs as participants
    # "accessories": [{"accessoryId": 1, "quantityRequested": 2}],
    # "customAttributes": [{"attributeId": 1, "attributeValue": "value"}],
    # "recurrenceRule": {...},  # See Recurrence Rules section below
    # "startReminder": {"value": 15, "interval": "minutes"},
    # "endReminder": {"value": 5, "interval": "minutes"},
}

r = requests.post(f"{server}/Services/Reservations/", headers=headers, json=reservation)
result = r.json()

# IMPORTANT: Status 200 does NOT mean success! Check for errors.
if result.get('referenceNumber'):
    print(f"Created: {result.get('referenceNumber')}")
else:
    print(f"Error: {result.get('errors')}")
```

### Update Reservation

```python
ref_num = "abc123def"

updated = {
    "resourceId": 1,
    "startDateTime": "2026-01-15T10:00:00",
    "endDateTime": "2026-01-15T11:00:00",
    "title": "Updated Meeting",
    # For recurring reservations, specify scope:
    # "updateScope": "this" | "full" | "future"
}

r = requests.post(f"{server}/Services/Reservations/{ref_num}", headers=headers, json=updated)
```

### Delete Reservation

```python
ref_num = "abc123def"
# For recurring: add ?updateScope=this|full|future
r = requests.delete(f"{server}/Services/Reservations/{ref_num}", headers=headers)
```

### Update Scope for Recurring Reservations

| Value | Effect |
|-------|--------|
| `this` | Only this instance |
| `full` | Entire series |
| `future` | This and all future instances |

### Recurrence Rules

For recurring reservations, use the `recurrenceRule` object:

```python
"recurrenceRule": {
    "type": "weekly",           # "none", "daily", "weekly", "monthly", "yearly"
    "interval": 4,              # Every N periods (e.g., every 4 weeks)
    "weekdays": [1],            # Days of week: 0=Sun, 1=Mon, ..., 6=Sat
    "monthlyType": None,        # For monthly: "dayOfMonth" or "dayOfWeek"
    "repeatTerminationDate": "2026-07-11T00:00:00+0000"  # End date (ISO8601 with TZ!)
}
```

**Recurrence Type Values:**

| Type | Description |
|------|-------------|
| `none` | No recurrence (single event) |
| `daily` | Repeat every N days |
| `weekly` | Repeat every N weeks on specified weekdays |
| `monthly` | Repeat every N months |
| `yearly` | Repeat every N years |

**Weekday Values (for weekly recurrence):**

Sunday is 0, Monday is 1, etc. The week starts on Sunday, 0.

### Participants Quirk

> **Note:** Participants may not be added on initial creation.
>
> **The `BookedAPI.create_reservation()` method handles this automatically** by checking
> if participants were added and performing a follow-up update if needed. This is why
> you should always use the helper scripts instead of raw API calls.

### Approve, Check In, Check Out

```python
ref_num = "abc123def"

# Approve (for reservations requiring approval)
requests.post(f"{server}/Services/Reservations/{ref_num}/Approval", headers=headers)

# Check in
requests.post(f"{server}/Services/Reservations/{ref_num}/CheckIn", headers=headers)

# Check out
requests.post(f"{server}/Services/Reservations/{ref_num}/CheckOut", headers=headers)
```

---

## Resources API

Manage bookable resources (rooms, equipment, etc.).

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/Services/Resources/` | List all resources user can access | Yes |
| GET | `/Services/Resources/:resourceId` | Get single resource | Yes |
| GET | `/Services/Resources/Availability` | Resource availability (7 days) | Yes |
| GET | `/Services/Resources/Status` | List resource statuses | **No** |
| GET | `/Services/Resources/Status/Reasons` | Status reason descriptions | Yes |
| GET | `/Services/Resources/Types` | List resource types | Yes |
| GET | `/Services/Resources/Groups` | Resource group tree | Yes |
| POST | `/Services/Resources/` | Create resource | Admin |
| POST | `/Services/Resources/:resourceId` | Update resource | Admin |
| DELETE | `/Services/Resources/:resourceId` | Delete resource | Admin |

### List Resources

```python
r = requests.get(f"{server}/Services/Resources/", headers=headers)
resources = r.json().get("resources", [])

for res in resources:
    print(f"{res['resourceId']}: {res['name']} (Schedule: {res['scheduleId']})")
```

### Get Resource Details

```python
resource_id = 1
r = requests.get(f"{server}/Services/Resources/{resource_id}", headers=headers)
resource = r.json()
# Returns: resourceId, name, location, contact, description, notes, minLength, maxLength,
#          requiresApproval, allowMultiday, maxParticipants, scheduleId, statusId, customAttributes, etc.
```

### Get Resource Availability

```python
r = requests.get(
    f"{server}/Services/Resources/Availability",
    headers=headers,
    params={"dateTime": "2026-01-15"}  # Optional, defaults to now
)
availability = r.json()
# Returns availability for next 7 days
```

### Resource Statuses (No Auth Required)

```python
r = requests.get(f"{server}/Services/Resources/Status")
# Returns: Hidden, Available, Unavailable
```

### Create Resource (Admin)

```python
resource = {
    "name": "Conference Room A",
    "scheduleId": 1,
    "autoAssignPermissions": True,
    # Optional:
    # "location": "Building 1, Floor 2",
    # "contact": "facilities@example.com",
    # "description": "Large conference room",
    # "minLength": "00:30",
    # "maxLength": "04:00",
    # "requiresApproval": False,
    # "allowMultiday": False,
    # "maxParticipants": 20,
}

r = requests.post(f"{server}/Services/Resources/", headers=headers, json=resource)
```

---

## Schedules API

Query schedules and availability slots.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/Services/Schedules/` | List all schedules |
| GET | `/Services/Schedules/:scheduleId` | Get schedule details |
| GET | `/Services/Schedules/:scheduleId/Slots` | Get schedule slots/availability |

### List Schedules

```python
r = requests.get(f"{server}/Services/Schedules/", headers=headers)
schedules = r.json().get("schedules", [])

for sched in schedules:
    print(f"{sched['id']}: {sched['name']} (TZ: {sched['timezone']})")
```

### Get Schedule Slots

```python
schedule_id = 1

r = requests.get(
    f"{server}/Services/Schedules/{schedule_id}/Slots",
    headers=headers,
    params={
        "startDateTime": "2026-01-15",
        "endDateTime": "2026-01-16",
        # Optional:
        # "resourceId": 1,  # Filter to specific resource
    }
)
slots = r.json()
# Returns dates with resources and their slot availability
```

---

## Users API

Manage users (mostly admin operations).

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/Services/Users/` | List users (may be limited by privacy) | Yes |
| GET | `/Services/Users/:userId` | Get user details | Yes |
| GET | `/Services/Users/Languages` | List supported languages | **No** |
| GET | `/Services/Users/PhoneCountryCodes` | List phone country codes | **No** |
| POST | `/Services/Users/` | Create user | Admin |
| POST | `/Services/Users/:userId` | Update user | Admin |
| POST | `/Services/Users/:userId/Status` | Update user status | Admin |
| POST | `/Services/Users/:userId/Password` | Update user password | Admin |
| DELETE | `/Services/Users/:userId` | Delete user | Admin |

### Query Parameters for Listing Users

| Parameter | Description |
|-----------|-------------|
| `username` | Filter by username |
| `email` | Filter by email |
| `firstName` | Filter by first name |
| `lastName` | Filter by last name |
| `phone` | Filter by phone |
| `organization` | Filter by organization |
| `att#` | Filter by custom attribute (e.g., `att1=value`) |

### List Users

```python
r = requests.get(f"{server}/Services/Users/", headers=headers)
users = r.json().get("users", [])

for user in users:
    print(f"{user['id']}: {user['firstName']} {user['lastName']} ({user['emailAddress']})")
```

### Get Languages (No Auth)

```python
r = requests.get(f"{server}/Services/Users/Languages")
languages = r.json()
```

### Create User (Admin)

```python
user = {
    "password": "securepassword",
    "firstName": "John",
    "lastName": "Doe",
    "emailAddress": "john.doe@example.com",
    "userName": "jdoe",
    "timezone": "America/New_York",
    # Optional:
    # "phone": "6175551234",
    # "phoneCountryCode": "US",
    # "organization": "Research Lab",
    # "position": "Researcher",
    # "language": "en_us",
    # "groups": [1, 2],
    # "customAttributes": [{"attributeId": 1, "attributeValue": "value"}],
}

r = requests.post(f"{server}/Services/Users/", headers=headers, json=user)
```

### Update User (Admin)

> **CRITICAL: User Updates Replace ALL Fields**
>
> When updating a user via `POST /Services/Users/:userId`, you MUST include ALL fields
> you want to preserve. Any omitted fields will be cleared/reset, including group memberships!
>
> **Required fields:** `firstName`, `lastName`, `emailAddress`, `userName`, `timezone`
>
> **Common mistake:** Updating just `position` without including `groups` will remove
> the user from all groups.

```python
user_id = 17

# First, get the current user data
user = requests.get(f"{server}/Services/Users/{user_id}", headers=headers).json()

# Build update payload preserving ALL existing data
update_data = {
    "firstName": user['firstName'],
    "lastName": user['lastName'],
    "emailAddress": user['emailAddress'],
    "userName": user['userName'],
    "timezone": user['timezone'],
    # Update the field you want to change
    "position": "New Position Title",
    # IMPORTANT: Include groups to preserve group memberships!
    "groups": [1, 2],  # List of group IDs
}

r = requests.post(f"{server}/Services/Users/{user_id}", headers=headers, json=update_data)
```

### Update User Status (Admin)

```python
user_id = 1
# statusId: 1=Active, 3=Inactive
requests.post(
    f"{server}/Services/Users/{user_id}/Status",
    headers=headers,
    json={"statusId": 1}
)
```

---

## Groups API

Manage user groups and permissions.

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/Services/Groups/` | List all groups | Yes |
| GET | `/Services/Groups/:groupId` | Get group details | Yes |
| POST | `/Services/Groups/` | Create group | Admin |
| POST | `/Services/Groups/:groupId` | Update group | Admin |
| POST | `/Services/Groups/:groupId/Roles` | Change group roles | Admin |
| POST | `/Services/Groups/:groupId/Permissions` | Change group permissions | Admin |
| POST | `/Services/Groups/:groupId/Users` | Change group users | Admin |
| DELETE | `/Services/Groups/:groupId` | Delete group | Admin |

### List Groups

```python
r = requests.get(f"{server}/Services/Groups/", headers=headers)
groups = r.json().get("groups", [])

for group in groups:
    print(f"{group['id']}: {group['name']} (default: {group['isDefault']})")
```

### Get Group Details

> **Note:** The `users` field in group details returns URL paths, not user objects.
> You must parse the user IDs from these paths.

```python
group_id = 1
r = requests.get(f"{server}/Services/Groups/{group_id}", headers=headers)
group = r.json()

# Users are returned as URL paths like "/Services/Users/2"
user_urls = group.get('users', [])
user_ids = [int(url.split('/')[-1]) for url in user_urls]
print(f"Group {group['name']} has users: {user_ids}")
```

### Role IDs

| ID | Role |
|----|------|
| 1 | Group Admin |
| 2 | Application Admin |
| 3 | Resource Admin |
| 4 | Schedule Admin |

### Change Group Roles (Admin)

```python
group_id = 1
requests.post(
    f"{server}/Services/Groups/{group_id}/Roles",
    headers=headers,
    json={"roleIds": [1, 3]}  # Group Admin + Resource Admin
)
```

### Change Group Permissions (Admin)

```python
group_id = 1
requests.post(
    f"{server}/Services/Groups/{group_id}/Permissions",
    headers=headers,
    json={
        "permissions": [1, 2, 3],      # Resource IDs with full access
        "viewPermissions": [4, 5]       # Resource IDs with view-only
    }
)
```

### Change Group Users (Admin)

```python
group_id = 1
requests.post(
    f"{server}/Services/Groups/{group_id}/Users",
    headers=headers,
    json={"userIds": [1, 2, 3]}
)
```

---

## Accessories API

Manage accessories that can be added to reservations.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/Services/Accessories/` | List all accessories |
| GET | `/Services/Accessories/:accessoryId` | Get accessory details |

### List Accessories

```python
r = requests.get(f"{server}/Services/Accessories/", headers=headers)
accessories = r.json().get("accessories", [])

for acc in accessories:
    print(f"{acc['id']}: {acc['name']} (qty: {acc['quantityAvailable']})")
```

### Credit Applicability Values

| Value | Meaning |
|-------|---------|
| 1 | Per slot |
| 2 | Per reservation |

---

## Custom Attributes API

Manage custom attribute definitions.

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/Services/Attributes/Category/:categoryId` | Get attributes for category | Yes |
| GET | `/Services/Attributes/:attributeId` | Get attribute definition | Yes |
| POST | `/Services/Attributes/` | Create attribute | Admin |
| POST | `/Services/Attributes/:attributeId` | Update attribute | Admin |
| DELETE | `/Services/Attributes/:attributeId` | Delete attribute | Admin |

### Attribute Categories

| ID | Category |
|----|----------|
| 1 | Reservations |
| 2 | Users |
| 4 | Resources |
| 5 | Resource Types |

### Get Attributes by Category

```python
category_id = 1  # Reservations
r = requests.get(f"{server}/Services/Attributes/Category/{category_id}", headers=headers)
attributes = r.json().get("attributes", [])
```

### Field Types

- Text
- Checkbox
- Select list
- Date/time

---

## Error Handling

```python
r = requests.get(url, headers=headers)

if r.status_code == 200:
    data = r.json()
elif r.status_code == 201:
    print("Created successfully")
    data = r.json()
elif r.status_code == 401:
    print("Authentication failed - check API credentials")
elif r.status_code == 403:
    print("Permission denied - may require admin access")
elif r.status_code == 404:
    print("Resource not found")
elif r.status_code == 400:
    print(f"Bad request: {r.text}")
else:
    print(f"Error {r.status_code}: {r.text}")
```

---

## Response Structure

Most list endpoints return:

```json
{
  "resources": [...],
  "links": [
    {"href": "...", "title": "..."}
  ],
  "message": null
}
```

The top-level key varies: `resources`, `reservations`, `users`, `groups`, `schedules`, `accessories`, `attributes`.

---

## Complete Example Script

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["requests"]
# ///

import os
import requests
from datetime import datetime, timedelta

# Configuration
server = "https://scandium.mclean.harvard.edu"
api_id, api_key = os.environ["SCANDIUM_API_KEY"].split(":")

headers = {
    "X-Booked-ApiId": api_id,
    "X-Booked-ApiKey": api_key,
}

def get_current_user():
    """Get current authenticated user info."""
    r = requests.get(f"{server}/Services/Accounts/", headers=headers)
    r.raise_for_status()
    return r.json()

def list_resources():
    """List all resources the user can access."""
    r = requests.get(f"{server}/Services/Resources/", headers=headers)
    r.raise_for_status()
    return r.json().get("resources", [])

def list_reservations(start_date=None, end_date=None, resource_id=None):
    """List reservations with optional filters."""
    params = {}
    if start_date:
        params["startDateTime"] = start_date
    if end_date:
        params["endDateTime"] = end_date
    if resource_id:
        params["resourceId"] = resource_id

    r = requests.get(f"{server}/Services/Reservations/", headers=headers, params=params)
    r.raise_for_status()
    return r.json().get("reservations", [])

def create_reservation(resource_id, start, end, title, description=None):
    """Create a new reservation."""
    data = {
        "resourceId": resource_id,
        "startDateTime": start,
        "endDateTime": end,
        "title": title,
    }
    if description:
        data["description"] = description

    r = requests.post(f"{server}/Services/Reservations/", headers=headers, json=data)
    r.raise_for_status()
    return r.json()

def get_schedule_slots(schedule_id, start_date, end_date, resource_id=None):
    """Get availability slots for a schedule."""
    params = {
        "startDateTime": start_date,
        "endDateTime": end_date,
    }
    if resource_id:
        params["resourceId"] = resource_id

    r = requests.get(f"{server}/Services/Schedules/{schedule_id}/Slots", headers=headers, params=params)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    # Example usage
    user = get_current_user()
    print(f"Logged in as: {user['firstName']} {user['lastName']}")

    resources = list_resources()
    print(f"\nAvailable resources: {len(resources)}")
    for r in resources[:5]:
        print(f"  - {r['resourceId']}: {r['name']}")

    # Get this week's reservations
    today = datetime.now().strftime("%Y-%m-%d")
    next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    reservations = list_reservations(today, next_week)
    print(f"\nReservations this week: {len(reservations)}")
    for res in reservations[:5]:
        print(f"  - {res['referenceNumber']}: {res['title']}")
```

---

## Best Practices

### DO:
- Use API key auth for scripts (simpler than session management)
- Include date filters when querying reservations
- Handle all HTTP status codes appropriately
- Store API credentials in `$SCANDIUM_API_KEY` env var (format: `api_id:api_key`)
- Check `updateScope` when modifying recurring reservations

### DON'T:
- Hardcode credentials in scripts
- Query all reservations without date filters (slow)
- Forget the `/Services/` prefix on all endpoints
- Assume 404 is always an error (it's expected when checking existence)
- Assume status 200 means success (check for `referenceNumber` or `errors` in response)
- Use datetime strings without timezone offset
- Update a user without including ALL fields you want to preserve (updates replace, not merge)
- Forget to include `groups` when updating a user (they'll be removed from all groups!)

---

## Importing ICS Events

When importing from ICS/vCalendar format, map fields as follows:

| ICS Field | Booked Field | Notes |
|-----------|--------------|-------|
| `DTSTART` | `startDateTime` | Convert to ISO8601 with TZ offset |
| `DTEND` | `endDateTime` | Convert to ISO8601 with TZ offset |
| `SUMMARY` | `title` | May contain participants and "Confirmed-XX/XXX" scanned initials |
| `DESCRIPTION` | `description` | |
| `RRULE` | `recurrenceRule` | See conversion below |
| `CATEGORIES` | `customAttributes` | Map to appropriate attribute; if no exact PI match, retry with the first word |

### Converting RRULE to recurrenceRule

```python
# Example: RRULE:FREQ=WEEKLY;INTERVAL=4;UNTIL=20260711
# Converts to:
{
    "type": "weekly",
    "interval": 4,
    "weekdays": [1],  # Determine from DTSTART day of week
    "repeatTerminationDate": "2026-07-11T00:00:00+0000"
}
```

### ICS DateTime Conversion

```python
from datetime import datetime

def ics_to_iso(ics_dt):
    """Convert ICS datetime to ISO8601 with UTC offset.

    ICS format: 20260112T130000Z (Z = UTC)
    ISO format: 2026-01-12T13:00:00+0000
    """
    # Remove the Z suffix if present
    if ics_dt.endswith('Z'):
        ics_dt = ics_dt[:-1]
        tz_offset = "+0000"
    else:
        tz_offset = "+0000"  # Assume UTC if no suffix

    dt = datetime.strptime(ics_dt, "%Y%m%dT%H%M%S")
    return dt.strftime(f"%Y-%m-%dT%H:%M:%S{tz_offset}")

# Example usage:
# ics_to_iso("20260112T130000Z") -> "2026-01-12T13:00:00+0000"
```

### Parsing SUMMARY for participants and scanned initials

If SUMMARY includes lines like `Confirmed-XX` or `Confirmed-XXX` (two or three letters),
map the letters to custom attribute **Scanned Person Initials** (attribute id 2).
If SUMMARY includes `Name: email` lines, use the email to match participants.

### Resource selection

If a tool or script needs a resource name, the approved choices are:
- `P1 Prisma` (default)
- `P2 Prisma Fit`

---

## Helper Scripts

Helper scripts are available in the `scripts/` directory:

### `scripts/ics_to_booked.py`

Imports an ICS event into Booked Scheduler. Handles:
- DateTime format conversion
- Resource lookup by name
- User lookup by email for participants
- Custom attribute mapping
- Recurrence rule conversion

Usage:
```bash
./scripts/ics_to_booked.py event.ics --resource "P1 Prisma"
```

> **Fallback for parsing issues:** If the script fails to correctly parse the ICS content
> (SUMMARY, participants, attributes, recurrence, etc.) or produces nonsensical results,
> don't try to fix the script. Instead, manually inspect the ICS content and use your
> own judgment to extract the relevant fields and match them to resources/users/attributes,
> then call the API directly using `booked_api.py` or inline code.

### `scripts/booked_api.py`

Common API functions for Booked Scheduler. Import in your own scripts:

```python
from scripts.booked_api import BookedAPI

api = BookedAPI()
user = api.get_current_user()
resources = api.list_resources()
```
