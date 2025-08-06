###############################################################################
# Coscine Python SDK
# Copyright (c) 2020-2025 RWTH Aachen University
# Licensed under the terms of the MIT License
# For more information on Coscine visit https://www.coscine.de/.
###############################################################################

"""
The Coscine Python SDK ships with its own set of exceptions.
All exceptions raised by the Coscine Python SDK are derived from
a common base exception class called "CoscineException".
"""


class CoscineException(Exception):
    """
    Coscine Python SDK base exception.
    Inherited by all other Coscine Python SDK exceptions.
    """


class AuthenticationError(CoscineException):
    """
    Failed to authenticate with the API token supplied by the user.
    """


class TooManyResults(CoscineException):
    """
    Two or more instances match the property provided by the user but
    the Coscine Python SDK expected just a single instance to match.
    """


class NotFoundError(CoscineException):
    """
    The droids you were looking for have not been found.
    Move along!
    """


class RequestRejected(CoscineException):
    """
    The request has reached the Coscine servers but has
    been rejected for whatever reason there may be. This
    exception is most likely thrown in case of ill-formatted
    requests.
    """
