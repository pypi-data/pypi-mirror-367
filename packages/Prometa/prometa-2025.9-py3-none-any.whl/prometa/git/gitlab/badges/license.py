#!/usr/bin/env python3
"""
Project license.
"""

from .base import BadgeManager
from .common import get_badge_url


class LicenseBadgeManager(BadgeManager):
    """
    The project's license name, as recognized by `SPDX`_.

    .. _SPDX: https://spdx.org/licenses/
    """

    NAME = "License"

    @property
    def enabled(self):
        """
        The project has a recognized license.
        """
        return self.project.spdx_license is not None

    @property
    def urls(self):
        lic = self.project.spdx_license
        link_url = f"https://spdx.org/licenses/{lic}.html"
        image_url = get_badge_url("license", lic, "9400d3")
        return link_url, image_url


LicenseBadgeManager.register(LicenseBadgeManager.NAME)
