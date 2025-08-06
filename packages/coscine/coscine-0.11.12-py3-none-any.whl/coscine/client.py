###############################################################################
# Coscine Python SDK
# Copyright (c) 2020-2025 RWTH Aachen University
# Licensed under the terms of the MIT License
# For more information on Coscine visit https://www.coscine.de/.
###############################################################################

"""
Provides the Coscine ApiClient.
"""

from __future__ import annotations
from typing import Iterator
from os import getenv, environ
import logging
from datetime import date, timedelta
import requests
import requests_cache
from requests.compat import quote as urlquote
from requests.utils import get_encoding_from_headers
from requests.adapters import HTTPAdapter
import urllib3
from urllib3.util import Retry
from coscine.__about__ import __version__
from coscine.exceptions import (
    AuthenticationError,
    CoscineException,
    NotFoundError,
    RequestRejected,
    TooManyResults,
)
from coscine.common import (
    ApiToken,
    Discipline,
    Language,
    License,
    MaintenanceNotice,
    Organization,
    SearchResult,
    User,
    Visibility,
)
from coscine.metadata import (
    ApplicationProfile,
    ApplicationProfileInfo,
    Instance,
    Vocabulary,
)
from coscine.project import Project, ProjectRole
from coscine.resource import ResourceType


logger = logging.getLogger(__name__)


class ApiResponse:
    """
    Models the response data object sent by the Coscine REST API upon
    a successful request.
    """

    response: requests.Response

    @property
    def data(self) -> dict:
        """
        The response data as a dict if it arrived in JSON format.
        """
        data = self.json
        return data["data"] if "data" in data else {}

    @property
    def json(self) -> dict:
        """
        The full response data as a dict if it arrived in JSON format.
        Includes response metadata.
        """
        try:
            return self.response.json()
        except requests.exceptions.JSONDecodeError:
            return {}

    @property
    def status_code(self) -> int:
        """
        The status code of the response as set by Coscine.
        """
        return self.json.get("statusCode") or 0

    @property
    def trace_id(self) -> str:
        """
        The Trace ID for Coscine internal error handling.
        """
        return self.json.get("traceId") or ""

    @property
    def is_paginated(self) -> bool:
        """
        Evaluates to True if the response is paginated, i.e. divided onto
        multiple pages.
        """
        return "pagination" in self.json

    @property
    def current_page(self) -> int:
        """
        The page number of the current page.
        """
        if self.is_paginated:
            return self.json["pagination"].get("currentPage") or 0
        raise AttributeError("The response is not paginated!")

    @property
    def total_pages(self) -> int:
        """
        The total number of pages for the specified PageSize.
        The PageSize is by default set to the maximum of 50.
        """
        if self.is_paginated:
            return self.json["pagination"].get("totalPages") or 0
        raise AttributeError("The response is not paginated!")

    @property
    def page_size(self) -> int:
        """
        The page size of the current response data.
        """
        if self.is_paginated:
            return self.json["pagination"].get("pageSize") or 0
        raise AttributeError("The response is not paginated!")

    @property
    def total_data_count(self) -> int:
        """
        The total amount of data items available.
        """
        if self.is_paginated:
            return self.json["pagination"].get("totalCount") or 0
        raise AttributeError("The response is not paginated!")

    @property
    def has_next(self) -> bool:
        """
        Evaluates to True if there are more pages available.
        """
        if self.is_paginated:
            return self.json["pagination"].get("hasNext") or False
        raise AttributeError("The response is not paginated!")

    @property
    def has_previous(self) -> bool:
        """
        Evaluates to True if there is at least one preceding page available.
        """
        if self.is_paginated:
            return self.json["pagination"].get("hasPrevious") or False
        raise AttributeError("The response is not paginated!")

    def pages(self) -> Iterator[ApiResponse]:
        """
        Returns all pages of the response. This may result in additional
        requests.
        """
        yield self
        if self.is_paginated:
            response = self
            request = self.request
            page = 1
            while response.has_next and page < self.client.max_pages:
                page += 1
                request.params["PageNumber"] = page
                response = self.client.send_request(request)
                yield response

    def __init__(
        self, client: ApiClient, request: requests.Request, response: requests.Response
    ) -> None:
        self.client = client
        self.request = request
        self.response = response


class ApiClient:
    """
    The ApiClient communicates with Coscine by sending requests to and
    receiving response data from Coscine.

    Parameters
    -----------
    token : str
        To be able to use the Coscine REST API one has to supply their
        Coscine API token. Every Coscine user can create their own set
        of API tokens for free in their Coscine user profile.
        For security reasons Coscine API Tokens are only valid for
        a certain amount of time after which they are deactivated.
    language : str
        Just like in the web interface of Coscine one can select
        a language preset for the Coscine API. This will localize
        all multi-language vocabularies and application profiles to the
        selected language. The language can later be switched on the fly.
    base_url : str
        Coscine is Open Source software and hosted on various domains.
        Via the base_url setting, the API user can specify which instance
        they would like to connect to. By default this is set to
        the Coscine instance of RWTH Aachen.
    verify_certificate : bool
        Whether to verify the SSL server certificate of the Coscine server.
        By default this is enabled as it provides some form of protection
        against spoofing, but on test instances or "fresh" installs
        certificates are often not used. To be able to use
        the Coscine Python SDK with such instances, the verify setting
        should be turned off.
    verbose : bool
        By disabling the verbose setting one can stop the Python SDK
        from printing to the command line interface (stdout). The stderr
        file handle is unaffected by this. This setting is particulary
        helpful in case you wish to disable the banner on initialization.
    enable_caching : bool
        Enabling caching allows the Python SDK to store some of
        the responses it gets from Coscine in a RequestCache. This cache
        is always active at runtime but may be saved and loaded to a file
        by enabling the caching setting. Entries in the cachefiles
        are valid for a certain amount of time until they are refreshed.
        With caching enabled the Python SDK is much faster.
    timeout : float (seconds)
        The timeout threshold for Coscine to respond to a request.
        If Coscine does not answer within the specified amount of
        seconds, an exception is raised. Note that setting a timeout
        is very important since otherwise your application may hang
        indefinitely if it never gets a response.
    use_native
        If enabled, up- and downloads are performed via the native providers.
        In the case of an s3 resource that equates to using boto3 behind
        the scenes. If set to False, the route via Coscine is taken, which
        is usually about 30% slower, less stable and has size and bandwidth
        limitations.
    """

    BANNER: str = (
        r"                      _              "
        "\n"
        r"                     (_)             "
        "\n"
        r"    ___ ___  ___  ___ _ _ __   ___   "
        "\n"
        r"   / __/ _ \/ __|/ __| | '_ \ / _ \  "
        "\n"
        r"  | (_| (_) \__ \ (__| | | | |  __/  "
        "\n"
        r"   \___\___/|___/\___|_|_| |_|\___|  "
        "\n"
        r" ___________________________________ "
        "\n"
        f"  Coscine Python SDK {__version__}   "
        "\n"
        r"  https://coscine.de/                "
        "\n"
    )

    base_url: str
    session: requests_cache.CachedSession
    verbose: bool
    verify: bool
    timeout: float

    _language: str

    @property
    def language(self) -> str:
        """
        The language setting of the ApiClient.
        This may be set to "en" for english or "de" for german.
        By default it is set to english but it can be changed
        on the fly even after the ApiClient has been instantiated.
        """
        return self._language

    @language.setter
    def language(self, value: str) -> None:
        language = value.lower()
        if language not in ("de", "en"):
            raise ValueError(
                f"Invalid language value: {value}! "
                "Acceptable values are: 'de' or 'en'."
            )
        self._language = language

    @property
    def version(self) -> str:
        """
        Coscine Python SDK version string. For example: "1.0.0"
        """
        return __version__

    def __init__(
        self,
        token: str,
        language: str = "en",
        base_url: str = "https://coscine.rwth-aachen.de",
        enable_caching: bool = True,
        verbose: bool = True,
        verify_certificate: bool = True,
        timeout: float = 60.0,
        retries: int = 3,
        use_native: bool = True,
        max_pages: int = 65535,
    ) -> None:
        self.base_url = base_url
        self.language = language
        self.timeout = timeout
        self.session = requests_cache.CachedSession(
            cache_name="coscine",
            allowable_methods=["GET"],
            backend="filesystem",
            serializer="json",
            use_cache_dir=True,
            urls_expire_after={
                "*/api/v2/application-profiles/profiles*": timedelta(days=30),
                "*/api/v2/disciplines*": timedelta(days=30),
                "*/api/v2/languages*": timedelta(days=30),
                "*/api/v2/licenses*": timedelta(days=30),
                "*/api/v2/organizations*": timedelta(days=30),
                "*/api/v2/resource-types/types*": timedelta(days=30),
                "*/api/v2/roles*": timedelta(days=30),
                "*/api/v2/titles*": timedelta(days=30),
                "*/api/v2/visibilities*": timedelta(days=30),
                "*/api/v2/vocabularies*": timedelta(days=30),
                "*": requests_cache.DO_NOT_CACHE,
            },
        )
        self.enable_caching(enable_caching)
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "User-Agent": f"Coscine Python SDK {self.version}",
            }
        )
        retrycfg = Retry(
            total=retries,
            backoff_factor=1.0,
            status_forcelist=[502, 503, 504],
            allowed_methods={"GET"},
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retrycfg))
        self.verbose = verbose
        self.verify = verify_certificate
        self.native = use_native
        self.max_pages = max_pages
        if use_native and not getenv("AWS_REQUEST_CHECKSUM_CALCULATION"):
            environ["AWS_REQUEST_CHECKSUM_CALCULATION"] = "WHEN_REQUIRED"
        if not verify_certificate:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        if self.verbose:
            print(ApiClient.BANNER)
        try:
            self.self()
        except CoscineException:
            raise AuthenticationError("Invalid Coscine REST API Token!")

    def enable_caching(self, enable: bool) -> None:
        """
        Enables or disables request caching on demand.
        """
        self.session.settings.disabled = not enable

    def latest_version(self) -> str:
        """
        Retrieves the version string of the latest version of this
        package hosted on PyPi. Useful for checking whether the currently
        used version is outdated and if an update should be performed.

        Examples
        --------
        >>> if client.version != client.latest_version():
        >>>     print("Module outdated.")
        >>>     print("Run 'py -m pip install --upgrade coscine'.")
        """
        uri = "https://pypi.org/pypi/coscine/json"
        data = requests.get(uri, timeout=60.0).json()
        version = data["info"]["version"]
        return version

    def uri(self, *args) -> str:
        """
        Constructs a URI for requests to the Coscine REST API.
        This method creates URLs relative to the ApiClient.base_url
        and escapes URL arguments for compliance with the HTTP.

        Parameters
        -----------
        *args
            Any number of arguments that should be included in the URI.
            The arguments do not have to be of type string, but should
            be str() serializable.

        Examples
        --------
        >>> ApiClient.uri("application-profiles", "profiles", profile_uri)
        """
        suffix = "/".join((urlquote(str(arg), safe="") for arg in args))
        return f"{self.base_url}/coscine/api/v2/{suffix}"

    def send_request(
        self, request: requests.Request, stream: bool = False
    ) -> ApiResponse:
        """
        Sends a requests request to Coscine.

        Parameters
        ----------
        request
            The request that previously has been created
            with requests.Request().
        stream
            If set to True, the data transfer will be streamed,
            i.e. performed in chunks.
        """
        try:
            prepared_request = self.session.prepare_request(request)
            if prepared_request.body:
                encoding = get_encoding_from_headers(request.headers)
                if encoding:
                    assert isinstance(prepared_request.body, bytes)
                    body = prepared_request.body.decode(encoding)
                else:
                    body = "<binary data>"
                logger.debug(body)
            response = self.session.send(
                prepared_request,
                stream=stream,
                verify=self.verify,
                timeout=self.timeout,
            )
            encoding = get_encoding_from_headers(response.headers)
            if encoding:
                logger.debug(response.content.decode("utf-8"))
            response.raise_for_status()
            return ApiResponse(self, request, response)
        except requests.exceptions.RequestException as error:
            self.handle_request_exception(error)
            raise error

    def request(
        self, method: str, *args, stream: bool = False, **kwargs
    ) -> ApiResponse:
        """
        Sends a request to the Coscine REST API. This method is used
        internally. As a user of the ApiClient you should use the methods
        ApiClient.get(), ApiClient.post(), ApiClient.put(),
        ApiClient.delete(), ApiClient.options()
        instead of directly calling ApiClient.request().

        Parameters
        ----------
        method
            The HTTP method to use for the request:
            GET, PUT, POST, DELETE, OPTIONS, etc.
        *args
            Any number of arguments to forward to the requests.Request()
        stream
            If set to true, the response will be streamed. This means that
            the response will be split up and arrive in multiple chunks.
            When attempting to download files, the stream parameter must be
            set to True. Otherwise it should be left at False.
        *kwargs
            Any number of keyword arguments to forward to requests.Request()

        Raises
        ------
        See coscine.ApiClient.handle_request_exception
        """
        request = requests.Request(method, *args, **kwargs)
        return self.send_request(request, stream)

    @staticmethod
    def handle_request_exception(exception: Exception) -> None:
        """
        Raises
        ------
        ConnectionError
            If the request never reaches Coscine or we never get a response.
        coscine.exceptions.AuthenticationError
            If the Coscine API token is not valid.
        coscine.exceptions.RequestRejected
            If the request reached Coscine but was subsequently rejected
            by the Server.
        """
        if isinstance(exception, requests.exceptions.ConnectionError):
            raise ConnectionError(
                "Failed to connect to Coscine! Check your internet "
                "connection or whether Coscine is currently down."
            ) from exception
        if isinstance(exception, requests.exceptions.Timeout):
            raise ConnectionError(
                "The connection timed out. This may either be "
                "a ConnectionError or Coscine took a lot of time "
                "processing the request. You can increase the timeout "
                "threshold of the SDK in the client settings."
            ) from exception
        if isinstance(exception, requests.exceptions.RequestException):
            assert hasattr(exception, "response")
            assert isinstance(exception.response, requests.Response)
            if exception.response.status_code == 401:
                raise AuthenticationError(
                    "Invalid Coscine API token! The token was rejected "
                    "by Coscine. Check whether it is expired."
                ) from exception
            raise RequestRejected(
                "Coscine rejected the request sent by the Coscine Python SDK "
                "with the following error message: "
                f"{exception.response.content.decode('utf-8')}."
            ) from exception

    def get(self, *args, **kwargs) -> ApiResponse:
        """
        Sends a GET request to the Coscine REST API.
        For a list of exceptions that are raised by this method
        or a detailed list of parameters, refer to ApiClient.request().

        Parameters
        ----------
        Refer to ApiClient.request() for a list of parameters.

        Raises
        -------
        Refer to ApiClient.request() for a list of exceptions.

        Returns
        --------
        dict
            The "data": { ... } section of the JSON-response.
        """
        if "params" not in kwargs:
            kwargs["params"] = {}
        kwargs["params"]["PageSize"] = 50
        return self.request("GET", *args, **kwargs)

    def put(self, *args, **kwargs) -> ApiResponse:
        """
        Sends a PUT request to the Coscine REST API.

        Parameters
        ----------
        Refer to ApiClient.request() for a list of parameters.

        Raises
        -------
        Refer to ApiClient.request() for a list of exceptions.
        """
        return self.request("PUT", *args, **kwargs)

    def post(self, *args, **kwargs) -> ApiResponse:
        """
        Sends a POST request to the Coscine REST API.

        Parameters
        ----------
        Refer to ApiClient.request() for a list of parameters.

        Raises
        -------
        Refer to ApiClient.request() for a list of exceptions.
        """
        return self.request("POST", *args, **kwargs)

    def delete(self, *args, **kwargs) -> ApiResponse:
        """
        Sends a DELETE request to the Coscine REST API.

        Parameters
        ----------
        Refer to ApiClient.request() for a list of parameters.

        Raises
        -------
        Refer to ApiClient.request() for a list of exceptions.
        """
        return self.request("DELETE", *args, **kwargs)

    def options(self, *args, **kwargs) -> ApiResponse:
        """
        Sends an OPTIONS request to the Coscine REST API.

        Parameters
        ----------
        Refer to ApiClient.request() for a list of parameters.

        Raises
        -------
        Refer to ApiClient.request() for a list of exceptions.
        """
        return self.request("OPTIONS", *args, **kwargs)

    def projects(self, toplevel: bool = True) -> list[Project]:
        """
        Retrieves a list of all Coscine projects that the creator of
        the Coscine API token is currently a member of.

        Parameters
        -----------
        toplevel
            If set to True, only toplevel projects are retrieved.
            Set it to False to include all (sub-)projects in the results.
        """
        uri = self.uri("projects")
        response = self.get(uri, params={"TopLevel": toplevel})
        return [Project(self, item) for page in response.pages() for item in page.data]

    def _fetch_project_via_id(self, id: str) -> Project:
        uri = self.uri("projects", id)
        response = self.get(uri, params={"IncludeSubProjects": True})
        return Project(self, response.data)

    def project(
        self,
        key: str,
        attribute: property = Project.display_name,
        toplevel: bool = True,
    ) -> Project:
        """
        Returns a single Coscine Project via one of its properties.

        Parameters
        ----------
        key
            The value of the property to filter by.
        property
            The property/attribute of the project to filter by. Defaults to the shortend, 25 character display name of the project.
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
            return self._fetch_project_via_id(key)
        results = list(
            filter(
                lambda project: project.match(attribute, key), self.projects(toplevel)
            )
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
        return self._fetch_project_via_id(results[0].id)

    def create_project(
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
        parent_id: str = "",
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
        # Responsible organization and additional organizations are given
        # as a single list, with the differentiating aspect of an additional
        # responsible = True field for the responsible organization.
        organizations = []
        organizations.append(responsible_organization.serialize())
        organizations[0]["responsible"] = True
        if additional_organizations is None:
            additional_organizations = []
        for org in additional_organizations:
            data = org.serialize()
            data["responsible"] = False
            organizations.append(data)
        data: dict = {
            "name": name,
            "displayName": display_name,
            "description": description,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "principleInvestigators": principal_investigators,
            "disciplines": [discipline.serialize() for discipline in disciplines],
            "organizations": organizations,
            "visibility": visibility.serialize(),
            "keywords": keywords if keywords else [],
            "grantId": grant_id,
        }
        if parent_id:
            data["parentId"] = parent_id
        uri = self.uri("projects")
        return Project(self, self.post(uri, json=data).data)

    def search(self, query: str, category: str | None = None) -> list[SearchResult]:
        """
        Sends a search request to Coscine and returns the results.

        Parameters
        -----------
        query
            The search query
        category
            The search can optionally be restricted to one of these
            categories: "metadata", "project" or "resource"
        """
        uri = self.uri("search")
        parameters = {"Query": query, "category": category}
        response = self.get(uri, params=parameters)
        return [SearchResult(item) for item in response.data]

    def maintenances(self) -> list[MaintenanceNotice]:
        """
        Retrieves the list of current active maintenance notices for Coscine.
        """
        uri = self.uri("maintenances")
        response = self.get(uri)
        return [MaintenanceNotice(item) for item in response.data]

    def visibilities(self) -> list[Visibility]:
        """
        Retrieves the list of visibility options available in Coscine.
        """
        uri = self.uri("visibilities")
        response = self.get(uri)
        return [Visibility(item) for item in response.data]

    def visibility(self, name: str) -> Visibility:
        """
        Returns the visibility that matches the name.
        Valid names are:
        * "Project Members"
        * "Public"
        """
        results = list(
            filter(lambda visibility: visibility.name == name, self.visibilities())
        )
        if len(results) > 1:
            raise TooManyResults(
                f"Found more than 1 visibility with the name '{name}'!"
            )
        if len(results) == 0:
            raise NotFoundError(f"Failed to find a visibility with the name '{name}'!")
        return results[0]

    def disciplines(self) -> list[Discipline]:
        """
        Retrieves the list of scientific disciplines available in Coscine.
        """
        uri = self.uri("disciplines")
        response = self.get(uri)
        return [Discipline(item) for page in response.pages() for item in page.data]

    def discipline(self, name: str) -> Discipline:
        """
        Returns the discipline that matches the name.
        Valid names are:
        * "Ancient Cultures 101"
        * "History 102"
        * "Fine Arts, Music, Theatre and Media Studies (103)"
        * "Linguistics 104"
        * "Library Studies 105"
        * "Social and Cultural Anthropology, Non-European Cultures, Jewish Studies and Religious Studies 106"
        * "Theology 107"
        * "Philosophy 108"
        * "Educational Research 109"
        * "Psychology 110"
        * "Social Sciences 111"
        * "Economics 112"
        * "Jurisprudence 113"
        * "Basic Biological and Medical Research 201"
        * "Plant Sciences 202"
        * "Zoology 203"
        * "Microbiology, Virology and Immunology 204"
        * "Medicine 205"
        * "Neurosciences 206"
        * "Agriculture, Forestry and Veterinary Medicine 207"
        * "Molecular Chemistry 301"
        * "Chemical Solid State and Surface Research 302"
        * "Physical and Theoretical Chemistry 303"
        * "Analytical Chemistry, Method Development (Chemistry) 304"
        * "Biological Chemistry and Food Chemistry 305"
        * "Polymer Research 306"
        * "Condensed Matter Physics 307"
        * "Optics, Quantum Optics and Physics of Atoms, Molecules and Plasmas 308"
        * "Particles, Nuclei and Fields 309"
        * "Statistical Physics, Soft Matter, Biological Physics, Nonlinear Dynamics 310"
        * "Astrophysics and Astronomy 311"
        * "Mathematics 312"
        * "Atmospheric Science, Oceanography and Climate Research 313"
        * "Geology and Palaeontology 314"
        * "Geophysics and Geodesy 315"
        * "Geochemistry, Mineralogy and Crystallography 316"
        * "Geography 317"
        * "Water Research 318"
        * "Production Technology 401"
        * "Mechanics and Constructive Mechanical Engineering 402"
        * "Process Engineering, Technical Chemistry 403"
        * "Heat Energy Technology, Thermal Machines, Fluid Mechanics 404"
        * "Materials Engineering 405"
        * "Materials Science 406"
        * "Systems Engineering 407"
        * "Electrical Engineering and Information Technology 408"
        * "Computer Science 409"
        * "Construction Engineering and Architecture 410"
        I had to copy these manually from a DFG PDF!
        The absolute state of digitization in germany...
        Expect some typos!
        """
        results = list(
            filter(lambda discipline: discipline.name == name, self.disciplines())
        )
        if len(results) > 1:
            raise TooManyResults(
                f"Found more than 1 discipline with the name '{name}'!"
            )
        if len(results) == 0:
            raise NotFoundError(f"Failed to find a discipline with the name '{name}'!")
        return results[0]

    def api_tokens(self) -> list[ApiToken]:
        """
        Retrieves the list of Coscine API tokens that have been created
        by the owner of the same API token that was used to initialize
        the Coscine Python SDK ApiClient.
        """
        uri = self.uri("self", "api-tokens")
        return [ApiToken(item) for page in self.get(uri).pages() for item in page.data]

    def self(self) -> User:
        """
        Returns the owner of the Coscine API token that was used to
        initialize the ApiClient.
        """
        return User(self.get(self.uri("self")).data)

    def users(self, query: str) -> list[User]:
        """
        Searches for users.
        """
        response = self.get(self.uri("users"), params={"SearchTerm": query})
        return [User(item) for page in response.pages() for item in page.data]

    def application_profile(self, profile_uri: str) -> ApplicationProfile:
        """
        Retrieves a specific application profile via its uri.

        Parameters
        ----------
        profile_uri
            The uri of the application profile,
            e.g. https://purl.org/coscine/ap/base/
            The trailing slash is important!
        """
        # Since we are parsing the ApplicationProfile right away as ttl
        # there is not point in fetching it in any other format or letting
        # the user decide the format.
        uri = self.uri("application-profiles", "profiles", profile_uri)
        response = self.get(uri, params={"format": "text/turtle"})
        return ApplicationProfile(self, response.data)

    def application_profiles(self) -> list[ApplicationProfileInfo]:
        """
        Retrieves the list of all application profiles that are currently
        available in Coscine.
        """
        uri = self.uri("application-profiles", "profiles")
        return [
            ApplicationProfileInfo(item)
            for page in self.get(uri).pages()
            for item in page.data
        ]

    def vocabulary(self, class_uri: str) -> Vocabulary:
        """
        Retrieves the vocabulary for the class.

        Parameters
        ----------
        class_uri
            The instance class uri, e.g. http://purl.org/dc/dcmitype
        """
        uri = self.uri("vocabularies", "instances")
        params = {"Class": class_uri, "Language": self.language}
        instances = [
            Instance(item)
            for page in self.get(uri, params=params).pages()
            for item in page.data
        ]
        return Vocabulary(instances)

    def languages(self) -> list[Language]:
        """
        Retrieves all language options available in Coscine.
        """
        uri = self.uri("languages")
        return [Language(item) for page in self.get(uri).pages() for item in page.data]

    def organization(self, ror_uri: str) -> Organization:
        """
        Looks up an organization based on its ror uri.
        Some commonly used ROR uris:
        * "https://ror.org/04xfq0f34" <- RWTH Aachen
        * "https://ror.org/04tqgg260" <- FH Aachen
        * "https://ror.org/04t3en479" <- KIT
        * "https://ror.org/02kkvpp62" <- TUM
        * "https://ror.org/05n911h24" <- TU Darm
        * "https://ror.org/01k97gp34" <- TU Do
        * "https://ror.org/02gm5zw39" <- UKA
        * "https://ror.org/00rcxh774" <- Uni Köln
        * "https://ror.org/04mz5ra38" <- Uni Due
        * "https://ror.org/00pd74e08" <- Uni Mün
        """
        uri = self.uri("organizations", ror_uri)
        return Organization(self.get(uri).data)

    def licenses(self) -> list[License]:
        """
        Retrieves a list of all licenses available in Coscine.
        """
        uri = self.uri("licenses")
        return [License(item) for page in self.get(uri).pages() for item in page.data]

    def license(self, name: str) -> License:
        """
        Returns the license that matches the name.
        * "Apache License 2.0"
        * "BSD 2-clause 'Simplified' License"
        * "BSD 3-clause 'New' or 'Revised' License"
        * "CC BY 4.0 (Attribution)"
        * "CC BY NC 4.0 (Attribution-NonCommercial)"
        * "CC BY NC ND 4.0 (Attribution-NonCommercial-NoDerivatives)"
        * "CC BY NC SA 4.0 (Attribution-NonCommercial-ShareAlike)"
        * "CC BY ND 4.0 (Attribution-NoDerivatives)"
        * "CC BY SA 4.0 (Attribution-ShareAlike)"
        * "Eclipse Public License 1.0"
        * "GNU Affero General Public License v3.0"
        * "GNU General Public License v2.0"
        * "GNU General Public License v3.0"
        * "GNU Lesser General Public License v2.1"
        * "GNU Lesser General Public License v3.0"
        * "MIT License"
        * "Mozilla Public License 2.0"
        * "The Unlicense"
        """
        results = list(filter(lambda license: license.name == name, self.licenses()))
        if len(results) > 1:
            raise TooManyResults(f"Found more than 1 licenses with the name '{name}'!")
        if len(results) == 0:
            raise NotFoundError(f"Failed to find a license with the name '{name}'!")
        return results[0]

    def roles(self) -> list[ProjectRole]:
        """
        Returns all roles that are available in Coscine,
        e.g. "Member", "Owner", ...
        """
        response = self.get(self.uri("roles"))
        return [ProjectRole(item) for item in response.data]

    def role(self, name: str) -> ProjectRole:
        """
        Returns the role that matches the name.
        """
        results = list(filter(lambda role: role.name == name, self.roles()))
        if len(results) > 1:
            raise TooManyResults(f"Found more than 1 role with the name '{name}'!")
        if len(results) == 0:
            raise NotFoundError(f"Failed to find a role with the name '{name}'!")
        return results[0]

    def resource_types(self) -> list[ResourceType]:
        """
        Retrieves a list of all resource types available in Coscine.
        """
        uri = self.uri("resource-types", "types")
        return [
            ResourceType(item) for page in self.get(uri).pages() for item in page.data
        ]

    def resource_type(self, name: str) -> ResourceType:
        """
        Returns the ResourceType that matches the name.
        Here name refers to the resource specificType,
        e.g. "rdsrwth" instead of the general type "rds".
        Mapping between specificType -> generalType:
        * "rdss3rwth" -> "rdss3"
        * "linked" -> "linked"
        * "rdss3wormrwth" -> "rdss3worm"
        * "rdsrwth" -> "rds"
        * "rdstudo" -> "rds"
        * "gitlab" -> "gitlab"
        * "rdss3nrw" -> "rdss3"
        * "rdss3ude" -> "rdss3"
        * "rdsude" -> "rds"
        * "rdss3tudo" -> "rdss3"
        * "rdsnrw" -> "rds"
        * "dsnrwweb" -> "dsnrwweb"
        * "dsNrwS3"-> "dsNrwS3"
        * "dsnrws3worm"-> "dsnrws3worm"
        """
        results = list(
            filter(lambda rtype: rtype.specific_type == name, self.resource_types())
        )
        if len(results) > 1:
            raise TooManyResults(
                f"Found more than 1 resource types with the name '{name}'!"
            )
        if len(results) == 0:
            raise NotFoundError(
                f"Failed to find a resource type with the name '{name}'!"
            )
        return results[0]

    def validate_pid(self, pid: str) -> bool:
        """
        Checks the given PID for validity.
        """
        try:
            if pid.startswith("http://hdl.handle.net/"):
                pid = pid.partition("http://hdl.handle.net/")[2]
            prefix, postfix = pid.split("/")
            uri = self.uri("pids", prefix, postfix)
            return self.get(uri).data.get("isValid") or False
        except (CoscineException, ValueError):
            return False
