# Coscine Python SDK
![python-logo] ![coscine-logo]  

[Coscine](https://coscine.de), short for **Co**llaborative **Sc**ientific
**In**tegration **E**nvironment, is a platform for Research Data Management.
The Coscine Python SDK is an open source package that provides
a high-level interface to the Coscine REST API. It enables you
to automate research workflows and offers the usual functionality
available in the Coscine web interface to python programmers.

## Showcase
Uploading a file to a resource:  
```python
import coscine
from datetime import datetime

token = "My Coscine API token"
client = coscine.ApiClient(token)
project = client.project("My Project")
resource = project.resource("My Resource")
form = resource.metadata_form()
form["Author"] = "Dr. Akula"
form["Created"] = datetime.now()
form["DAP"] = 3.12
with open("file.csv", "r") as fp:
    resource.upload("file.csv", fp, form)
```

## Documentation
Installation instructions and an in-depth guide on using the Python SDK can
be found in the online [documentation]. The source code itself has been
heavily annotated with numpy-style DOCstrings. You can generate a local
copy of the documentation using Sphinx:  

```bash
py -m pip install -U requirements.txt
cd docs
set SPHINXBUILD=py -m sphinx.cmd.build
py -m sphinx.ext.apidoc -o . ../src/coscine
make html
```

## Contributing
To report bugs, request features or resolve questions open an issue inside
of the current git repository. Contributions and any help on improving this
package are appreciated. To contribute source code you may fork
the repository and open a merge request or simply submit a short
and relevant snippet or fix inside of an issue.
This package is currently not actively maintained. Merge requests providing
bug fixes or new features will be merged after a short review.  
Critical bug fixes will be taken care of. But this package is not affiliated
with the Coscine development team and entirely maintained
by the open source community.
Therefore, if you want to see a change, be the first to implement
it or provide a description of your proposal and ask nicely if somebody else
can implement it for you.

## License
This project is Open Source Software and licensed under the terms of
the [MIT License].

[coscine-logo]: https://git.rwth-aachen.de/coscine/community-features/coscine-python-sdk/-/raw/master/docs/_static/coscine_logo_rgb.png
[python-logo]: https://git.rwth-aachen.de/coscine/community-features/coscine-python-sdk/-/raw/master/docs/_static/python-powered-w-200x80.png
[documentation]: https://coscine.pages.rwth-aachen.de/community-features/coscine-python-sdk/
[MIT License]: https://git.rwth-aachen.de/coscine/community-features/coscine-python-sdk/-/blob/master/LICENSE.txt
