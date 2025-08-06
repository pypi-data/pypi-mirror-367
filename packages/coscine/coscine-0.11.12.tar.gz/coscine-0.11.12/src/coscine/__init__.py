###############################################################################
# Coscine Python SDK
# Copyright (c) 2020-2025 RWTH Aachen University
# Licensed under the terms of the MIT License
# For more information on Coscine visit https://www.coscine.de/.
###############################################################################

"""
The Coscine Python SDK provides a high-level interface
to the Coscine REST API.
"""

import logging
from coscine.__about__ import *
from coscine.exceptions import *
from coscine.client import *
from coscine.common import *
from coscine.metadata import *
from coscine.project import *
from coscine.resource import *

# Set up logging to /dev/null like a library is supposed to.
# This ensures that if no logger was configured, all the logging
# calls made by this library do not yield any output.
logging.getLogger(__name__).addHandler(logging.NullHandler())
