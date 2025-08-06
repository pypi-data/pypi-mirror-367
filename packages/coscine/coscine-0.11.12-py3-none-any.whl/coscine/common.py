###############################################################################
# Coscine Python SDK
# Copyright (c) 2020-2025 RWTH Aachen University
# Licensed under the terms of the MIT License
# For more information on Coscine visit https://www.coscine.de/.
###############################################################################

"""
Provides common classes shared among multiple modules.
"""

from datetime import date, datetime
from isodate import parse_datetime


class MaintenanceNotice:
    """
    Models maintenance notices set in Coscine.
    """

    _data: dict

    @property
    def title(self) -> str:
        """
        The title or name of the maintenance notice.
        """
        return self._data.get("displayName") or ""

    @property
    def link(self) -> str:
        """
        The URL link to the detailed maintenance notice.
        """
        return self._data.get("href") or ""

    @property
    def type(self) -> str:
        """
        The type of maintenance.
        """
        return self._data.get("type") or ""

    @property
    def body(self) -> str:
        """
        The body or description of the notice.
        """
        return self._data.get("body") or ""

    @property
    def starts_date(self) -> date:
        """
        Date when the maintenance goes active.
        """
        value: str = self._data.get("startsDate") or "1998-01-01T00:00:00Z"
        return parse_datetime(value).date()

    @property
    def ends_date(self) -> date:
        """
        Date when the maintenance ends.
        """
        value = self._data.get("endsDate") or "1998-01-01T00:00:00Z"
        return parse_datetime(value).date()

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.title


class SearchResult:
    """
    This class models the search results returned by Coscine upon
    a search request.
    """

    _data: dict

    @property
    def uri(self) -> str:
        """
        Link to the result (i.e. a project or resource or file).
        """
        return self._data.get("uri") or ""

    @property
    def type(self) -> str:
        """
        The search category the result falls into (e.g. project).
        """
        return self._data.get("type") or ""

    @property
    def source(self) -> str:
        """
        The source text that matches in some way or another the search query.
        """
        return self._data.get("source") or ""

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.uri


class ApiToken:
    """
    This class models the Coscine API token.
    """

    _data: dict

    @property
    def id(self) -> str:
        """
        Unique Coscine-internal identifier for the API token.
        """
        return self._data.get("id") or ""

    @property
    def name(self) -> str:
        """
        The name assigned to the API token by the creator upon creation.
        """
        return self._data.get("name") or ""

    @property
    def created(self) -> date:
        """
        Timestamp of when the API token was created.
        """
        value = self._data.get("creationDate") or "1998-01-01T00:00:00Z"
        return parse_datetime(value).date()

    @property
    def expires(self) -> date:
        """
        Timestamp of when the API token will expire.
        """
        value = self._data.get("expiryDate") or "1998-01-01T00:00:00Z"
        return parse_datetime(value).date()

    @property
    def expired(self) -> bool:
        """
        Evaluates to True if the API token is expired.
        """
        return datetime.now().date() > self.expires

    @property
    def owner(self) -> str:
        """
        Unique Coscine-internal user id of the owner of the API token.
        """
        return self._data["owner"]["id"]

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.name


class Language:
    """
    Models the languages available in Coscine.
    """

    _data: dict

    @property
    def id(self) -> str:
        """
        Unique and constant Coscine internal identifier for
        the respective language option.
        """
        return self._data.get("id") or ""

    @property
    def name(self) -> str:
        """
        The full name of the language option.
        """
        return self._data.get("displayName") or ""

    @property
    def abbreviation(self) -> str:
        """
        The abbreviated name of the language option.
        """
        return self._data.get("abbreviation") or ""

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.name


class AcademicTitle:
    """
    Models the Academic Titles available in Coscine.
    """

    _data: dict

    @property
    def id(self) -> str:
        """
        Unique and constant Coscine internal identifier for
        the respective Academic Title.
        """
        return self._data.get("id") or ""

    @property
    def name(self) -> str:
        """
        The name of the Academic Title, e.g. "Prof." or "Dr."
        """
        return self._data.get("displayName") or ""

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.name


class Discipline:
    """
    Models the disciplines available in Coscine.
    """

    _data: dict

    @property
    def id(self) -> str:
        """
        The Coscine-internal unique identifier for the discipline.
        """
        return self._data.get("id") or ""

    @property
    def uri(self) -> str:
        """
        The uri of the discipline.
        """
        return self._data.get("uri") or ""

    @property
    def name(self) -> str:
        """
        The human-readable name of the discipline.
        """
        return self._data.get("displayNameEn") or ""

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.name

    def serialize(self) -> dict:
        """
        Returns the machine-readable representation of the discipline
        data instance.
        """
        return self._data


class License:
    """
    Models the licenses available in Coscine.
    """

    _data: dict

    @property
    def id(self) -> str:
        """
        The Coscine-internal unique identifier for the license.
        """
        return self._data.get("id") or ""

    @property
    def name(self) -> str:
        """
        The human-readable name of the license.
        """
        return self._data.get("displayName") or ""

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.name

    def serialize(self) -> dict:
        """
        Returns the machine-readable representation of the license
        data instance.
        """
        return self._data


class Organization:
    """
    Models organization information for organizations in Coscine.
    """

    _data: dict

    @property
    def uri(self) -> str:
        """
        The organization's ror uri.
        """
        return self._data.get("uri") or ""

    @property
    def name(self) -> str:
        """
        The full name of the organization.
        """
        return self._data.get("displayName") or ""

    @property
    def email(self) -> str:
        """
        Contact email address of the organization.
        """
        return self._data.get("email") or ""

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.name

    def serialize(self) -> dict:
        """
        Returns the machine-readable representation of the organization
        data instance.
        """
        return self._data


class User:
    """
    This class provides an interface around userdata in Coscine.
    """

    _data: dict

    @property
    def id(self) -> str:
        """
        The unique Coscine-internal user id for a user.
        """
        return self._data.get("id") or ""

    @property
    def display_name(self) -> str:
        """
        The full name of a Coscine user as displayed
        in the Coscine web interface.
        """
        return self._data.get("displayName") or ""

    @property
    def first_name(self) -> str:
        """
        The first name of a Coscine user.
        """
        return self._data.get("givenName") or ""

    @property
    def last_name(self) -> str:
        """
        The family name of a Coscine user.
        """
        return self._data.get("familyName") or ""

    @property
    def email(self) -> str | list[str]:
        """
        The email address or list of email addresses of a user.
        In case the user has not associated an email address with their
        account 'None' is returned.
        """
        if "email" in self._data:
            return self._data.get("email") or ""
        return self._data.get("emails") or []

    @property
    def title(self) -> AcademicTitle | None:
        """
        The academic title of a user.
        In case the user has not set a title in their user profile
        'None' is returned.
        """
        title = self._data.get("title")
        if title is not None:
            title = AcademicTitle(title)
        return title

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.display_name


class Visibility:
    """
    Models the visibility settings available in Coscine.
    """

    _data: dict

    @property
    def id(self) -> str:
        """
        Coscine-internal identifier for the visibility setting.
        """
        return self._data.get("id") or ""

    @property
    def name(self) -> str:
        """
        Human-readable name of the visibility setting.
        """
        return self._data.get("displayName") or ""

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.name

    def serialize(self) -> dict:
        """
        Returns the machine-readable representation of the visibility
        data instance.
        """
        return self._data
