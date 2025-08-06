"""HTTP Digest authentication backend."""

from __future__ import annotations

import hashlib
import logging
from typing import Optional, TYPE_CHECKING

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from reviewboard.accounts.backends.base import BaseAuthBackend
from reviewboard.accounts.forms.auth import HTTPBasicSettingsForm

if TYPE_CHECKING:
    from django.http import HttpRequest


logger = logging.getLogger(__name__)


class HTTPDigestBackend(BaseAuthBackend):
    """Authenticate against a user in a digest password file.

    This is controlled by the following Django settings:

    .. setting:: DIGEST_FILE_LOCATION

    ``DIGEST_FILE_LOCATION``:
        The local file path on the server containing an HTTP password
        (:file:`htpasswd`) file.

        This is ``auth_digest_file_location`` in the site configuration.


    .. setting:: DIGEST_REALM

    ``DIGEST_REALM``:
        The HTTP realm users will be authenticated into.

        This is ``auth_digest_realm`` in the site configuration.
    """

    backend_id = 'digest'
    name = _('HTTP Digest Authentication')
    settings_form = HTTPBasicSettingsForm
    login_instructions = _('Use your standard username and password.')

    def authenticate(
        self,
        request: Optional[HttpRequest] = None,
        *,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs,
    ) -> Optional[User]:
        """Authenticate a user against the HTTP password file.

        This will attempt to authenticate the user against the digest password
        file. If the username and password are valid, a user will be returned,
        and added to the database if it doesn't already exist.

        Version Changed:
            6.0:
            * ``request`` is now optional.
            * ``username`` and ``password`` are technically optional, to
              aid in consistency for type hints, but will result in a ``None``
              result.

        Version Changed:
            4.0:
            The ``request`` argument is now mandatory as the first positional
            argument, as per requirements in Django.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the caller. This may be ``None``.

            username (str):
                The username to authenticate.

            password (str):
                The user's password.

            **kwargs (dict, unused):
                Additional keyword arguments passed by the caller.

        Returns:
            django.contrib.auth.models.User:
            The authenticated user, or ``None`` if the user could not be
            authenticated for any reason.
        """
        if not username or not password:
            # This may be an authentication request for a backend expecting
            # different arguments.
            return None

        username = username.strip()

        filename = settings.DIGEST_FILE_LOCATION
        digest_text = '%s:%s:%s' % (username, settings.DIGEST_REALM, password)
        digest_password = hashlib.md5(digest_text.encode('utf-8')).hexdigest()

        try:
            with open(filename, 'r') as fp:
                for line_no, line in enumerate(fp):
                    try:
                        user, realm, passwd = line.strip().split(':')

                        if user == username and passwd == digest_password:
                            return self.get_or_create_user(username=username,
                                                           request=request)
                    except ValueError as e:
                        logger.exception('Error parsing HTTP Digest password '
                                         'file "%s" at line %d: %s',
                                         filename, line_no, e,
                                         extra={'request': request})
                        break
        except IOError as e:
            logger.exception('Could not open the HTTP Digest password '
                             'file "%s": %s',
                             filename, e,
                             extra={'request': request})

        return None

    def get_or_create_user(
        self,
        username: str,
        request: Optional[HttpRequest] = None,
    ) -> Optional[User]:
        """Return an existing user or create one if it doesn't exist.

        This does not authenticate the user.

        If the user does not exist in the database, but does in the HTTP
        password file, its information will be stored in the database for later
        lookup.

        Args:
            username (str):
                The name of the user to look up or create.

            request (django.http.HttpRequest, unused):
                The HTTP request from the client. This is unused.

        Returns:
            django.contrib.auth.models.User:
            The resulting user, or ``None`` if one could not be found.
        """
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(username=username)

        return user
