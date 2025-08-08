#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Third party imports
from pkg_resources import get_distribution

# Project imports
from magma_auth.auth import Auth, AuthExternal
from magma_auth.utils import validate_token

__version__ = get_distribution("magma-auth").version
__author__ = "Martanto"
__author_email__ = "martanto@live.com"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2025, MAGMA Indonesia"
__url__ = "https://github.com/martanto/magma-auth"

auth = Auth()
auth_external = AuthExternal()

__all__ = [
    "__version__",
    "__author__",
    "__author_email__",
    "__license__",
    "__copyright__",
    "auth",
    "auth_external",
    "validate_token",
]
