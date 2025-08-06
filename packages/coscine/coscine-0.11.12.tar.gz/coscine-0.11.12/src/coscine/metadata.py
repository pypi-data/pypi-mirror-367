###############################################################################
# Coscine Python SDK
# Copyright (c) 2020-2025 RWTH Aachen University
# Licensed under the terms of the MIT License
# For more information on Coscine visit https://www.coscine.de/.
###############################################################################

"""
Provides functions and classes around the handling of metadata.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, TypeAlias
from datetime import date, datetime, time, timedelta
from threading import Lock
from decimal import Decimal
import random
import logging
from string import ascii_letters
from requests.compat import urlparse
from tabulate import tabulate
from isodate import parse_duration, parse_datetime, parse_date, parse_time
import rdflib
import rdflib.term
import pyshacl
from coscine.exceptions import NotFoundError
if TYPE_CHECKING:
    from coscine.client import ApiClient
    from coscine.resource import Resource


logger = logging.getLogger(__name__)


# Type Alias according to PEP 613 for supported metadata value types
FormType: TypeAlias = (
    bool | date | datetime | Decimal | int | float | str | time | timedelta
)

# XML Schema datatype to Python native type lookup table
XSD_TYPES: dict[str, type] = {
    "any": str,
    "anyURI": str,
    "anyType": str,
    "byte": int,
    "int": int,
    "integer": int,
    "long": int,
    "unsignedShort": int,
    "unsignedByte": int,
    "negativeInteger": int,
    "nonNegativeInteger": int,
    "nonPositiveInteger": int,
    "positiveInteger": int,
    "short": int,
    "unsignedLong": int,
    "unsignedInt": int,
    "double": float,
    "float": float,
    "decimal": Decimal,
    "boolean": bool,
    "date": date,
    "dateTime": datetime,
    "duration": timedelta,
    "gDay": datetime,
    "gMonth": datetime,
    "gMonthDay": datetime,
    "gYear": datetime,
    "gYearMonth": datetime,
    "time": time,
    "ENTITIES": str,
    "ENTITY": str,
    "ID": str,
    "IDREF": str,
    "IDREFS": str,
    "language": str,
    "Name": str,
    "NCName": str,
    "NMTOKEN": str,
    "NMTOKENS": str,
    "normalizedString": str,
    "QName": str,
    "string": str,
    "token": str
}


def xsd_to_python(xmltype: str) -> type:
    """
    Converts an XMLSchema XSD datatype string to a native
    Python datatype class instance.
    """
    if xmltype.startswith("http://www.w3.org/2001/XMLSchema#"):
        xmltype = urlparse(xmltype)[-1]
        if xmltype not in XSD_TYPES:
            raise ValueError(
                "Failed to convert XMLSchema XSD datatype "
                f"to native Python type: Unsupported type '{xmltype}'!"
            )
        return XSD_TYPES[xmltype]
    return str


class Instance:
    """
    A (vocabulary) instance is an entry inside of a vocabulary.
    It maps from a human-readable name to a unique uniform
    resource identifier.
    """

    _data: dict

    @property
    def graph_uri(self) -> str:
        """
        The uniform resource identifier of the graph.
        If entered in a web browser, it should yield the definition
        of the graph.

        Example:
        >>> http://www.dfg.de/dfg_profil/gremien/fachkollegien/faecher/
        """
        return self._data.get("graphUri") or ""

    @property
    def instance_uri(self) -> str:
        """
        The uniform resource identifier of the instance.
        If entered in a web browser, it should yield the definition
        of the instance.

        Example:
        >>> http://www.dfg.de/dfg_profil/gremien/fachkollegien/liste/
        >>> index.jsp?id=112#112-03
        -> The item with id 112 within the graph
        """
        return self._data.get("instanceUri") or ""

    @property
    def type_uri(self) -> str:
        """
        Identifies the type of instance.

        Example:
        >>> http://www.dfg.de/dfg_profil/gremien/fachkollegien/liste/
        >>> index.jsp?id=112#112-03
        -> Commonly the same as instance_uri
        """
        return self._data.get("typeUri") or ""

    @property
    def subclass_of(self) -> str:
        """
        Identifies the subclass of the instance.

        Example:
        >>> http://www.dfg.de/dfg_profil/gremien/fachkollegien/liste/
        >>> index.jsp?id=112
        -> subclass of the item
        """
        return self._data.get("subClassOfUri") or ""

    @property
    def name(self) -> str:
        """
        The display name of the instance.
        """
        return self._data.get("displayName") or ""

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.name


class Vocabulary:
    """
    The Vocabulary contains all instances of a class and provides
    an interface to easily check whether a term is contained in
    the set of instances and to query the respective instance.
    """

    _data: list[Instance]

    def __init__(self, data: list[Instance]) -> None:
        self._data = data

    def __str__(self) -> str:
        return "\n".join(self.keys())

    def __contains__(self, key: str) -> bool:
        return key in self.keys()

    def __getitem__(self, key: str) -> str:
        for entry in self._data:
            if entry.name == key:
                return entry.instance_uri
        raise KeyError(f"Key {key} is not contained in vocabulary!")

    def __iter__(self):
        for key in self.keys():
            yield key

    def graph(self) -> rdflib.Graph:
        """
        Returns the vocabulary as an rdflib knowledge graph.
        """
        graph = rdflib.Graph()
        for entry in self._data:
            graph.add((
                rdflib.URIRef(entry.instance_uri),
                rdflib.RDF.type,
                rdflib.URIRef(entry.type_uri)
            ))
            graph.add((
                rdflib.URIRef(entry.instance_uri),
                rdflib.RDFS.label,
                rdflib.Literal(entry.name)
            ))
            if entry.subclass_of:
                graph.add((
                    rdflib.URIRef(entry.instance_uri),
                    rdflib.RDFS.subClassOf,
                    rdflib.URIRef(entry.subclass_of)
                ))
        return graph

    def keys(self) -> list[str]:
        """
        Returns the list of keys that are contained inside
        of the vocabulary. This equals the set of names of the
        class instances.
        """
        return [entry.name for entry in self._data]

    def resolve(self, value: str) -> FormType:
        """
        This method takes a value and returns its corresponding key.
        It can be considered the reverse of Vocabulary[key] -> value,
        namely Vocabulary[value] -> key but that cannot be expressed
        in Python, hence this method.
        """
        for entry in self._data:
            if entry.instance_uri == value:
                return entry.name
        raise KeyError(f"Value {value} is not contained in vocabulary!")


class FormField:
    """
    A FormField represents a MetadataField that has been specified
    in an application profile. The FormField has numerous properties
    which restrict the range of values that can be assigned to
    a metadata field. It is thus very important for the validation
    of metadata and ensures the consistency of metadata.
    """

    client: ApiClient

    _data: dict
    _values: list[FormType | MetadataForm]
    _vocabulary: Vocabulary | None

    @property
    def path(self) -> str:
        """
        The path of the FormField, acting as a unique identifier.
        """
        return self._data.get("path") or ""

    @property
    def name(self) -> str:
        """
        The human-readable name of the field, as displayed in
        the Coscine web interface.
        """
        return self._data.get("name") or ""

    @property
    def order(self) -> int:
        """
        The order of appearance of the field. The metadata fields are
        often displayed in a list in some sort of user interface. This
        property simply states at which position the field should appear.
        """
        return int(self._data.get("order") or 1)

    @property
    def class_uri(self) -> str:
        """
        In case the field is controlled by a vocabulary, the class_uri
        specifies the link to the instances of the vocabulary. These
        can then be fetched via ApiClient.instances(class_uri)
        """
        return self._data.get("class") or ""

    @property
    def min_count(self) -> int:
        """
        The minimum count of values that the field must receive.
        If the count is greater than 0, the field is a required one,
        as it will always need a value.
        """
        return self._data.get("minCount") or 0

    @property
    def max_count(self) -> int:
        """
        The maximum amount of values that can be given to the field.
        """
        return self._data.get("maxCount") or 128

    @property
    def min_length(self) -> int:
        """
        Specifies the minumum required length of the value.
        For values of type string this would equal the minimum
        string length.
        """
        return self._data.get("minLength") or 0

    @property
    def max_length(self) -> int:
        """
        Specifies the maximum permissible length of the value.
        For values of type string this would equal the maximum
        string length.
        """
        return self._data.get("maxLength") or 4096

    @property
    def literals(self) -> list[rdflib.Literal]:
        """
        The field as rdflib.Literal ready for use with rdflib.
        The literal has the appropriate datatype as specified in
        the SHACL application profile. This should be used as Coscine
        is very strict with its verification: There is apparently
        a difference between xsd:int and xsd:integer, I kid you not!
        """
        # See also: https://rdflib.readthedocs.io/en/stable/rdf_terms.html
        return [
            rdflib.Literal(value, datatype=self.xsd_type)
            for value in self.values
        ]

    @property
    def identifiers(self) -> list[rdflib.Literal] | list[rdflib.URIRef]:
        """
        The list of values as rdflib identifiers.
        """
        if self.has_vocabulary:
            return [rdflib.URIRef(serial) for serial in self.serial]
        return self.literals

    @property
    def node(self) -> str:
        """
        The node property of the metadata field, if present.
        """
        return self._data.get("node") or ""

    @property
    def xsd_type(self) -> str | None:
        """
        The string representation of the xsd:datatype.
        For example: http://www.w3.org/2001/XMLSchema#int
        """
        return self._data.get("datatype") or None

    @property
    def datatype(self) -> type:
        """
        Restricts the datatype of values that can be assigned
        to the field.
        """
        if self.is_inherited:
            return MetadataForm
        return xsd_to_python(self._data.get("datatype") or "")

    @property
    def vocabulary(self) -> Vocabulary:
        """
        In the case that the field has a value for the class_uri property,
        it is controlled by a vocabulary.
        """
        if not self.has_vocabulary:
            raise NotFoundError(
                f"Field {self.name} is not controlled by a vocabulary!"
            )
        if not self._vocabulary:
            self._vocabulary = self.client.vocabulary(self.class_uri)
        return self._vocabulary

    @property
    def selection(self) -> list[str]:
        """
        Some fields have a predefined selection of values that the user
        can choose from. In that case other values are not permitted.
        """
        return self._data.get("selection", "").split("~,~") or []

    @property
    def language(self) -> str:
        """
        The language setting of the field. This influences the field
        name and the values of fields controlled by a vocabulary or
        selection.
        """
        return self._data.get("language") or "en"

    @property
    def has_vocabulary(self) -> bool:
        """
        Evaluates to True if the field values are controlled by a vocabulary.
        """
        return bool(self._data["class"])

    @property
    def has_selection(self) -> bool:
        """
        Evaluates to True if the field values are controlled
        by a predefined selection of values.
        """
        return bool(self._data["selection"])

    @property
    def is_controlled(self) -> bool:
        """
        Evaluates to True if the field is either controlled by
        a vocabulary or a selection.
        """
        return self.has_vocabulary or self.has_selection

    @property
    def is_required(self) -> bool:
        """
        Evaluates to True if the field must be assigned a value before
        it can be sent to Coscine alongside the other metadata.
        """
        return self.min_count > 0

    @property
    def is_inherited(self) -> bool:
        """
        Evaluates to True if the field refers to another MetadataForm.
        """
        return bool(self.node)

    @property
    def serial(self) -> list[str]:
        """
        Serializes the metadata value to Coscine format. That means
        that for vocabulary controlled fields, the human-readable
        value is translated to the machine-readable unique identifier.
        This property can also be set with the metadata value received
        by the Coscine API, which is already in machine-readable format
        and will be translated to human-readable internally.
        """
        return self.serialize()

    @serial.setter
    def serial(self, value: str) -> None:
        self.values = [self.deserialize(value)]

    @property
    def values(self) -> list[FormType | MetadataForm]:
        """
        This is the value of the metadata field in human-readable
        form. For the machine-readable form that is sent to Coscine
        use the property FormValue.serial!
        Setting a value can only be done by using the appropriate datatype.
        If the FormField.max_count is greater than 1, you may assign a list
        of values to the field.
        """
        return self._values

    @values.setter
    def values(
        self,
        value: FormType | list[FormType | MetadataForm] | MetadataForm
    ) -> None:
        if isinstance(value, (list, tuple)):
            self._values = []
            for item in value:
                self.append(item)
        else:
            self.validate(value)
            self._values = [value]

    def _merge_default(
        self,
        root_node: rdflib.term.Node,
        graph: rdflib.Graph
    ) -> None:
        for value in self.identifiers:
            graph.add((root_node, rdflib.URIRef(self.path), value))

    def _merge_inherited(
        self,
        root_node: rdflib.term.Node,
        graph: rdflib.Graph
    ) -> None:
        for form in self.values:
            assert isinstance(form, MetadataForm)
            container = rdflib.term.BNode()
            graph.add((root_node, rdflib.URIRef(self.path), container))
            graph.add((container, rdflib.RDF.type, rdflib.URIRef(self.node)))
            for field in form.fields():
                field.merge(container, graph)

    def merge(self, root_node: rdflib.term.Node, graph: rdflib.Graph) -> None:
        """
        Merges the field as a value to root_node into an RDFlib graph
        """
        if not bool(self.values):
            return
        if self.is_inherited:
            self._merge_inherited(root_node, graph)
        else:
            self._merge_default(root_node, graph)

    def strlist(self) -> list[str]:
        """
        """
        entries = []
        if not self.invisible:
            if self.is_inherited:
                controlled = "Inherited"
                #values = self.node
                values = "\n".join([str(v) for v in self.values])
            else:
                controlled = "Controlled" if self.is_controlled else "Default"
                values = "\n".join([str(v) for v in self.values])
            entries = [
                self.is_required,
                controlled,
                self.datatype.__name__,
                f"{self.min_count} - {self.max_count}",
                self.name,
                values
            ]
        return entries

    def validate(self, value: FormType | MetadataForm) -> None:
        """
        Validates whether the value matches the specification of the
        FormField. Does not return anything but instead raises all
        sorts of exceptions.
        """
        if not isinstance(value, self.datatype):
            raise TypeError(
                f"While setting value for field {self.name}: "
                f"Expected type {self.datatype} but got {type(value)}!"
            )
        if self.is_controlled:
            assert isinstance(value, str)
            if self.has_vocabulary and value not in self.vocabulary:
                raise ValueError(
                    f"The field '{self.name}' is controlled by a vocabulary. "
                    f"The value '{value}' that you have provided did not "
                    "match any of the entries in the vocabulary!"
                )
            if self.has_selection and value not in self.selection:
                raise ValueError(
                    f"The field '{self.name}' is controlled by a selection. "
                    f"The value '{value}' that you have provided did not "
                    "match any of the entries in the selection!"
                )

    def metadata_form(self) -> MetadataForm:
        """
        Returns the inherited child MetadataForm if the field is inherited.
        """
        if not self.is_inherited:
            raise TypeError(f"The field {self.name} is not inherited!")
        return MetadataForm(self.client.application_profile(self.node))

    @property
    def invisible(self) -> bool:
        """
        FormFields can be set to invisible in the Coscine resource metadata
        default value settings. Inivisble FormFields are not displayed.
        """
        return self._invisible

    @invisible.setter
    def invisible(self, value: bool) -> None:
        self._invisible = value

    def append(
        self,
        value: FormType | MetadataForm,
        serialized: bool = False
    ) -> None:
        """
        If the field accepts a list of values, one can use the append
        method to add another value to the end of that list.
        """
        if serialized:
            if not isinstance(value, str):
                raise TypeError("Serialized values must be strings!")
            value = self.deserialize(value)
        self.validate(value)
        self._values.append(value)

    def serialize(self) -> list[str]:
        """
        Serializes the form field values into machine readable format.
        """
        if self.has_vocabulary:
            serialized_values = []
            for value in self.values:
                if not isinstance(value, str):
                    raise TypeError(f"Value '{value}' is not a string")
                serialized_values.append(self.vocabulary[value])
            return serialized_values
        return [str(value) for value in self.values]

    def deserialize(self, value: str) -> FormType:
        """
        Unmarshals the value and returns the pythonic representation.
        """
        if self.has_vocabulary:
            return self.vocabulary.resolve(value)
        if self.datatype == datetime:
            return parse_datetime(value)
        if self.datatype == date:
            return parse_date(value)
        if self.datatype == time:
            return parse_time(value)
        if self.datatype == timedelta:
            return parse_duration(value)
        if self.datatype == int:
            return int(value)
        if self.datatype == float:
            return float(value)
        if self.datatype == Decimal:
            return Decimal(value)
        if self.datatype == bool:
            return value.lower() == "true"
        return value

    def __init__(self, client: ApiClient, data: dict) -> None:
        self.client = client
        self._data = data
        self._invisible = False
        self._values = []
        self._vocabulary = None

    def clear(self) -> None:
        """
        Clears all values of all metadata fields.
        """
        self._values = []


class ApplicationProfileInfo:
    """
    Many different application profiles are available in Coscine.
    To be able to get information on a specific application profile or all
    application profiles, the ApplicationProfileInfo datatype is
    provided.
    """

    _data: dict

    @property
    def uri(self) -> str:
        """
        The uri of the application profile.
        """
        return self._data.get("uri") or ""

    @property
    def name(self) -> str:
        """
        The human-readable name of the application profile.
        """
        return self._data.get("displayName") or ""

    @property
    def description(self) -> str:
        """
        A description of the application profile.
        """
        return self._data.get("description") or ""

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.name


class ApplicationProfile(ApplicationProfileInfo):
    """
    An application profile defines how metadata can be specified.

    Parameters
    ----------
    client
        A Coscine Python SDK ApiClient for access to settings and requests.
    data
        ApplicationProfileInfo data as received by Coscine.
    """

    _data: dict

    client: ApiClient
    graph: rdflib.Graph
    lock = Lock()

    @property
    def definition(self) -> str:
        """
        The actual application profile in text/turtle format.
        """
        return self._data["definition"].get("content") or ""

    def __init__(self, client: ApiClient, data: dict) -> None:
        super().__init__(data)
        self.client = client
        self.graph = rdflib.Graph()
        self.graph.bind("sh", "http://www.w3.org/ns/shacl#")
        self.graph.bind("dcterms", "http://purl.org/dc/terms/")
        self.graph.parse(data=self.definition, format="ttl")
        self._determine_target_class()
        self._resolve_imports()

    def __str__(self) -> str:
        return str(self.graph.serialize(format="ttl"))

    def _determine_target_class(self) -> None:
        """
        Figures out the target class of the application profile.
        If not target class is present, the application profile URI is used
        as a fallback.
        """
        results = self.query(
            r"SELECT ?targetClass WHERE { ?_ sh:targetClass ?targetClass . }"
        )
        if len(results) != 1 or len(results[0]) != 1:
            self._target_class = self.uri
        else:
            self._target_class = results[0][0]

    def _resolve_imports(self) -> None:
        """
        Recursively resolves owl:imports statements
        """
        for row in self.query(
            "SELECT ?url WHERE { ?target sh:node ?url . }",
            initBindings={"target": rdflib.URIRef(self.uri)}
        ):
            profile = self.client.application_profile(str(row[0]))
            self.graph += profile.graph

        # Previous implementation:
        #for row in self.query("SELECT ?url WHERE { ?_ owl:imports ?url . }"):
        #    profile = self.client.application_profile(str(row[0]))
        #    self.graph += profile.graph

    @property
    def target_class(self) -> str:
        """
        Returns the target class of the application profile.
        If no target class is present, the application profile URI is used
        as a fallback.
        """
        return self._target_class

    def query(self, query: str, **kwargs) -> list:
        """
        Performs a SPARQL query on the application profile and
        returns the results as a list of rows, with each row
        containing as many columns as selected in the SPARQL query.

        Warnings
        ---------
        Note that rdflib SPARQL queries are NOT thread-safe! Under the
        hood pyparsing is invoked, which leads to a lot of trouble if
        used in a multithreaded context. To avoid any problems the
        Coscine Python SDK employs a lock on this function - only one
        thread can use it at any given time.
        TODO: Open pull request at rdflib and make rdflib itself thread-safe.

        Parameters
        ----------
        query
            A SPARQL query string.
        **kwargs
            Any number of keyword arguments to pass onto rdflib.query()
        """
        with self.lock:
            results: rdflib.query.Result = self.graph.query(query, **kwargs)
            items: list[list] = []
            for row in results:
                assert isinstance(row, rdflib.query.ResultRow)
                values = [
                    column.toPython() if column else None
                    for column in row
                ]
                items.append(values)
            return items

    def fields(self) -> list[FormField]:
        """
        Returns the list of metadata fields with their properties as specified
        in the application profile.
        """
        fields = []
        for result in self.query(
            "SELECT ?path ?name ?order ?class ?minCount ?maxCount\n"
            "?minLength ?maxLength ?datatype\n"
            "(GROUP_CONCAT(?in; SEPARATOR=\"~,~\") as ?ins)\n"
            "(lang(?name) as ?lang)\n"
            "?node\n"
            "WHERE {\n"
            "    ?_ sh:path ?path ;\n"
            "       sh:name ?name .\n"
            "    OPTIONAL { ?_ sh:order ?order . } .\n"
            "    OPTIONAL { ?_ sh:class ?class . } .\n"
            "    OPTIONAL { ?_ sh:minCount ?minCount . } .\n"
            "    OPTIONAL { ?_ sh:maxCount ?maxCount . } .\n"
            "    OPTIONAL { ?_ sh:minLength ?minLength . } .\n"
            "    OPTIONAL { ?_ sh:maxLength ?maxLength . } .\n"
            "    OPTIONAL { ?_ sh:datatype ?datatype . } .\n"
            "    OPTIONAL { ?_ sh:in/rdf:rest*/rdf:first ?in . } .\n"
            "    OPTIONAL { ?_ sh:node ?node . } . \n"
            "}\n"
            "GROUP BY ?name\n"
            "ORDER BY ASC(?order)\n"
        ):
            if result[10] == self.client.language:
                data: dict = {
                    "path": result[0],
                    "name": result[1],
                    "order": result[2],
                    "class": result[3],
                    "minCount": result[4],
                    "maxCount": result[5],
                    "minLength": result[6],
                    "maxLength": result[7],
                    "datatype": result[8],
                    "selection": result[9],
                    "language": result[10],
                    "node": result[11]
                }
                fields.append(FormField(self.client, data))
        return fields


class FileMetadata:
    """
    The existing metadata to a file as returned by the Coscine API.
    This metadata is by default in machine-readable format and not
    human-readable.
    """

    _data: dict

    @property
    def path(self) -> str:
        """
        Path/Identifier of the metadata field.
        """
        return self._data.get("path") or ""

    @property
    def type(self) -> str:
        """
        Datatype of the value as a string.
        """
        return self._data.get("type") or ""

    @property
    def version(self) -> str:
        """
        Current metadata version string. The version is a Unix timestamp.
        """
        return self._data.get("version") or ""

    @property
    def versions(self) -> list[str]:
        """
        List of all metadata version strings. Versions are unix timestamps.
        """
        versions = self._data.get("availableVersions")
        return list(versions) if versions else []

    @property
    def created(self) -> datetime:
        """
        The timestamp when the metadata was assigned.
        """
        return datetime.fromtimestamp(float(self.version))

    @property
    def definition(self) -> str:
        """
        The actual metadata in rdf turtle format.
        """
        turtle = self._data["definition"].get("content") or ""
        return turtle

    @property
    def is_latest(self) -> bool:
        """
        Returns True if the current metadata is the newest metadata
        for the file.
        """
        return self.version == max(self.versions)

    def graph(self) -> rdflib.Graph:
        """
        The metadata parsed as rdflib graph.
        """
        return rdflib.Graph().parse(data=self.definition, format="ttl")

    def fixed_graph(self, resource: Resource) -> rdflib.Graph:
        """
        Patches the file metadata knowledge graph to include the
        file path as its root subject.
        """
        graph = rdflib.Graph().parse(data=self.definition, format="ttl")
        for s, p, o in iter(graph.triples((None, None, None))):
            base: str = (
                f"https://purl.org/coscine/resources/{resource.id}/"
                f"{self.path}/@type=metadata&version={self.version}"
            )
            graph.remove((s, p, o))
            graph.add((rdflib.URIRef(base), p, o))
        return graph

    def items(self) -> list[dict[str, str]]:
        """
        Returns the list of metadata values in the format:
        >>> [{
        >>>     "path": "...",
        >>>     "value": "...",
        >>>     "datatype": "..."
        >>> }]
        """
        results: rdflib.query.Result = self.graph().query(
            "SELECT ?root ?property (str(?value) as ?value) "
            "(datatype(?value) as ?type)\n"
            "WHERE {\n"
            "    ?root ?property ?value .\n"
            "    FILTER( ?property != rdf:type )\n"
            "}\n"
        )
        items = []
        for row in results:
            assert isinstance(row, rdflib.query.ResultRow)
            root = str(row[0])
            path = str(row[1])
            value = str(row[2])
            datatype = str(row[3])
            item = {
                "root": root,
                "path": path,
                "value": value,
                "datatype": datatype
            }
            items.append(item)
        return items

    def __init__(self, data: dict) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.definition


class MetadataForm:
    """
    The metadata form makes the meatadata fields that have been
    defined in an application profile accessible to users.

    Parameters
    ----------
    resource
        Coscine resource instance
    fixed_values
        If set to true, the fixed values set in the resource are applied
        when creating the application profile.
        If set to false, they are ignored and an empty metadata form
        is returned.
    """

    _fields: list[FormField]
    _fixed_values: dict
    application_profile: ApplicationProfile

    def __init__(
        self,
        application_profile: ApplicationProfile,
        fixed_values: dict | None = None
    ) -> None:
        self.application_profile = application_profile
        self._fields = self.application_profile.fields()
        if fixed_values:
            self._fixed_values = fixed_values
            self.defaults()

    def __str__(self) -> str:
        entries = []
        for key in self.keys():
            columns = self.field(key).strlist()
            if columns:
                entries.append(columns)
        headers: list[str] = [
            "Required", "Mode", "Type", "Range", "Field", "Value"
        ]
        return tabulate(entries, headers=headers, disable_numparse=True)

    def __setitem__(
        self,
        key: str, values: FormType | MetadataForm | list[FormType | MetadataForm]
    ) -> None:
        self.field(key).values = values

    def __getitem__(self, key: str) -> list[FormType | MetadataForm]:
        return self.field(key).values

    def __delitem__(self, key: str) -> None:
        self.field(key).clear()

    def __contains__(self, key: str) -> bool:
        return key in self.keys()

    def __iter__(self):
        for key in self.keys():
            yield key

    def defaults(self) -> None:
        """
        Parses the fixed and default value settings of a resource.
        This also includes visibility settings for metadata fields.
        """
        self.clear()
        for field_path, values in self._fixed_values.items():
            try:
                field = self.path(field_path)
            except KeyError:
                logger.warning(f"Fixed value path '{field_path}' is invalid!")
                continue
            if "https://purl.org/coscine/defaultValue" in values:
                field.values = [
                    field.deserialize(v["value"])
                    for v in values["https://purl.org/coscine/defaultValue"]
                    if v["type"] != "bnode"
                ]
            elif "https://purl.org/coscine/fixedValue" in values:
                field.values = [
                    field.deserialize(v["value"])
                    for v in values["https://purl.org/coscine/fixedValue"]
                    if v["type"] != "bnode"
                ]
            if "https://purl.org/coscine/invisible" in values:
                setting = values["https://purl.org/coscine/invisible"]
                field.invisible = bool(int(setting[0]["value"]))

    def clear(self) -> None:
        """
        Clears all values.
        """
        for field in self.fields():
            field.clear()

    def fields(self) -> list[FormField]:
        """
        The list of metadata fields that can be filled in as defined
        in the application profile.
        """
        return self._fields

    def field(self, key: str) -> FormField:
        """
        Looks up a metadata field via its name.
        """
        for field in self._fields:
            if field.name == key:
                return field
        raise KeyError(f"The field {key} is not part of the form!")

    def path(self, path: str) -> FormField:
        """
        Looks up a metadata field via its path.
        """
        for field in self._fields:
            if field.path == path:
                return field
        raise KeyError(f"The field path {path} is not part of the form!")

    def paths(self) -> list[str]:
        """
        Returns the list of paths of all metadata fields.
        """
        return [field.path for field in self._fields]

    def keys(self) -> list[str]:
        """
        Returns the list of names of all metadata fields.
        """
        return [field.name for field in self._fields]

    def values(self) -> list[list[FormType | MetadataForm]]:
        """
        Returns the list of values of all metadata fields.
        """
        return [field.values for field in self._fields]

    def items(self) -> list[tuple[str, list[FormType | MetadataForm]]]:
        """
        Returns key, value pairs for all metadata fields
        """
        return list(zip(self.keys(), self.values()))

    def graph(self) -> rdflib.Graph:
        """
        Returns the metadata as a knowledge graph.
        """
        root = rdflib.BNode()
        graph = rdflib.Graph()
        graph.add((
            root,
            rdflib.RDF.type,
            rdflib.URIRef(self.application_profile.target_class)
        ))
        for field in self._fields:
            field.merge(root, graph)
        return graph

    def validate(self) -> bool:
        """
        Validates the metadata against the resource application profile SHACL.
        """
        ontologies = rdflib.Graph()
        for field in self.fields():
            if field.has_vocabulary:
                ontologies += field.vocabulary.graph()
        graph = self.graph() + ontologies
        conforms, _, results_text = pyshacl.validate(
            graph,
            shacl_graph=self.application_profile.graph,
            ont_graph=ontologies,
            debug=False,
            inference="rdfs",
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=False,
            meta_shacl=True,
            advanced=False,
            js=False
        )
        if not conforms:
            raise ValueError(results_text)
        return conforms

    def test(self) -> None:
        """
        Auto-fills the MetadataForm with a set of predefined values.
        Every field is filled in.
        """
        def generate_value(field: FormField):
            length = field.min_length if field.min_length > 1 else 8
            if length > field.max_length:
                length = field.max_length
            sample_data = {
                datetime: datetime.now(),
                date: datetime.now().date(),
                time: datetime.now().time(),
                timedelta: timedelta(2),
                int: random.randint(1, 16),
                float: random.random() * 123.0,
                Decimal: Decimal(random.randint(1, 42)),
                bool: True,
                str: "".join(random.choices(ascii_letters, k=length))
            }
            if field.has_vocabulary:
                length = len(field.vocabulary.keys()) - 1
                return field.vocabulary.keys()[random.randint(0, length)]
            if field.has_selection:
                length = len(field.selection) - 1
                return field.selection[random.randint(0, length)]
            if field.is_inherited:
                f = field.metadata_form()
                f.test()
                return f
            if field.datatype == "str" and field.min_length > 0:
                return "X" * field.min_length
            if field.datatype == "str" and field.max_length < 4096:
                return "X" * (field.max_length - 1)
            return sample_data[field.datatype]

        for field in self.fields():
            values = []
            if field.min_count > 1:
                for _ in range(field.min_count):
                    values.append(generate_value(field))
            else:
                values.append(generate_value(field))
            field.values = values

    def serialize(self, path: str) -> dict:
        """
        Prepares and validates metadata for sending to Coscine.
        Requires the file path of the file in Coscine as an argument.

        Parameters
        ----------
        path
            The path in Coscine to the FileObject that you would like
            to attach metadata to.
        """
        return {
            "path": path,
            "definition": {
                "content": self.graph().serialize(format="ttl"),
                "type": "text/turtle"
            }
        }

    def _parse_items(self, items: list[dict]) -> None:
        # Select the smallest lexicographic blank node guid
        active_root = min([i["root"] for i in items])
        for item in items:
            path: str = item["path"]
            value: str = item["value"]
            root: str = item["root"]
            if root == active_root:
                field = self.path(path)
                if field.is_inherited:
                    form = field.metadata_form()
                    subitems = list(filter(lambda e: e["root"] == value, items))
                    form._parse_items(subitems)
                    field.append(form)
                else:
                    field.append(value, True)

    def parse(self, data: FileMetadata) -> None:
        """
        Parses existing metadata that was received from Coscine.
        """
        self.clear()
        self._parse_items(data.items())
