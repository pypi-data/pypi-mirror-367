"""Models for API tokens."""

from __future__ import annotations

from typing import ClassVar

from django.db import models
from django.utils.translation import gettext_lazy as _
from djblets.webapi.models import BaseWebAPIToken

from reviewboard.site.models import LocalSite
from reviewboard.webapi.managers import WebAPITokenManager


class WebAPIToken(BaseWebAPIToken):
    """An access token used for authenticating with the API.

    Each token can be used to authenticate the token's owner with the API,
    without requiring a username or password to be provided. Tokens can
    be revoked, and new tokens added.

    Tokens can store policy information, which will later be used for
    restricting access to the API.
    """

    local_site = models.ForeignKey(LocalSite,
                                   on_delete=models.CASCADE,
                                   related_name='webapi_tokens',
                                   blank=True, null=True)

    objects: ClassVar[WebAPITokenManager] = WebAPITokenManager()

    @classmethod
    def get_root_resource(cls):
        from reviewboard.webapi.resources import resources

        return resources.root

    class Meta:
        db_table = 'webapi_webapitoken'
        verbose_name = _('Web API Token')
        verbose_name_plural = _('Web API Tokens')
