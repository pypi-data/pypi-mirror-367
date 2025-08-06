###############################################################################
# Coscine Python SDK
# Copyright (c) 2020-2025 RWTH Aachen University
# Licensed under the terms of the MIT License
# For more information on Coscine visit https://www.coscine.de/.
###############################################################################

"""
Provides an interface around resources in Coscine.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Callable, BinaryIO
from datetime import date, datetime
from pathlib import Path
from io import BytesIO, IOBase
from os import mkdir
from os.path import basename, isdir, splitext
from posixpath import join as join_paths
import logging
from textwrap import wrap
from urllib.parse import urlparse, parse_qs
from isodate import parse_datetime
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from tabulate import tabulate
from tqdm import tqdm
import boto3
import rdflib
from coscine.common import Discipline, License, Visibility
from coscine.metadata import ApplicationProfile, MetadataForm, FileMetadata
from coscine.exceptions import NotFoundError, RequestRejected

if TYPE_CHECKING:
    from coscine.client import ApiClient
    from coscine.project import Project


logger = logging.getLogger(__name__)


class ResourceQuota:
    """
    Models the Coscine resource quota data.
    """

    _data: dict

    @property
    def resource_id(self) -> str:
        """
        The associated Coscine resource id.
        """
        return self._data["resource"].get("id") or ""

    @property
    def used_percentage(self) -> float:
        """
        The ratio of used up quota in relation to the available quota.
        """
        value = self._data.get("usedPercentage") or 0.00
        return float(value)

    @property
    def used(self) -> int:
        """
        The used quota in bytes.
        """
        return int(self._data["used"]["value"])

    @property
    def reserved(self) -> int:
        """
        The reserved quota for the resource.
        """
        return int(self._data["reserved"]["value"] * 1024**3)

    def __init__(self, data: dict) -> None:
        self._data = data

    def serialize(self) -> dict:
        return self._data


class ResourceTypeOptions:
    """
    Options and settings regarding the resource type.
    Mainly provides an interface to resource type specific attributes
    such as S3 access credentials for resources of type rds-s3.
    """

    _data: dict

    @property
    def bucket_name(self) -> str:
        """
        The S3 bucket name.
        """
        return self._data.get("bucketName") or ""

    @property
    def access_key_read(self) -> str:
        """
        The S3 access key for reading.
        """
        return self._data.get("accessKeyRead") or ""

    @property
    def secret_key_read(self) -> str:
        """
        The S3 secret key for reading.
        """
        return self._data.get("secretKeyRead") or ""

    @property
    def access_key_write(self) -> str:
        """
        The S3 access key for writing.
        """
        return self._data.get("accessKeyWrite") or ""

    @property
    def secret_key_write(self) -> str:
        """
        The S3 secret key for writing.
        """
        return self._data.get("secretKeyWrite") or ""

    @property
    def endpoint(self) -> str:
        """
        The S3 endpoint.
        """
        return self._data.get("endpoint") or ""

    @property
    def size(self) -> int:
        """
        The size setting of the resource type in GibiByte.
        """
        if "size" in self._data:
            return int(self._data["size"].get("value"))
        return 0

    @size.setter
    def size(self, value: int) -> None:
        self._data["size"] = {
            "value": value,
            "unit": "https://qudt.org/vocab/unit/GibiBYTE",
        }

    def __init__(self, data: dict | None = None) -> None:
        self._data = data if data else {}


class ResourceType:
    """
    Models the resource types available in Coscine.
    """

    _data: dict

    @property
    def options(self) -> ResourceTypeOptions:
        """
        The resource's resource type specific options.
        """
        try:
            options = self._data["options"]
            if self.general_type == "rdss3":
                options = options.get("rdsS3")
            elif self.general_type == "rdss3worm":
                options = options.get("rdsS3Worm")
            elif self.general_type == "rds":
                options = options.get("rds")
            elif self.general_type == "dsnrws3":
                options = options.get("dsNrwS3")
            elif self.general_type == "dsnrws3worm":
                options = options.get("dsNrwS3Worm")
            elif self.general_type == "dsnrwweb":
                options = options.get("dsNrwWeb")
            elif self.general_type == "gitlab":
                options = options.get("gitLab")
            elif self.general_type == "linked":
                options = options.get("linkedData")
            return ResourceTypeOptions(options)
        except KeyError:
            return ResourceTypeOptions()

    @property
    def id(self) -> str:
        """
        Coscine-internal resource type identifier.
        """
        return self._data.get("id") or ""

    @property
    def general_type(self) -> str:
        """
        General resource type, e.g. rdss3
        """
        general_type = self._data.get("generalType") or ""
        return general_type.lower()

    @property
    def specific_type(self) -> str:
        """
        Specific resource type, e.g. rdss3rwth
        """
        specific_type = self._data.get("specificType") or ""
        return specific_type.lower()

    @property
    def active(self) -> str:
        """
        Whether the resource type is enabled on the Coscine instance.
        """
        return self._data.get("status") or ""

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.specific_type

    def serialize(self) -> dict[str, dict]:
        """
        Serializes to resourceTypeOptions {},
        not type.
        """
        return self._data


class Resource:
    """
    Models a Coscine Resource object.
    """

    client: ApiClient
    project: Project
    _data: dict

    @property
    def id(self) -> str:
        """
        Unique Coscine-internal resource identifier.
        """
        return self._data.get("id") or ""

    @property
    def name(self) -> str:
        """
        Full resource name as displayed in the resource settings.
        """
        return self._data.get("name") or ""

    @name.setter
    def name(self, value: str) -> None:
        self._data["name"] = value

    @property
    def display_name(self) -> str:
        """
        Shortened resource name as displayed in the Coscine web interface.
        """
        return self._data.get("displayName") or ""

    @display_name.setter
    def display_name(self, value: str) -> None:
        self._data["displayName"] = value

    @property
    def description(self) -> str:
        """
        The resource description.
        """
        return self._data.get("description") or ""

    @description.setter
    def description(self, value: str) -> None:
        self._data["description"] = value

    @property
    def type(self) -> ResourceType:
        """
        The resource's resource type.
        """
        return ResourceType(self._data["type"])

    @property
    def pid(self) -> str:
        """
        The persistent identifier assigned to the resource.
        """
        return self._data.get("pid") or ""

    @property
    def url(self) -> str:
        """
        Project URL - makes the resource accessible in the web browser.
        """
        return f"{self.client.base_url}/p/{self.project.slug}/r/{self.id}/-/"

    @property
    def access_url(self) -> str:
        """Resource Access URL via PID"""
        return f"http://hdl.handle.net/{self.pid}"

    @property
    def keywords(self) -> list[str]:
        """
        List of keywords for better discoverability.
        """
        return self._data.get("keywords") or []

    @keywords.setter
    def keywords(self, value: list[str]) -> None:
        self._data["keywords"] = value

    @property
    def license(self) -> License | None:
        """
        The license used for the resource data.
        """
        value = self._data.get("license")
        if value:
            return License(value)
        return None

    @license.setter
    def license(self, value: License) -> None:
        self._data["license"] = value.serialize()

    @property
    def usage_rights(self) -> str:
        """
        The usage rights specified for the data inside the resource.
        """
        return self._data.get("usageRights") or ""

    @usage_rights.setter
    def usage_rights(self, value: str) -> None:
        self._data["usageRights"] = value

    @property
    def application_profile(self) -> ApplicationProfile:
        """
        The application profile of the resource.
        """
        uri = self._data["applicationProfile"]["uri"]
        return self.client.application_profile(uri)

    @property
    def disciplines(self) -> list[Discipline]:
        """
        The scientific disciplines set for the resource.
        """
        values = self._data.get("disciplines", [])
        return [Discipline(data) for data in values]

    @disciplines.setter
    def disciplines(self, value: list[Discipline]) -> None:
        self._data["disciplines"] = [discipline.serialize() for discipline in value]

    @property
    def visibility(self) -> Visibility:
        """
        The Coscine visibility setting for the resource.
        """
        return Visibility(self._data["visibility"])

    @visibility.setter
    def visibility(self, value: Visibility) -> None:
        self._data["visibility"] = value.serialize()

    @property
    def created(self) -> date:
        """
        Timestamp of when the resource was created.
        """
        value = self._data.get("dateCreated") or "1998-01-01T00:00:00Z"
        return parse_datetime(value)

    @property
    def creator(self) -> str:
        """
        The Coscine user id of the resource creator.
        """
        return self._data.get("creator") or ""

    @property
    def archived(self) -> bool:
        """
        Evaluates to True when the resource is set to archived.
        """
        return bool(self._data.get("archived"))

    @archived.setter
    def archived(self, value: bool) -> None:
        self._data["archived"] = value

    @property
    def quota(self) -> ResourceQuota:
        """
        The resources storage quota.
        """
        uri = self.client.uri(
            "projects", self.project.id, "resources", self.id, "quota"
        )
        return ResourceQuota(self.client.get(uri).data)

    @property
    def fixed_values(self) -> dict:
        """
        The resources default metadata values.
        """
        return self._data.get("fixedValues") or {}

    def __init__(self, project: Project, data: dict) -> None:
        self.client = project.client
        self.project = project
        self._data = data

    def __str__(self) -> str:
        return tabulate(
            [
                ("ID", self.id),
                ("Name", self.name),
                ("Display Name", self.display_name),
                ("Description", "\n".join(wrap(self.description))),
                ("Disciplines", "\n".join([str(i) for i in self.disciplines])),
                ("Date created", self.created),
                ("Creator", self.creator),
                ("PID", self.pid),
                ("Keywords", self.keywords),
                ("Visibility", self.visibility),
                ("Application Profile", self.application_profile.name),
                ("Usage rights", self.usage_rights),
                ("License", self.license),
                ("Archived", self.archived),
            ],
            disable_numparse=True,
        )

    def match(self, attribute: property, key: str) -> bool:
        """
        Attempts to match the resource via the given property
        and property value.
        Filterable properties:
        * Resource.id
        * Resource.pid
        * Resource.name
        * Resource.display_name
        * Resource.url

        Returns
        -------
        True
            If its a match ♥
        False
            Otherwise :(
        """
        if (
            (attribute is Resource.id and self.id == key)
            or (attribute is Resource.pid and self.pid == key)
            or (attribute is Resource.name and self.name == key)
            or (attribute is Resource.url and self.url == key)
            or ((attribute is Resource.display_name) and (self.display_name == key))
        ):
            return True
        return False

    def serialize(self) -> dict:
        """
        Serializes Coscine Resource metadata into machine-readable
        representation.
        """
        data = {
            "name": self.name,
            "displayName": self.display_name,
            "description": self.description,
            "id": self.id,
            "pid": self.pid,
            "keywords": self.keywords,
            "visibility": self.visibility.serialize(),
            "disciplines": [discipline.serialize() for discipline in self.disciplines],
            "applicationProfile": {"uri": self.application_profile.uri},
            "type": self.type.serialize(),
            "usageRights": self.usage_rights,
            "fixedValues": self.fixed_values,
            "archived": self.archived,
            "quota": self.quota.serialize(),
        }
        if self.license:
            data["license"] = self.license.serialize()
        return data

    def metadata_form(self, fixed_values: bool = True) -> MetadataForm:
        """
        Returns the resource metadata form.

        Parameters
        ----------
        fixed_values
            If set to true, the fixed values set in the resource are applied
            when creating the application profile.
            If set to false, they are ignored and an empty metadata form
            is returned.
        """
        return MetadataForm(
            self.application_profile, self.fixed_values if fixed_values else None
        )

    def update(self) -> None:
        """
        Change the values locally via setter properties
        """
        uri = self.client.uri("projects", self.project.id, "resources", self.id)
        self.client.put(uri, json=self.serialize())

    def delete(self) -> None:
        """
        Deletes the Coscine resource and along with it all files
        and metadata contained within it on the Coscine servers.
        Special care should be taken when using that method in code
        as to not accidentially trigger a delete on a whole resource.
        Therefore this method is best combined with additional input
        from the user e.g. by prompting them with the message
        "Do you really want to delete the resource? (Y/N)".
        """
        uri = self.client.uri("projects", self.project.id, "resources", self.id)
        self.client.delete(uri)

    def download(self, path: str = "./") -> None:
        """
        Downloads the resource to the local directory given by path.
        """
        path = join_paths(path, self.display_name, "")
        if not isdir(path):
            mkdir(path)
        for file in self.files(recursive=True):
            file.download(path, True)

    def mkdir(self, path: str, metadata: MetadataForm | None = None) -> None:
        """
        Creates a folder inside of a resource. Should work for all
        resource types.
        """
        if not path.endswith("/"):
            path += "/"
        self.upload(path, "", metadata)

    def upload(
        self,
        path: str,
        handle: BinaryIO | bytes | str,
        metadata: MetadataForm | dict | rdflib.Graph | None = None,
        progress: Callable[[int], None] | None = None,
        overwrite: bool = False,
    ) -> None:
        """
        Uploads a file-like object to a resource in Coscine.

        Parameters
        ----------
        path
            The path the file shall assume inside of the Coscine resource.
            Not the path on your local harddrive!
            The terms path, key and filename can be used interchangeably.
        handle
            A binary file handle that supports reading or
            a set of bytes or a string that can be utf-8 encoded.
        metadata
            Metadata for the file that matches the resource
            application profile.
        progress
            Optional callback function that gets occasionally called
            during the upload with the progress in bytes.
        """
        if isinstance(metadata, MetadataForm):
            metadata = metadata.serialize(path)
        elif isinstance(metadata, dict):
            raise NotImplementedError("Fill MetadataForm")
        elif isinstance(metadata, rdflib.Graph):
            metadata = {
                "path": path,
                "definition": {
                    "content": metadata.serialize(format="turtle"),
                    "type": "text/turtle",
                },
            }
        else:
            raise ValueError("unrecognized metadata format")
        if metadata is None and self.type.general_type != "rdss3":
            raise ValueError(
                "Resources other than S3 resources require metadata " "for uploads!"
            )
        if isinstance(handle, str):
            handle = handle.encode("utf-8")
        if isinstance(handle, bytes):
            handle = BytesIO(handle)
        if metadata is not None:
            self.update_metadata(metadata, overwrite)
        assert isinstance(handle, IOBase)
        if self.type.general_type == "rdss3" and self.client.native:
            self._upload_blob_s3(path, handle, progress)
        else:
            self._upload_blob(path, handle, progress)

    def post_metadata(self, metadata: dict) -> None:
        """
        Creates metadata for a file object for the first time.
        There shall be no metadata assigned to the file already - in that
        case use put_metadata()!
        """
        uri = self.client.uri(
            "projects", self.project.id, "resources", self.id, "trees", "metadata"
        )
        self.client.post(uri, json=metadata)

    def put_metadata(self, metadata: dict) -> None:
        """
        Updates existing metadata of a file object. If the file object
        does not yet have metadata, use post_metadata()!
        """
        uri = self.client.uri(
            "projects", self.project.id, "resources", self.id, "trees", "metadata"
        )
        self.client.put(uri, json=metadata)

    def update_metadata(self, metadata: dict, overwrite: bool = False) -> None:
        """
        Updates metadata of a file. In case no metadata has yet been
        assigned to the file, it will create new metadata. This method
        basically incorporates both post_metadata() and put_metadata()
        into one, choosing the appropriate method when applicable.
        This comes at the cost of possibly sending two requests, where
        one would have sufficed.
        """
        if overwrite:
            try:
                self.put_metadata(metadata)
            except RequestRejected:
                self.post_metadata(metadata)
        else:
            self.post_metadata(metadata)

    def _upload_blob(
        self,
        path: str,
        handle: BinaryIO,
        progress: Callable[[int], None] | None = None,
        use_put: bool = False,
    ):
        """
        Uploads a file-like object to a resource in Coscine.

        Parameters
        ----------
        path : str
            The path the file shall assume inside of the Coscine resource.
            Not the path on your local harddrive!
            The terms path, key and filename can be used interchangeably.
        handle : BinaryIO
            A binary file handle that supports reading.
        metadata : MetadataForm or dict
            Metadata for the file that matches the resource
            application profile.
        progress : Callable "def function(int)"
            Optional callback function that gets occasionally called
            during the upload with the progress in bytes.
        """
        uri = self.client.uri(
            "projects", self.project.id, "resources", self.id, "blobs", path
        )
        files = {"file": (path, handle, "application/octect-stream")}
        encoder = MultipartEncoder(fields=files)
        progress_bar = tqdm(
            smoothing=0.1,
            mininterval=0.5,
            desc=path,
            total=encoder.len,
            unit="B",
            unit_scale=True,
            ascii=True,
            disable=not self.client.verbose,
        )

        def progress_callback(mon):
            nonlocal progress_bar, progress
            progress_bar.update(mon.bytes_read - progress_bar.n)
            if progress:
                progress(mon.bytes_read)

        monitor = MultipartEncoderMonitor(encoder, progress_callback)
        headers = {"Content-Type": monitor.content_type}
        if use_put:
            self.client.put(uri, data=monitor, headers=headers)
        else:
            self.client.post(uri, data=monitor, headers=headers)

    def _upload_blob_s3(
        self, path: str, handle: BinaryIO, progress: Callable[[int], None] | None = None
    ) -> None:
        """
        Works only on rdss3 resources and should not be called
        on other resource types! Bypasses Coscine and uploads
        directly to the underlying s3 storage.
        """
        progress_bar = tqdm(
            smoothing=0.1,
            mininterval=0.5,
            desc=path,
            unit="B",
            unit_scale=True,
            ascii=True,
            disable=not self.client.verbose,
        )
        s3 = boto3.client(
            "s3",
            aws_access_key_id=self.type.options.access_key_write,
            aws_secret_access_key=self.type.options.secret_key_write,
            endpoint_url=self.type.options.endpoint,
        )

        bytes_read_abs = 0

        def progress_callback(bytes_read_inc):
            nonlocal progress_bar, progress, bytes_read_abs
            progress_bar.update(bytes_read_inc)
            bytes_read_abs += bytes_read_inc
            if progress:
                progress(bytes_read_abs)

        s3.upload_fileobj(
            handle, self.type.options.bucket_name, path, Callback=progress_callback
        )

    def _fetch_files_recursively(self, path: str = ""):
        more_folders: bool = True
        contents: list[FileObject] = []
        directories: list[FileObject] = []
        for fileobj in self._fetch_files(path):
            if more_folders:
                more_folders = False
            if fileobj.is_folder:
                directories.append(fileobj)
                if fileobj.path != "/":
                    yield from self._fetch_files(fileobj.path)
                more_folders = True
            else:
                yield fileobj

    def _fetch_files(self, path: str = ""):
        uri = self.client.uri(
            "projects", self.project.id, "resources", self.id, "trees", "files"
        )
        params = {"Path": path} if path else {}
        for page in self.client.get(uri, params=params).pages():
            for item in page.data:
                yield FileObject(self, item)

    def files(
        self, path: str = "", recursive: bool = False, with_metadata: bool = False
    ) -> list[FileObject]:
        """
        Retrieves the list of files that are contained in the resource.
        Via an additional single API call the metadata for those files
        can be fetched and made available in the returned files.

        Parameters
        ----------
        path
            You can limit the set of returned files to a path.
            The path may be the path to a single file in which
            case a list containing that single file will be returned.
            Or it may point to a "directory" in which case all
            the files contained in that "directory" are returned.
        recursive
            S3 resources may have folders inside them. Set the recursive
            parameter to True to also fetch all files contained
            in these folders.
        with_metadata
            If set to True the set of files are returned alongside
            with their metadata. This internally requires another
            API request which is considerably slower (1 to 2 seconds).
            However if you plan on manipulating each files metadata
            this is the way to go. Otherwise you would have to make
            an API call to fetch the metadata for each file which
            in case of large resources will prove to be very painful... :)
        """
        if recursive:
            files = self._fetch_files_recursively(path)
        else:
            files = self._fetch_files(path)
        if with_metadata:
            metadata = self.metadata(path)
            for file in files:
                file.assign_metadata(metadata)
        return files

    def file(self, path: str) -> FileObject:
        """
        Returns a single file of the resource via its unique path.
        """
        uri = self.client.uri(
            "projects", self.project.id, "resources", self.id, "trees", "files"
        )
        files = [
            FileObject(self, item)
            for item in self.client.get(uri, params={"Path": path}).data
        ]
        if len(files) > 1:
            # path argument acts as prefix, may yield more than 1 result
            # Only return exact matches!
            for f in files:
                if f.path == path:
                    return f
            raise NotFoundError
        if len(files) == 0:
            raise NotFoundError
        return files[0]

    def metadata(self, path: str = "") -> list[FileMetadata]:
        """
        Returns the full set of metadata for each file in the resource.
        """
        uri = self.client.uri(
            "projects", self.project.id, "resources", self.id, "trees", "metadata"
        )
        params = {"Path": path} if path else {}
        return [
            FileMetadata(item)
            for page in self.client.get(uri, params=params).pages()
            for item in page.data
        ]

    def graph(self) -> rdflib.Graph:
        """
        Returns a knowledge graph with the full set of file object metadata.
        """
        graph = self.application_profile.graph
        for metadata in self.metadata():
            if metadata.is_latest:
                subgraph = metadata.fixed_graph(self)
                graph += subgraph
        return graph

    def query(self, sparql: str) -> list[FileObject]:
        """
        Runs a SPARQL query on the underlying resource knowledge graph and
        returns the file objects whose metadata matches the query.
        IMPORTANT: The query must (!) include ?path as a variable/column.
        Otherwise it will get rejected and a ValueError is raised.

        Examples
        --------
        >>> resource.query("SELECT ?path ?p ?o { ?path ?p ?o . }")

        >>> project = client.project("Solaris")
        >>> resource = project.resource("Chest X-Ray CNN")
        >>> files = resource.query(
        >>>     "SELECT ?path WHERE { "
        >>>     "    ?path dcterms:creator ?creator . "
        >>>     "     FILTER(?creator != 'Dr. Akula') "
        >>>     "}"
        >>> )
        >>> for file in files:
        >>>     print(file.path)
        """
        results: rdflib.query.Result = self.graph().query(sparql)
        columns: list[str] = [x.toPython() for x in results.vars]
        if "?path" not in columns:
            raise ValueError("?path not present in sparql query string!")
        files: list[FileObject] = []
        filepaths: list[str] = [row.path.split("/")[6] for row in results]
        for file in self.files(recursive=True, with_metadata=True):
            if file.path in filepaths:
                files.append(file)
        return files

    def file_index(self) -> list[dict]:
        """
        Returns a file index with the following data:
        {
            file-path: {
                filename: "foo",
                filesize: 0,
                download: http://example.org/foo,
                expires: datetime
            }, ...
        }
        This index can easily be serialized to JSON format and made available
        publicly. Coscine currently prohibits external users from
        downloading files in a resource.
        To be able to publicly make data available one can
        instead publish this file index, which needs to be updated in
        regular intervals to ensure that the download urls do not expire.
        By hosting the json-serialized representation of this index on
        a free to use platform such as GitHub, one can access it via browser
        or via software and thus use Coscine as a storage provider in software
        and data publications regardless of whether people have access
        to Coscine.
        """
        return [
            {
                "path": file.path,
                "filename": file.name,
                "filesize": file.size,
                "download": file.download_url,
                "expires": file.download_expires,
            }
            for file in self.files(recursive=True)
            if not file.is_folder
        ]


class FileObject:
    """
    Models files or file-like objects in Coscine resources.
    """

    _data: dict
    _metadata: FileMetadata | None
    resource: Resource

    @property
    def path(self) -> str:
        """
        The path to the file. Usually equivalent to the filename, except
        when the file is a directory or contained within a directory.
        Which in the case of S3 resource may occur regularly.

        Examples
        ---------
        >>> chest_xray.png
        >>> pneumonia/lung_ap.png
        >>> pneumonia/
        """
        return self._data.get("path") or ""

    @property
    def type(self) -> str:
        """
        The type of the file object in the file tree.

        Examples
        ---------
        >>> Leaf
        >>> Tree
        """
        return self._data.get("type") or ""

    @property
    def filetype(self) -> str:
        """
        The file's filetype.

        Examples
        --------
        >>> ".png"
        >>> ".txt"
        >>> ""
        """
        return splitext(self.name)[1]

    @property
    def directory(self) -> str:
        """
        The directory the file object is located in, if it is in a folder.
        """
        return self._data.get("directory") or ""

    @property
    def name(self) -> str:
        """
        The filename of the file. Includes the file type extension.

        Examples
        --------
        >>> foo.txt
        >>> bar.png

        """
        return self._data.get("name") or ""

    @property
    def extension(self) -> str:
        """
        The file type extension.
        """
        return self._data.get("extension") or ""

    @property
    def size(self) -> int:
        """
        The size of the file contents in bytes.
        """
        value = self._data.get("size") or 0
        return int(value)

    @property
    def created(self) -> date:
        """
        Timestamp of when the file has been uploaded.
        """
        value = self._data.get("creationDate") or "1998-01-01T00:00:00Z"
        return parse_datetime(value)

    @property
    def modified(self) -> date:
        """
        Timestamp of when the file was recently modified.
        """
        value = self._data.get("changeDate") or "1998-01-01T00:00:00Z"
        return parse_datetime(value)

    @property
    def is_folder(self) -> bool:
        """
        Evaluates to True when the FileObject represents a folder and
        not an actual file.
        """
        return self.type == "Tree"

    @property
    def download_url(self) -> str:
        """
        The download URL for the file.
        """
        if "actions" in self._data:
            return self._data["actions"]["download"]["url"]
        return ""

    @property
    def download_expires(self) -> datetime:
        """
        The timestamp when the FileObject.download_url will expire.
        """
        if self.download_url:
            expires = parse_qs(urlparse(self.download_url).query)["Expires"][0]
        else:
            expires = "0"
        return datetime.fromtimestamp(float(expires))

    @property
    def client(self) -> ApiClient:
        """
        The Coscine ApiClient associated with the resource instance.
        """
        return self.resource.client

    def __init__(
        self, resource: Resource, data: dict, metadata: FileMetadata | None = None
    ) -> None:
        self.resource = resource
        self._data = data
        self._metadata = metadata

    def __str__(self) -> str:
        return self.path

    def delete(self) -> None:
        """
        Deletes the FileObject remote on the Coscine server.
        """
        uri = self.client.uri(
            "projects",
            self.resource.project.id,
            "resources",
            self.resource.id,
            "blobs",
            self.path,
        )
        self.client.delete(uri)

    def metadata(self, refresh: bool = True) -> FileMetadata | None:
        """
        Returns the metadata of the file. This might use a cached version
        of file metadata or make a request, if no cached version is available.
        """
        if (not self._metadata) and refresh:
            data = self.resource.metadata(path=self.path)
            self.assign_metadata(data)
        return self._metadata

    def metadata_form(self, refresh: bool = True) -> MetadataForm:
        """
        Returns the metadata of the file or an empty metadata form if
        no metadata has been attached to the file.
        """
        form = MetadataForm(self.resource.application_profile)
        metadata = self.metadata(refresh=refresh)
        if metadata:
            form.parse(metadata)
        return form

    def download(self, path: str = "./", recursive: bool = False) -> None:
        """
        Downloads the file to the computer.
        If path ends in a filename, the whole path is used.
        Otherwise the filename of the file is appended to the given path.
        If recursive is True, the full path of the file is used and appended
        to the path. But all folders on that path must have already been
        created then.
        """
        if not basename(path):
            path = join_paths(path, self.path if recursive else self.name)
        filepath = path
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        if self.is_folder:
            return
        else:
            # Since Coscine allows directories and files to share the same name
            # we need to handle collisions on the client side. Most filesystems
            # such as FAT and NTFS do not allow files to have the same name
            # as a folder within the same directory.
            for i in range(100):
                if not isdir(filepath):
                    break
                filepath = f"{path} ({i})"
            with open(filepath, "wb") as fp:
                self.stream(fp)

    def stream(self, fp: BinaryIO) -> None:
        """
        Streams file contents.
        """
        if self.resource.type.general_type == "rdss3" and self.client.native:
            self.stream_s3(fp)
        else:
            self.stream_blob(fp)

    def stream_blob(self, fp: BinaryIO) -> None:
        """
        Streams file contents from the Coscine Blob API.
        """
        uri = self.client.uri(
            "projects",
            self.resource.project.id,
            "resources",
            self.resource.id,
            "blobs",
            self.path,
        )
        progress_bar = tqdm(
            smoothing=0.1,
            mininterval=0.5,
            desc=self.path,
            total=self.size,
            unit="B",
            unit_scale=True,
            ascii=True,
            disable=not self.client.verbose,
        )
        response = self.client.request("GET", uri, stream=True)
        for chunk in response.response.iter_content(chunk_size=4096):
            progress_bar.update(len(chunk))
            fp.write(chunk)

    def stream_s3(self, handle: BinaryIO) -> None:
        """
        Works only on rdss3 resources and should not be called
        on other resource types! Bypasses Coscine and uploads
        directly to the underlying s3 storage.
        """
        progress_bar = tqdm(
            smoothing=0.1,
            mininterval=0.5,
            desc=self.path,
            total=self.size,
            unit="B",
            unit_scale=True,
            ascii=True,
            disable=not self.client.verbose,
        )
        s3 = boto3.client(
            "s3",
            aws_access_key_id=self.resource.type.options.access_key_write,
            aws_secret_access_key=self.resource.type.options.secret_key_write,
            endpoint_url=self.resource.type.options.endpoint,
        )
        s3.download_fileobj(
            self.resource.type.options.bucket_name,
            self.path,
            handle,
            Callback=progress_bar.update,
        )

    def update(
        self,
        handle: BinaryIO | bytes | str,
        progress: Callable[[int], None] | None = None,
    ) -> None:
        """
        Uploads a file-like object to a resource in Coscine.

        Parameters
        ----------
        handle : BinaryIO | bytes | str
            A binary file handle that supports reading or
            bytes or str.
        progress : Callable "def function(int)"
            Optional callback function that gets occasionally called
            during the upload with the progress in bytes.
        """
        if isinstance(handle, str):
            handle = handle.encode("utf-8")
        if isinstance(handle, bytes):
            handle = BytesIO(handle)

        if self.type.general_type == "rdss3" and self.client.native:
            self.resource._upload_blob_s3(self.path, handle, progress)
        else:
            self.resource._upload_blob(self.path, handle, progress, use_put=True)

    def update_metadata(self, metadata: MetadataForm | dict | rdflib.Graph) -> None:
        """
        Updates the metadata for a file object or creates new metadata
        if there has not been metadata assigned yet.
        """
        self._metadata = None
        if isinstance(metadata, MetadataForm):
            metadata = metadata.serialize(self.path)
        elif isinstance(metadata, dict):
            raise NotImplementedError("Fill MetadataForm")
        elif isinstance(metadata, rdflib.Graph):
            metadata = {
                "path": self.path,
                "definition": {
                    "content": metadata.serialize(format="turtle"),
                    "type": "text/turtle",
                },
            }
        else:
            raise ValueError("unrecognized metadata format")
        self.resource.update_metadata(metadata)

    def post_metadata(self, metadata: MetadataForm | dict | rdflib.Graph) -> None:
        """
        Creates metadata for a file object for the first time.
        There shall be no metadata assigned to the file already - in that
        case use put_metadata()!
        """
        if isinstance(metadata, MetadataForm):
            metadata = metadata.serialize(self.path)
        elif isinstance(metadata, dict):
            raise NotImplementedError("Fill MetadataForm")
        elif isinstance(metadata, rdflib.Graph):
            metadata = {
                "path": self.path,
                "definition": {
                    "content": metadata.serialize(format="turtle"),
                    "type": "text/turtle",
                },
            }
        else:
            raise ValueError("unrecognized metadata format")
        self.resource.post_metadata(metadata)

    def put_metadata(self, metadata: MetadataForm | dict | rdflib.Graph) -> None:
        """
        Updates existing metadata of a file object. If the file object
        does not yet have metadata, use post_metadata()!
        """
        if isinstance(metadata, MetadataForm):
            metadata = metadata.serialize(self.path)
        elif isinstance(metadata, dict):
            raise NotImplementedError("Fill MetadataForm")
        elif isinstance(metadata, rdflib.Graph):
            metadata = {
                "path": self.path,
                "definition": {
                    "content": metadata.serialize(format="turtle"),
                    "type": "text/turtle",
                },
            }
        else:
            raise ValueError("unrecognized metadata format")
        self.resource.put_metadata(metadata)

    def assign_metadata(self, metadata: list[FileMetadata]) -> None:
        """
        Assigns locally available metadata to the file object.
        This is mostly used internally and can be ignored by most users.
        """
        for item in metadata:
            if item.path == self.path and item.is_latest:
                self._metadata = item
                return
