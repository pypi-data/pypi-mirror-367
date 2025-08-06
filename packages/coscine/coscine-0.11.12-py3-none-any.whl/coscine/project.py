###############################################################################
# Coscine Python SDK
# Copyright (c) 2020-2025 RWTH Aachen University
# Licensed under the terms of the MIT License
# For more information on Coscine visit https://www.coscine.de/.
###############################################################################

""" """

from __future__ import annotations
from typing import TYPE_CHECKING
from os import mkdir
from os.path import isdir
from posixpath import join as join_paths
from datetime import date
from textwrap import wrap
from isodate import parse_datetime
from tabulate import tabulate
from coscine.common import Discipline, License, Organization, User, Visibility
from coscine.resource import Resource, ResourceType, ResourceQuota
from coscine.metadata import ApplicationProfileInfo
from coscine.exceptions import NotFoundError, TooManyResults

if TYPE_CHECKING:
    from coscine.client import ApiClient


class ProjectQuota:
    """
    Projects have a set of storage space quotas. This class models
    the quota data returned by Coscine.
    """

    _data: dict

    @property
    def project_id(self) -> str:
        """
        The ID of the associated project.
        """
        return self._data.get("projectId") or ""

    @property
    def total_used(self) -> int:
        """
        The total used storage space in bytes.
        """
        return int(self._data["totalUsed"]["value"] * 1024**3)

    @property
    def total_reserved(self) -> int:
        """
        The total reserved storage space in bytes.
        """
        return int(self._data["totalReserved"]["value"] * 1024**3)

    @property
    def allocated(self) -> int:
        """
        The allocated storage space in bytes.
        """
        return int(self._data["allocated"]["value"] * 1024**3)

    @property
    def maximum(self) -> int:
        """
        The maximum available storage space in bytes.
        """
        value = self._data["maximum"]["value"] or 0
        return value * int(1024**3)

    @property
    def resource_type(self) -> ResourceType:
        """
        The associated resource type.
        """
        return ResourceType(self._data["resourceType"])

    @property
    def resource_quotas(self) -> list[ResourceQuota]:
        """
        The list of used resource quotas for the project.
        """
        return [ResourceQuota(data) for data in self._data["resourceQuotas"]]

    def __init__(self, data: dict) -> None:
        self._data = data


class ProjectRole:
    """
    Models roles that can be assumed by project members
    within a Coscine project.
    """

    _data: dict

    @property
    def id(self) -> str:
        """
        Unique and constant Coscine-internal identifier of the role.
        """
        return self._data.get("id") or ""

    @property
    def name(self) -> str:
        """
        Name of the role.
        """
        return self._data.get("displayName") or ""

    @property
    def description(self) -> str:
        """
        Description for the role.
        """
        return self._data.get("description") or ""

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.name


class ProjectMember:
    """
    This class models the members of a Coscine project.
    """

    project: Project
    _data: dict

    @property
    def id(self) -> str:
        """
        Unique Coscine-internal project member identifier.
        """
        return self._data.get("id") or ""

    @property
    def user(self) -> User:
        """
        The user in Coscine that represents the project member.
        """
        return User(self._data["user"])

    @property
    def role(self) -> ProjectRole:
        """
        The role of the member within the project.
        """
        return ProjectRole(self._data["role"])

    @role.setter
    def role(self, role: ProjectRole) -> None:
        uri = self.project.client.uri("projects", self.project.id, "members", self.id)
        self.project.client.put(uri, json={"roleId": role.id})

    def __init__(self, project: Project, data: dict) -> None:
        self.project = project
        self._data = data

    def __str__(self) -> str:
        return f"{self.user.display_name} as {self.role}"


class ProjectInvitation:
    """
    Models external user invitations via email in Coscine.
    """

    _data: dict

    @property
    def id(self) -> str:
        """
        Unique Coscine-internal identifier for the invitation.
        """
        return self._data.get("id") or ""

    @property
    def expires(self) -> date:
        """
        Timestamp of when the invitation expires.
        """
        value = self._data.get("expirationDate") or ""
        return parse_datetime(value)

    @property
    def email(self) -> str:
        """
        The email address of the invited user.
        """
        return self._data.get("email") or ""

    @property
    def issuer(self) -> User:
        """
        The user in Coscine who sent the invitation.
        """
        return User(self._data["issuer"])

    @property
    def project_id(self) -> str:
        """
        Project ID of the project the invitation applies to.
        """
        return self._data["project"]["id"]

    @property
    def role(self) -> ProjectRole:
        """
        Role assigned to the invited user.
        """
        return ProjectRole(self._data["role"])

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return f"{self.email} as {self.role.name}"


class Project:
    """
    Projects in Coscine contains resources.
    """

    client: ApiClient

    _data: dict

    @property
    def id(self) -> str:
        """
        Unique Coscine-internal project identifier.
        """
        return self._data.get("id") or ""

    @property
    def name(self) -> str:
        """
        The full project name as set in the project settings.
        """
        return self._data.get("name") or ""

    @name.setter
    def name(self, value: str) -> None:
        self._data["name"] = value

    @property
    def display_name(self) -> str:
        """
        The shortened project name as displayed in
        the Coscine web interface.
        """
        return self._data.get("displayName") or ""

    @display_name.setter
    def display_name(self, value: str) -> None:
        self._data["displayName"] = value

    @property
    def description(self) -> str:
        """
        The project description.
        """
        return self._data.get("description") or ""

    @description.setter
    def description(self, value: str) -> None:
        self._data["description"] = value

    @property
    def principal_investigators(self) -> str:
        """
        The project investigators.
        """
        return self._data.get("principleInvestigators") or ""

    @principal_investigators.setter
    def principal_investigators(self, value: str) -> None:
        self._data["principleInvestigators"] = value

    @property
    def start_date(self) -> date:
        """
        Start of project lifecycle timestamp.
        """
        value = self._data.get("startDate") or "1998-01-01T00:00:00Z"
        return parse_datetime(value)

    @start_date.setter
    def start_date(self, value: date) -> None:
        self._data["startDate"] = value

    @property
    def end_date(self) -> date:
        """
        End of project lifecycle timestamp.
        """
        value = self._data.get("endDate") or "1998-01-01T00:00:00Z"
        return parse_datetime(value)

    @end_date.setter
    def end_date(self, value: date) -> None:
        self._data["endDate"] = value

    @property
    def keywords(self) -> list[str]:
        """
        Project keywords for better discoverability.
        """
        return self._data.get("keywords") or []

    @keywords.setter
    def keywords(self, value: list[str]) -> None:
        self._data["keywords"] = value

    @property
    def grant_id(self) -> str:
        """
        Project grant id.
        """
        return self._data.get("grantId") or ""

    @grant_id.setter
    def grant_id(self, value: str) -> None:
        self._data["grantId"] = value

    @property
    def slug(self) -> str:
        """
        Project slug - usually a combination out of original
        project name and some arbitrary Coscine-internal
        data appended to it.
        """
        return self._data.get("slug") or ""

    @property
    def pid(self) -> str:
        """
        Project Persistent Identifier.
        """
        return self._data.get("pid") or ""

    @property
    def creator(self) -> str:
        """
        Project creator user ID.
        """
        creator = self._data.get("creator")
        if creator:
            return creator.get("id") or ""
        return ""

    @property
    def created(self) -> date:
        """
        Timestamp of when the project was created.
        If 1998-01-01T00:00:00Z is returned, then the created() value is erroneous
        or missing.
        """
        value = self._data.get("creationDate") or "1998-01-01T00:00:00Z"
        return parse_datetime(value)

    @property
    def organizations(self) -> list[Organization]:
        """
        Organizations participating in the project.
        """
        values = self._data.get("organizations", [])
        return [Organization(data) for data in values]

    @property
    def disciplines(self) -> list[Discipline]:
        """
        Scientific disciplines the project is involved with.
        """
        values = self._data.get("disciplines") or []
        return [Discipline(data) for data in values]

    @disciplines.setter
    def disciplines(self, value: list[Discipline]) -> None:
        self._data["disciplines"] = [discipline.serialize() for discipline in value]

    @property
    def visibility(self) -> Visibility:
        """
        Project visibility setting.
        """
        return Visibility(self._data["visibility"])

    @visibility.setter
    def visibility(self, value: Visibility) -> None:
        self._data["visibility"] = value.serialize()

    @property
    def url(self) -> str:
        """
        Project URL - makes the project accessible in the web browser.
        """
        return f"{self.client.base_url}/p/{self.slug}"

    def __init__(self, client: ApiClient, data: dict) -> None:
        self.client = client
        self._data = data

    def __str__(self) -> str:
        return tabulate(
            [
                ("ID", self.id),
                ("Name", self.name),
                ("Display Name", self.display_name),
                ("Description", "\n".join(wrap(self.description))),
                (
                    "Principal Investigators",
                    "\n".join(wrap(self.principal_investigators)),
                ),
                ("Disciplines", "\n".join([str(it) for it in self.disciplines])),
                ("Organizations", "\n".join([str(it) for it in self.organizations])),
                ("Start Date", self.start_date),
                ("End Date", self.end_date),
                ("Date created", self.created),
                ("Creator", self.creator),
                ("Grant ID", self.grant_id),
                ("PID", self.pid),
                ("Slug", self.slug),
                ("Keywords", ",".join(self.keywords)),
                ("Visibility", self.visibility),
            ],
            disable_numparse=True,
        )

    def match(self, attribute: property, key: str) -> bool:
        """
        Attempts to match the project via the given property
        and property value.
        Filterable properties:
        * Project.id
        * Project.pid
        * Project.name
        * Project.display_name
        * Project.url

        Returns
        -------
        True
            If its a match ♥
        False
            Otherwise :(
        """
        if (
            (attribute is Project.id and self.id == key)
            or (attribute is Project.pid and self.pid == key)
            or (attribute is Project.name and self.name == key)
            or (attribute is Project.url and self.url == key)
            or ((attribute is Project.display_name) and (self.display_name == key))
        ):
            return True
        return False

    def serialize(self) -> dict:
        """
        Marshals the project metadata into machine-readable format.
        """
        return {
            "name": self.name,
            "displayName": self.display_name,
            "description": self.description,
            "startDate": self.start_date.isoformat(),
            "endDate": self.end_date.isoformat(),
            "principleInvestigators": self.principal_investigators,
            "disciplines": [discipline.serialize() for discipline in self.disciplines],
            "organizations": [
                organization.serialize() for organization in self.organizations
            ],
            "visibility": self.visibility.serialize(),
            "keywords": self.keywords,
            "grantId": self.grant_id,
            "slug": self.slug,
            "pid": self.pid,
        }

    def delete(self) -> None:
        """
        Deletes the project on the Coscine servers.
        Be careful when using this function in your code, as users
        should be prevented from accidentially triggering it!
        Best to prompt the user before calling this function on whether
        they really wish to delete their project.
        """
        uri = self.client.uri("projects", self.id)
        self.client.delete(uri)

    def resources(self) -> list[Resource]:
        """
        Retrieves a list of all resources of the project.
        """
        uri = self.client.uri("projects", f"{self.id}", "resources")
        return [
            Resource(self, item)
            for page in self.client.get(uri).pages()
            for item in page.data
        ]

    # This is now required to access s3 options as they are no longer
    # sent with the resources() endpoint due to performance optimizations
    # in the Coscine API. Results in an additional request for a specific
    # resource.
    def _fetch_specific_resource_via_id(self, id: str) -> Resource:
        uri = self.client.uri("projects", f"{self.id}", "resources", id)
        return Resource(self, self.client.get(uri).data)

    def resource(
        self, key: str, attribute: property = Resource.display_name
    ) -> Resource:
        """
        Returns a single resource via one of its properties.
        The key can be specified to match any of the ResourceProperty items.
        """
        if attribute == Resource.id:
            return self._fetch_specific_resource_via_id(key)
        resources = self.resources()
        results = list(
            filter(lambda resource: resource.match(attribute, key), resources)
        )
        if len(results) > 1:
            raise TooManyResults(
                f"Found more than 1 resource matching the key '{key}'. "
                "Certain properties such as the name of a resource "
                "allow for duplicates among other resources."
            )
        if len(results) == 0:
            raise NotFoundError(f"Failed to find a resource via the key '{key}'! ")
        # Required for access to the resourcetypeoptions DTO
        return self._fetch_specific_resource_via_id(results[0].id)

    def download(self, path: str = "./") -> None:
        """
        Downloads the project to the local directory path.
        """
        path = join_paths(path, self.display_name, "")
        if not isdir(path):
            mkdir(path)
        for resource in self.resources():
            resource.download(path)

    def add_member(self, user: User, role: ProjectRole) -> None:
        """
        Adds the project member of another project to the current project.
        The owner of the Coscine API token must be a member
        of the other project.
        """
        uri = self.client.uri("projects", self.id, "members")
        self.client.post(uri, json={"roleId": role.id, "userId": user.id})

    def remove_member(self, member: ProjectMember) -> None:
        """
        Removes the member from the project. Does not invalidate the member
        object in Python - it is up to the API user to not use that variable
        again.
        """
        uri = self.client.uri("projects", self.id, "members", member.id)
        self.client.delete(uri)

    def invite(self, email: str, role: ProjectRole) -> None:
        """
        Invites an external user via their email address to
        the Coscine project.
        """
        uri = self.client.uri("projects", self.id, "invitations")
        self.client.post(uri, json={"roleId": role.id, "email": email})

    def quotas(self) -> list[ProjectQuota]:
        """
        Returns the project storage quotas.
        """
        uri = self.client.uri("projects", self.id, "quotas")
        response = self.client.get(uri)
        return [ProjectQuota(item) for item in response.data]

    def members(self) -> list[ProjectMember]:
        """
        Returns the list of all members of the current project.
        """
        uri = self.client.uri("projects", self.id, "members")
        return [
            ProjectMember(self, item)
            for page in self.client.get(uri).pages()
            for item in page.data
        ]

    def invitations(self) -> list[ProjectInvitation]:
        """
        Returns the list of all outstanding project invitations.
        """
        uri = self.client.uri("projects", self.id, "invitations")
        return [
            ProjectInvitation(item)
            for page in self.client.get(uri).pages()
            for item in page.data
        ]

    def update(self) -> None:
        """
        Updates a Coscine project's settings.
        To update certain properties just access the properties
        of the coscine.Project class directly and call Project.update()
        when done.
        """
        uri = self.client.uri("projects", self.id)
        self.client.put(uri, json=self.serialize())

    def subprojects(self) -> list[Project]:
        """ """
        if not "subProjects" in self._data:
            project = self.client.project(self.id, Project.id)
            self._data = project._data
        return [
            Project(self.client, data) for data in self._data.get("subProjects", [])
        ]

    def subproject(self, key: str, attribute: property = display_name) -> Project:
        """
        Returns a single Coscine Project via one of its properties.

        Parameters
        ----------
        key
            The value of the property to filter by.
        property
            The property/attribute of the project to filter by.
        toplevel
            If set to True, only toplevel projects are searched.
            Set it to False to include all (sub-)projects in the search.

        Raises
        ------
        coscine.exceptions.TooManyResults
            In case more than 1 project was found via the selected property.
        coscine.exceptions.NotFoundError
            In case the project could not be found via the selected property.
        """
        if attribute == Project.id:
            return self.client._fetch_project_via_id(key)
        results = list(
            filter(lambda project: project.match(attribute, key), self.subprojects())
        )
        if len(results) > 1:
            raise TooManyResults(
                "Found more than 1 project with a property matching "
                f"the key '{key}'. "
                "Certain project properties such as the name "
                "allow for duplicates among other projects. "
                "Use a different (unique) property to filter by!"
            )
        if len(results) == 0:
            raise NotFoundError(
                f"Failed to find a project via the key '{key}'! "
                "Maybe you are looking for a subproject and have "
                "set the toplevel argument to False? Also check whether "
                "you are filtering by the correct property."
            )
        # Required for access to subproject list
        return self.client._fetch_project_via_id(results[0].id)

    def create_subproject(
        self,
        name: str,
        display_name: str,
        description: str,
        start_date: date,
        end_date: date,
        principal_investigators: str,
        visibility: Visibility,
        disciplines: list[Discipline],
        responsible_organization: Organization,
        additional_organizations: list[Organization] | None = None,
        keywords: list[str] | None = None,
        grant_id: str = "",
    ) -> Project:
        """
        Creates a new Coscine project.

        Parameters
        ----------
        name
            The project's name.
        display_name
            The project's display name (how it appears in the web interface).
        description
            The project description.
        start_date
            Date when the project starts.
        end_date
            Date when the project ends.
        principal_investigators
            The project PIs.
        visibility
            Project metadata visibility (relevant for search).
        disciplines
            List of associated scientific disciplines.
        responsible_organization
            The lead organization.
        additional_organizations
            List of organizations partaking in the project. The responsible
            organization may not re-appear here.
        keywords
            List of project keywords (relevant for search).
        grant_id
            The projects grant ID.
        parent_id
            Parent project ID if the project should be a subproject.
        """
        return self.client.create_project(
            name,
            display_name,
            description,
            start_date,
            end_date,
            principal_investigators,
            visibility,
            disciplines,
            responsible_organization,
            additional_organizations,
            keywords,
            grant_id,
            self.id,
        )

    def create_resource(
        self,
        name: str,
        display_name: str,
        description: str,
        license: License,
        visibility: Visibility,
        disciplines: list[Discipline],
        resource_type: ResourceType,
        quota: int,
        application_profile: ApplicationProfileInfo,
        usage_rights: str = "",
        keywords: list[str] | None = None,
    ) -> Resource:
        """
        Creates a new Coscine resource within the project.

        Parameters
        ----------
        name
            The full name of the resource.
        display_name
            The shortened display name of the resource.
        description
            The description of the resource.
        license
            License for the resource contents.
        visibility
            Resource metadata visibility (relevant for search).
        disciplines
            Associated/Involved scientific disciplines.
        resource_type
            The Cosciner resource type.
        quota
            Resource quota in GB (irrelevant for linked data resources).
        application_profile
            The metadata application profile for the resource.
        notes
            Data usage notes
        keywords
            Keywords (relevant for search).

        """
        rds_options = {
            "quota": {"value": quota, "unit": "https://qudt.org/vocab/unit/GibiBYTE"}
        }
        options = {
            "linked": {"linkedResourceTypeOptions": {}},
            "gitlab": {
                "gitlabResourceTypeOptions": {},  # currently unsupported
            },
            "rds": {"rdsResourceTypeOptions": rds_options},
            "rdss3": {"rdsS3ResourceTypeOptions": rds_options},
            "rdss3worm": {"rdsS3WormResourceTypeOptions": rds_options},
            "dsnrwweb": {"dataStorageNrwWebResourceTypeOptions": rds_options},
            "dsnrws3worm": {"dataStorageNrwS3WormResourceTypeOptions": rds_options},
            "dsnrws3": {"dataStorageNrwS3ResourceTypeOptions": rds_options},
        }
        data: dict = {
            "name": name,
            "displayName": display_name,
            "description": description,
            "keywords": keywords if keywords else [],
            "license": license.serialize(),
            "visibility": visibility.serialize(),
            "disciplines": [discipline.serialize() for discipline in disciplines],
            "resourceTypeId": resource_type.id,
            "resourceTypeOptions": options[resource_type.general_type],
            "applicationProfile": {"uri": application_profile.uri},
            "usageRights": usage_rights,
        }
        uri = self.client.uri("projects", self.id, "resources")
        return Resource(self, self.client.post(uri, json=data).data)

    def update_quota(
        self, resource_type: ResourceType, allocated: int, maximum: int
    ) -> None:
        """
        Updates the quota settings of a project.
        This might require Admin privileges (not Owner) when
        influencing the maximum value. The allocated value
        should be modifiable by project owners.
        """
        uri = self.client.uri("projects", self.id, "quotas", resource_type.id)
        self.client.put(
            uri,
            json={
                "allocated": {
                    "value": allocated,
                    "unit": "https://qudt.org/vocab/unit/GibiBYTE",
                },
                "maximum": {
                    "value": maximum,
                    "unit": "https://qudt.org/vocab/unit/GibiBYTE",
                },
            },
        )
