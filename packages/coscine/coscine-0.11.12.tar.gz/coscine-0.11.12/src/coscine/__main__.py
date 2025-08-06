"""
A basic executable interface to Coscine.

The program offers a set of actions that apply to the current selection
of Coscine project, resource and/or files.
Example:
    >>> coscine list
    This will list all projects of the Coscine user.

    >>> coscine list -p "My Coscine Project"
    This will list all resources inside the project "My Coscine Project".

    >>> coscine list -p "My Coscine Project" -r "My Coscine Resource"
    This will list all files inside the resource "My Coscine Resource"
    in the Coscine project "My Coscine Project".

    >>> coscine download -p "My Coscine Project"
    This will download the project "My Coscine Project".

    >>> coscine download -p "Project" -r "Resource" -f "File path"
    This will download the file "File path".
"""

import argparse
import coscine
import logging
from os import getenv
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
argument_parser = argparse.ArgumentParser("coscine", description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
# Positional arguments
ACTIONS = [
    "delete",
    "download",
    "list",
    "upload",
    "update"
]
argument_parser.add_argument("action", choices=ACTIONS)
# Optional arguments
argument_parser.add_argument("-v", "--version", action="version", version=coscine.ApiClient.BANNER)
argument_parser.add_argument("-e", "--endpoint", type=str, help="Set the Coscine API base url", default="https://coscine.rwth-aachen.de")
argument_parser.add_argument("-p", "--project", type=str, help="Coscine project display name")
argument_parser.add_argument("-r", "--resource", type=str, help="Coscine resource display name")
argument_parser.add_argument("-f", "--file", type=str, help="Coscine file path")
argument_parser.add_argument("-t", "--token", type=str, help="Coscine API token")
args = argument_parser.parse_args()
token = args.token if args.token else getenv("COSCINE_API_TOKEN")
if token is None:
    raise RuntimeError(
        "Specify a coscine API token via the command-line argument -t, "
        "--token or via the environment variable COSCINE_API_TOKEN!"
        " For more information visit https://docs.coscine.de/en/token/."
    )
client = coscine.ApiClient(token, base_url=args.endpoint)
if client.version != client.latest_version():
    logging.warning(
        f"Using version {client.version} of the Coscine Python SDK, but "
        f"a newer version {client.latest_version()} is available on PyPi! "
        "Consider updating the Coscine Python SDK via `pip install -U coscine` "
        "or `conda update coscine`."
    )
project  = client.project(args.project)     if args.project else None
resource = project.resource(args.resource)  if args.resource else None
if args.action not in ("upload", "update"):
    file = resource.file(args.file)         if args.file else None
else:
    file = str(args.file) if args.file else None


def action_delete():
    """
    Deletes Coscine projects or resources or files.
    """
    if not project:
        raise RuntimeError("Action 'delete' requires at least a project name!")
    elif not resource:
        if input(f"Delete Coscine project '{project.name}' (Y/N)? ").upper() == "Y":
            project.delete()
            print(f"Project {project.name} deleted!")
        else:
            print("Delete aborted!")
    elif not file:
        if input(f"Delete Coscine resource '{resource.name}' (Y/N)? ").upper() == "Y":
            resource.delete()
            print(f"Resource {resource.name} deleted!")
        else:
            print("Delete aborted!")
    else:
        if input(f"Delete Coscine file '{file.path}' (Y/N)? ").upper() == "Y":
            file.delete()
            print(f"File {file.path} deleted!")
        else:
            print("Delete aborted!")

def action_download():
    """
    Downloads Coscine projects or resources or files.
    """
    if not project:
        raise RuntimeError("Action 'download' requires at least a project name!")
    elif not resource:
        project.download()
    elif not file:
        resource.download()
    else:
        file.download()


def action_list():
    """
    Lists Coscine projects or resources or files.
    """
    if not project:
        for index, item in enumerate(client.projects()):
            print(f"Project [{index}]")
            print(f"  name: {item.name}")
            print(f"  display_name: {item.display_name}")
            print(f"  description: {(item.description[:75] + '...') if len(item.description) > 75 else item.description}")
    elif not resource:
        for index, item in enumerate(project.resources()):
            print(f"Resource [{index}]")
            print(f"  name: {item.name}")
            print(f"  display_name: {item.display_name}")
            print(f"  description: {(item.description[:75] + '...') if len(item.description) > 75 else item.description}")
    else:
        for index, item in enumerate(resource.files()):
            print(f"File [{index}] {item.path}")


def action_upload():
    """
    Uploads files to a Coscine resource. This will overwrite existing files.
    """
    if not (project and resource):
        raise RuntimeError("Action 'upload' requires a project and a resource name!")
    metadata = resource.metadata_form()
    print(
        "Because entering metadata from the command line is really annoying, "
        "required fields are automatically filled with garbage values. "
        "You can edit the metadata after the upload in the Coscine web interface "
        "or via a python script."
    )
    #print("To upload the file you must specify its metadata according to the resource metadata profile.")
    #print("You can leave non-required fields empty by just pressing Enter/Return.")
    #print("Required fields are marked with an asterisk, e.g. 'Field*' instead of 'Field'.")
    metadata.test()
    #for field in metadata.fields():
    #    field_name = field.name if not field.is_required else field.name + "*"
    #    if field.has_vocabulary:
    #        key = input(f"{field_name}: ")
    #        if key:
    #            value = field.vocabulary(key)
    #            metadata[field.name] = value
    #    elif field.has_selection:
    #        key = input(f"{field_name}: ")
    #        if key:
    #            value = field.selection(key)
    #            metadata[field.name] = value
    #    elif field.datatype == str:
    #        value = input(f"{field_name}: ")
    #        if value:
    #            metadata[field.name] = value
    #    elif field.datatype == int:
    #        value = input(f"{field_name}: ")
    #        if value:
    #            metadata[field.name] = int(value)
    #    elif field.datatype == float:
    #        value = input(f"{field_name}: ")
    #        if value:
    #            metadata[field.name] = float(value)
    #    elif field.datatype == datetime.date:
    #        value = input(f"{field_name}: ")
    #        if value:
    #            metadata[field.name] = datetime.strptime(value, r"%Y-%m-%d").date()
    with open(file, "rb") as fp:
        resource.upload(Path(file).name, fp, metadata, overwrite=True)


def action_update():
    with open(file, "rb") as fp:
        resource._upload_blob(Path(file).name, fp, use_put=True)


if args.action == "delete":
    action_delete()
if args.action == "download":
    action_download()
elif args.action == "list":
    action_list()
elif args.action == "upload":
    action_upload()
elif args.action == "update":
    action_update()
