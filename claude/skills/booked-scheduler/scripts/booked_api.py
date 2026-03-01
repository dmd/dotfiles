#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["requests"]
# ///
"""
Booked Scheduler API client library.

Common functions for interacting with the Booked Scheduler API at scandium.mclean.harvard.edu.

Usage:
    from booked_api import BookedAPI

    api = BookedAPI()
    user = api.get_current_user()
    resources = api.list_resources()
"""

import json
import os
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any


class BookedAPI:
    """Client for Booked Scheduler API."""

    _RESERVATION_QUERY_HARD_LIMIT = 1000

    def __init__(self, server: str = None, api_id: str = None, api_key: str = None):
        """Initialize the API client.

        Args:
            server: Server URL (default: from env or scandium.mclean.harvard.edu)
            api_id: API ID (default: from SCANDIUM_API_KEY env var)
            api_key: API Key (default: from SCANDIUM_API_KEY env var)
        """
        self.server = server or os.environ.get(
            "BOOKED_SERVER", "https://scandium.mclean.harvard.edu"
        )

        if api_id and api_key:
            self._api_id = api_id
            self._api_key = api_key
        else:
            creds = os.environ.get("SCANDIUM_API_KEY", "")
            if ":" in creds:
                self._api_id, self._api_key = creds.split(":", 1)
            else:
                raise ValueError(
                    "SCANDIUM_API_KEY environment variable must be set (format: api_id:api_key)"
                )

        self.headers = {
            "X-Booked-ApiId": self._api_id,
            "X-Booked-ApiKey": self._api_key,
        }
        self._session = requests.Session()

        self._user_id: Optional[int] = None

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        json: Dict = None,
        expect_json: bool = True,
    ) -> Dict | str:
        """Make an API request."""
        url = f"{self.server}/Services/{endpoint.lstrip('/')}"
        r = self._session.request(
            method,
            url,
            headers=self.headers,
            params=params,
            json=json,
        )
        r.raise_for_status()
        if not expect_json:
            return r.text
        try:
            return r.json()
        except requests.exceptions.JSONDecodeError as exc:
            snippet = r.text[:500].strip()
            raise RuntimeError(
                f"Non-JSON response from {endpoint}: {snippet or '<empty>'}"
            ) from exc

    # ==================== Account Methods ====================

    def get_current_user(self) -> Dict:
        """Get current authenticated user info."""
        attempts = [
            ("Accounts/", None),
            ("Accounts/Current", None),
            ("Users/Current", None),
        ]
        last_result = None
        for endpoint, params in attempts:
            try:
                result = self._request("GET", endpoint, params=params, expect_json=True)
                last_result = result
                if isinstance(result, dict):
                    if result.get("message") and not (
                        result.get("userId") or result.get("id") or result.get("user")
                    ):
                        continue
                    return result
            except (requests.HTTPError, RuntimeError):
                pass
            try:
                raw = self._request("GET", endpoint, params=params, expect_json=False)
            except requests.HTTPError:
                continue
            last_result = raw
            if isinstance(raw, str) and raw.strip():
                try:
                    parsed = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                last_result = parsed
                if isinstance(parsed, dict):
                    if parsed.get("message") and not (
                        parsed.get("userId") or parsed.get("id") or parsed.get("user")
                    ):
                        continue
                    return parsed
        raise RuntimeError(f"Unexpected current user response: {last_result!r}")

    def get_user_id(self) -> int:
        """Get the current user's ID (cached)."""
        if self._user_id is None:
            env_user_id = os.environ.get("SCANDIUM_USER_ID", "").strip()
            if env_user_id:
                self._user_id = int(env_user_id)
            else:
                env_user_email = os.environ.get("SCANDIUM_USER_EMAIL", "").strip()
                if not env_user_email:
                    env_user_email = "ddrucker@mclean.harvard.edu"
                if env_user_email:
                    user = self.find_user_by_email(env_user_email)
                    if user and user.get("id"):
                        self._user_id = int(user["id"])
                if self._user_id is None:
                    user = self.get_current_user()
                    self._user_id = (
                        user.get("userId")
                        or user.get("id")
                        or user.get("user", {}).get("userId")
                        or user.get("user", {}).get("id")
                    )
            if self._user_id is None:
                raise RuntimeError(
                    "Unable to resolve user id from API. Set SCANDIUM_USER_ID "
                    "or SCANDIUM_USER_EMAIL."
                )
        return self._user_id

    # ==================== Resource Methods ====================

    def list_resources(self) -> List[Dict]:
        """List all resources the user can access."""
        return self._request("GET", "Resources/").get("resources", [])

    def get_resource(self, resource_id: int) -> Dict:
        """Get a single resource by ID."""
        return self._request("GET", f"Resources/{resource_id}")

    def find_resource_by_name(self, name: str) -> Optional[Dict]:
        """Find a resource by name (partial match)."""
        resources = self.list_resources()
        for r in resources:
            if name.lower() in r.get("name", "").lower():
                return r
        return None

    # ==================== User Methods ====================

    def list_users(self, **filters) -> List[Dict]:
        """List users with optional filters (email, firstName, lastName, etc.)."""
        return self._request("GET", "Users/", params=filters).get("users", [])

    def find_user_by_email(self, email: str) -> Optional[Dict]:
        """Find a user by exact email match."""
        users = self.list_users(email=email)
        for u in users:
            if u.get("emailAddress", "").lower() == email.lower():
                return u
        return None

    def get_user(self, user_id: int) -> Dict:
        """Get a single user by ID."""
        return self._request("GET", f"Users/{user_id}")

    # ==================== Schedule Methods ====================

    def list_schedules(self) -> List[Dict]:
        """List all schedules."""
        return self._request("GET", "Schedules/").get("schedules", [])

    def get_schedule(self, schedule_id: int) -> Dict:
        """Get a single schedule by ID."""
        return self._request("GET", f"Schedules/{schedule_id}")

    def get_schedule_slots(
        self,
        schedule_id: int,
        start_date: str,
        end_date: str,
        resource_id: int = None,
    ) -> Dict:
        """Get availability slots for a schedule."""
        params = {"startDateTime": start_date, "endDateTime": end_date}
        if resource_id:
            params["resourceId"] = resource_id
        return self._request("GET", f"Schedules/{schedule_id}/Slots", params=params)

    # ==================== Reservation Methods ====================

    @staticmethod
    def _build_reservation_query_params(
        start_date: str = None,
        end_date: str = None,
        resource_id: int = None,
        user_id: int = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if start_date:
            params["startDateTime"] = start_date
        if end_date:
            params["endDateTime"] = end_date
        if resource_id:
            params["resourceId"] = resource_id
        if user_id:
            params["userId"] = user_id
        return params

    @staticmethod
    def _parse_ymd(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return None

    @staticmethod
    def _reservation_dedupe_key(reservation: Dict[str, Any]) -> tuple:
        ref = reservation.get("referenceNumber")
        if ref:
            return ("ref", ref)
        return (
            "fallback",
            reservation.get("resourceId"),
            reservation.get("startDate"),
            reservation.get("endDate"),
            reservation.get("title"),
            reservation.get("description"),
        )

    def list_reservations(
        self,
        start_date: str = None,
        end_date: str = None,
        resource_id: int = None,
        user_id: int = None,
    ) -> List[Dict]:
        """List reservations with optional filters.

        The Booked API currently caps reservation list responses at 1000 rows and
        does not expose working pagination params on this deployment. When the
        first query returns 1000 rows and both bounds are YYYY-MM-DD, this method
        automatically splits the range and merges/dedupes the results.
        """
        params = self._build_reservation_query_params(
            start_date=start_date,
            end_date=end_date,
            resource_id=resource_id,
            user_id=user_id,
        )
        first_chunk = self._request("GET", "Reservations/", params=params).get(
            "reservations", []
        )
        if len(first_chunk) < self._RESERVATION_QUERY_HARD_LIMIT:
            return first_chunk

        start_dt = self._parse_ymd(start_date)
        end_dt = self._parse_ymd(end_date)
        if not start_dt or not end_dt or start_dt >= end_dt:
            return first_chunk

        pending = [(start_dt, end_dt, first_chunk)]
        merged: List[Dict] = []
        seen = set()

        while pending:
            window_start, window_end, chunk = pending.pop()
            if chunk is None:
                window_params = self._build_reservation_query_params(
                    start_date=window_start.strftime("%Y-%m-%d"),
                    end_date=window_end.strftime("%Y-%m-%d"),
                    resource_id=resource_id,
                    user_id=user_id,
                )
                chunk = self._request("GET", "Reservations/", params=window_params).get(
                    "reservations", []
                )

            window_days = (window_end - window_start).days
            if len(chunk) >= self._RESERVATION_QUERY_HARD_LIMIT and window_days > 1:
                midpoint = window_start + timedelta(days=window_days // 2)
                if midpoint <= window_start:
                    midpoint = window_start + timedelta(days=1)
                pending.append((midpoint, window_end, None))
                pending.append((window_start, midpoint, None))
                continue

            for reservation in chunk:
                dedupe_key = self._reservation_dedupe_key(reservation)
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                merged.append(reservation)

        return merged or first_chunk

    def get_reservation(self, reference_number: str) -> Dict:
        """Get a single reservation by reference number."""
        return self._request("GET", f"Reservations/{reference_number}")

    def create_reservation(
        self,
        resource_id: int,
        start_datetime: str,
        end_datetime: str,
        title: str,
        description: str = None,
        user_id: int = None,
        participants: List[int] = None,
        invitees: List[int] = None,
        custom_attributes: List[Dict] = None,
        recurrence_rule: Dict = None,
    ) -> Dict:
        """Create a new reservation.

        Args:
            resource_id: ID of the resource to book
            start_datetime: Start time in ISO8601 format with TZ (e.g., "2026-01-15T14:00:00+0000")
            end_datetime: End time in ISO8601 format with TZ
            title: Reservation title
            description: Optional description
            user_id: Owner user ID (defaults to current user)
            participants: List of user IDs to add as participants
            invitees: List of user IDs to invite
            custom_attributes: List of {"attributeId": id, "attributeValue": value}
            recurrence_rule: Recurrence configuration (see skill.md for format)

        Returns:
            API response with referenceNumber on success, errors on failure

        Note:
            Due to an API quirk, participants may not be added on initial creation.
            This method automatically performs a follow-up update to ensure
            participants are added.
        """
        resolved_user_id = user_id or self.get_user_id()

        data = {
            "resourceId": resource_id,
            "userId": resolved_user_id,
            "startDateTime": start_datetime,
            "endDateTime": end_datetime,
            "title": title,
        }

        if description:
            data["description"] = description
        if participants:
            data["participants"] = participants
        if invitees:
            data["invitees"] = invitees
        if custom_attributes:
            data["customAttributes"] = custom_attributes
        if recurrence_rule:
            data["recurrenceRule"] = recurrence_rule

        result = self._request("POST", "Reservations/", json=data)

        # Handle participants quirk: they often don't get added on creation
        # Do a follow-up update to ensure they're added
        if participants and result.get("referenceNumber"):
            ref_num = result["referenceNumber"]
            created = self.get_reservation(ref_num)

            # Check if participants were actually added
            created_participant_ids = [
                int(p.get("userId")) for p in created.get("participants", [])
            ]
            if set(participants) != set(created_participant_ids):
                # Need to update to add participants
                # Use startDate/endDate from the created reservation (API returns these keys)
                self.update_reservation(
                    reference_number=ref_num,
                    resource_id=resource_id,
                    start_datetime=created.get("startDate"),
                    end_datetime=created.get("endDate"),
                    title=title,
                    update_scope="full",
                    user_id=resolved_user_id,
                    description=description,
                    participants=participants,
                    invitees=invitees,
                    custom_attributes=custom_attributes,
                )

        return result

    def update_reservation(
        self,
        reference_number: str,
        resource_id: int,
        start_datetime: str,
        end_datetime: str,
        title: str,
        update_scope: str = "full",
        **kwargs,
    ) -> Dict:
        """Update an existing reservation.

        Args:
            reference_number: Reservation reference number
            update_scope: "this", "full", or "future"
            **kwargs: Same as create_reservation
        """
        data = {
            "resourceId": resource_id,
            "userId": kwargs.get("user_id") or self.get_user_id(),
            "startDateTime": start_datetime,
            "endDateTime": end_datetime,
            "title": title,
        }

        for key in [
            "description",
            "participants",
            "invitees",
            "custom_attributes",
            "recurrence_rule",
        ]:
            if key in kwargs and kwargs[key]:
                # Convert snake_case to camelCase for API
                api_key = key.replace("_", " ").title().replace(" ", "")
                api_key = api_key[0].lower() + api_key[1:]
                data[api_key] = kwargs[key]

        url = f"{self.server}/Services/Reservations/{reference_number}"
        r = requests.post(
            url, headers=self.headers, params={"updateScope": update_scope}, json=data
        )
        r.raise_for_status()
        return r.json()

    def delete_reservation(
        self, reference_number: str, update_scope: str = "this"
    ) -> Dict:
        """Delete a reservation.

        Args:
            reference_number: Reservation reference number
            update_scope: "this", "full", or "future" for recurring
        """
        url = f"{self.server}/Services/Reservations/{reference_number}"
        r = requests.delete(
            url, headers=self.headers, params={"updateScope": update_scope}
        )
        r.raise_for_status()
        return r.json() if r.text else {}

    # ==================== Attribute Methods ====================

    def get_reservation_attributes(self) -> List[Dict]:
        """Get custom attributes for reservations (category 1)."""
        return self._request("GET", "Attributes/Category/1").get("attributes", [])

    def find_attribute_value(
        self, attribute_id: int, search_value: str
    ) -> Optional[str]:
        """Find the closest matching value for a select-list attribute.

        Args:
            attribute_id: The attribute ID
            search_value: Value to search for (case-insensitive partial match)

        Returns:
            The matching value from possibleValues, or None
        """
        attrs = self.get_reservation_attributes()
        for attr in attrs:
            if attr.get("id") == attribute_id:
                possible = attr.get("possibleValues", [])
                # Try exact match first
                for v in possible:
                    if v.lower() == search_value.lower():
                        return v
                # Try partial match
                for v in possible:
                    if search_value.lower() in v.lower():
                        return v
        return None


# ==================== Utility Functions ====================


def ics_datetime_to_iso(ics_dt: str) -> str:
    """Convert ICS datetime to ISO8601 with UTC offset.

    Args:
        ics_dt: ICS format datetime (e.g., "20260112T130000Z")

    Returns:
        ISO8601 format with timezone (e.g., "2026-01-12T13:00:00+0000")
    """
    # Remove the Z suffix if present
    if ics_dt.endswith("Z"):
        ics_dt = ics_dt[:-1]
        tz_offset = "+0000"
    else:
        tz_offset = "+0000"  # Assume UTC if no suffix

    dt = datetime.strptime(ics_dt, "%Y%m%dT%H%M%S")
    return dt.strftime(f"%Y-%m-%dT%H:%M:%S{tz_offset}")


def parse_rrule(rrule: str, start_dt: datetime) -> Dict:
    """Parse an ICS RRULE into Booked recurrenceRule format.

    Args:
        rrule: ICS RRULE string (e.g., "FREQ=WEEKLY;INTERVAL=4;UNTIL=20260711")
        start_dt: Start datetime (used to determine weekday)

    Returns:
        Booked recurrenceRule dictionary
    """
    parts = {}
    for part in rrule.split(";"):
        if "=" in part:
            key, value = part.split("=", 1)
            parts[key] = value

    freq_map = {
        "DAILY": "daily",
        "WEEKLY": "weekly",
        "MONTHLY": "monthly",
        "YEARLY": "yearly",
    }

    result = {
        "type": freq_map.get(parts.get("FREQ", ""), "none"),
        "interval": int(parts.get("INTERVAL", 1)),
    }

    # For weekly, include the weekday from start date
    # Python: 0=Monday, Booked: 0=Sunday, so add 1 and mod 7
    if result["type"] == "weekly":
        python_weekday = start_dt.weekday()  # 0=Monday in Python
        booked_weekday = (python_weekday + 1) % 7  # Convert to 0=Sunday
        result["weekdays"] = [booked_weekday]

    # Parse UNTIL date
    if "UNTIL" in parts:
        until = parts["UNTIL"]
        if len(until) == 8:  # YYYYMMDD format
            until_dt = datetime.strptime(until, "%Y%m%d")
        else:
            until_dt = datetime.strptime(until[:15], "%Y%m%dT%H%M%S")
        result["repeatTerminationDate"] = until_dt.strftime("%Y-%m-%dT00:00:00+0000")

    return result


if __name__ == "__main__":
    # Example usage
    api = BookedAPI()

    user = api.get_current_user()
    print(f"Logged in as: {user['firstName']} {user['lastName']}")

    resources = api.list_resources()
    print(f"\nAvailable resources: {len(resources)}")
    for r in resources[:5]:
        print(f"  - {r['resourceId']}: {r['name']}")

    # Get this week's reservations
    today = datetime.now().strftime("%Y-%m-%d")
    next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    reservations = api.list_reservations(today, next_week)
    print(f"\nReservations this week: {len(reservations)}")
    for res in reservations[:5]:
        print(f"  - {res['referenceNumber']}: {res['title']}")
