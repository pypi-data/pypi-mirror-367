# pylint: disable=too-few-public-methods
# Copyright 2025 Cisco Systems, Inc. and its affiliates
# SPDX-License-Identifier: Apache-2.0
"""Httpx Auth module for the Identity Service Python SDK."""

import logging

from identityservice.sdk import IdentityServiceSdk as Sdk

import httpx

logger = logging.getLogger("identityservice.auth.httpx")


class IdentityServiceAuth(httpx.Auth):
    """Httpx authentication class for the Identity Service SDK."""

    def __init__(self):
        """Initialize the IdentityServiceAuth class."""
        self.sdk = Sdk()

    def auth_flow(self, request):
        """Add the Authorization header to the request."""
        access_token = self.sdk.access_token()

        logger.debug("Issued new access token for Identity Service SDK")

        request.headers["Authorization"] = f"Bearer {access_token}"
        yield request
