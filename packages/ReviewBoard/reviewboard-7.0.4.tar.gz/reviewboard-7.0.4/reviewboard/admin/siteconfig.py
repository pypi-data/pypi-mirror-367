"""Loads and manages site configuration settings."""

from __future__ import annotations

import logging
import os
import re
from typing import Optional, cast

from django.conf import settings, global_settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage, storages
from django.utils.functional import empty
from djblets.log import restart_logging, siteconfig as log_siteconfig
from djblets.recaptcha import siteconfig as recaptcha_siteconfig
from djblets.siteconfig.django_settings import (apply_django_settings,
                                                get_django_defaults,
                                                get_django_settings_map)
from djblets.siteconfig.models import SiteConfiguration
from djblets.webapi.auth.backends import reset_auth_backends
from haystack import connections as haystack_connections

from reviewboard.accounts.backends import auth_backends
from reviewboard.accounts.privacy import recompute_privacy_consents
from reviewboard.accounts.sso.backends import sso_backends
from reviewboard.avatars import avatar_services
from reviewboard.diffviewer.settings import DiffSettings
from reviewboard.oauth.features import oauth2_service_feature
from reviewboard.notifications.email.message import EmailMessage
from reviewboard.search.search_backends.whoosh import WhooshBackend
from reviewboard.signals import site_settings_loaded


# A mapping of our supported storage backend names to backend class paths.
storage_backend_map = {
    'builtin': 'django.core.files.storage.FileSystemStorage',
    's3':      'storages.backends.s3.S3Storage',
    'swift':   'swift.storage.SwiftStorage',
}


log_settings_map = log_siteconfig.settings_map
log_settings_defaults = log_siteconfig.defaults


# A mapping of siteconfig setting names to Django settings.py names.
# This also contains all the djblets-provided mappings as well.
settings_map = {
    'auth_digest_file_location':       'DIGEST_FILE_LOCATION',
    'auth_digest_realm':               'DIGEST_REALM',
    'auth_ldap_anon_bind_uid':         'LDAP_ANON_BIND_UID',
    'auth_ldap_anon_bind_passwd':      'LDAP_ANON_BIND_PASSWD',
    'auth_ldap_given_name_attribute':  'LDAP_GIVEN_NAME_ATTRIBUTE',
    'auth_ldap_surname_attribute':     'LDAP_SURNAME_ATTRIBUTE',
    'auth_ldap_full_name_attribute':   'LDAP_FULL_NAME_ATTRIBUTE',
    'auth_ldap_email_domain':          'LDAP_EMAIL_DOMAIN',
    'auth_ldap_email_attribute':       'LDAP_EMAIL_ATTRIBUTE',
    'auth_ldap_tls':                   'LDAP_TLS',
    'auth_ldap_base_dn':               'LDAP_BASE_DN',
    'auth_ldap_uid':                   'LDAP_UID',
    'auth_ldap_uid_mask':              'LDAP_UID_MASK',
    'auth_ldap_uri':                   'LDAP_URI',
    'auth_ad_domain_name':             'AD_DOMAIN_NAME',
    'auth_ad_use_tls':                 'AD_USE_TLS',
    'auth_ad_find_dc_from_dns':        'AD_FIND_DC_FROM_DNS',
    'auth_ad_domain_controller':       'AD_DOMAIN_CONTROLLER',
    'auth_ad_ou_name':                 'AD_OU_NAME',
    'auth_ad_group_name':              'AD_GROUP_NAME',
    'auth_ad_search_root':             'AD_SEARCH_ROOT',
    'auth_ad_recursion_depth':         'AD_RECURSION_DEPTH',
    'auth_x509_username_field':        'X509_USERNAME_FIELD',
    'auth_x509_custom_username_field': 'X509_CUSTOM_USERNAME_FIELD',
    'auth_x509_username_regex':        'X509_USERNAME_REGEX',
    'auth_x509_autocreate_users':      'X509_AUTOCREATE_USERS',
    'auth_nis_email_domain':           'NIS_EMAIL_DOMAIN',
    'site_domain_method':              'DOMAIN_METHOD',
}
settings_map.update(get_django_settings_map())
settings_map.update(log_settings_map)
settings_map.update(recaptcha_siteconfig.settings_map)

# Settings for django-storages
settings_map.update({
    'aws_access_key_id':       'AWS_ACCESS_KEY_ID',
    'aws_secret_access_key':   'AWS_SECRET_ACCESS_KEY',
    'aws_headers':             'AWS_HEADERS',
    'aws_calling_format':      'AWS_CALLING_FORMAT',
    'aws_default_acl':         'AWS_DEFAULT_ACL',
    'aws_querystring_auth':    'AWS_QUERYSTRING_AUTH',
    'aws_querystring_active':  'AWS_QUERYSTRING_ACTIVE',
    'aws_querystring_expire':  'AWS_QUERYSTRING_EXPIRE',
    'aws_s3_secure_urls':      'AWS_S3_SECURE_URLS',
    'aws_s3_bucket_name':      'AWS_STORAGE_BUCKET_NAME',
    'swift_auth_url':          'SWIFT_AUTH_URL',
    'swift_username':          'SWIFT_USERNAME',
    'swift_key':               'SWIFT_KEY',
    'swift_auth_version':      'SWIFT_AUTH_VERSION',
    'swift_container_name':    'SWIFT_CONTAINER_NAME',
    'couchdb_default_server':  'COUCHDB_DEFAULT_SERVER',
    'couchdb_storage_options': 'COUCHDB_STORAGE_OPTIONS',
})


# All the default values for settings.
defaults = get_django_defaults()
defaults.update(log_settings_defaults)
defaults.update(recaptcha_siteconfig.defaults)
defaults.update(avatar_services.get_siteconfig_defaults())
defaults.update({
    'auth_ldap_anon_bind_uid': '',
    'auth_ldap_anon_bind_passwd': '',
    'auth_ldap_email_domain': '',
    'auth_ldap_tls': False,
    'auth_ldap_uid': 'uid',
    'auth_ldap_uid_mask': '',
    'auth_ldap_uri': '',
    'auth_nis_email_domain': '',
    'auth_registration_show_captcha': False,
    'auth_require_sitewide_login': False,
    'auth_custom_backends': [],
    'auth_enable_registration': True,
    'auth_x509_username_field': 'SSL_CLIENT_S_DN_CN',
    'auth_x509_username_regex': '',
    'auth_x509_autocreate_users': False,
    'code_safety_checkers': {},
    'company': '',
    'default_ui_theme': 'default',
    'default_use_rich_text': True,
    'diffviewer_context_num_lines': 5,
    'diffviewer_default_tab_size': DiffSettings.DEFAULT_TAB_SIZE,
    'diffviewer_include_space_patterns': [],
    'diffviewer_max_binary_size': 10_485_760,
    'diffviewer_max_diff_size': 2_097_152,
    'diffviewer_paginate_by': 20,
    'diffviewer_paginate_orphans': 10,
    'diffviewer_syntax_highlighting': True,
    'diffviewer_syntax_highlighting_threshold': 20_000,
    'diffviewer_custom_pygments_lexers': {'.less': 'LessCss'},
    'diffviewer_show_trailing_whitespace': True,
    'mail_send_review_mail': False,
    'mail_send_new_user_mail': False,
    'mail_send_password_changed_mail': False,
    'mail_enable_autogenerated_header': True,
    'mail_from_spoofing': EmailMessage.FROM_SPOOFING_SMART,
    'search_enable': False,
    'send_support_usage_stats': True,
    'site_domain_method': 'http',
    'site_read_only': False,
    'sso_auto_login_backend': '',
    'client_web_login': True,

    # The number of days in which client API tokens should expire
    # after creation.
    'client_token_expiration': 365,

    'privacy_enable_user_consent': False,
    'privacy_info_html': None,
    'privacy_policy_url': None,
    'terms_of_service_url': None,

    'search_results_per_page': 20,
    'search_backend_id': WhooshBackend.search_backend_id,
    'search_backend_settings': {},
    'search_on_the_fly_indexing': False,

    # Overwrite this.
    'site_media_url': settings.SITE_ROOT + "media/",
})

defaults.update({
    'aws_access_key_id': '',
    'aws_calling_format': 2,
    'aws_default_acl': 'public-read',
    'aws_headers': {},
    'aws_querystring_active': False,
    'aws_querystring_auth': True,
    'aws_querystring_expire': 3600,
    'aws_s3_bucket_name': '',
    'aws_s3_secure_urls': False,
    'aws_secret_access_key': '',
    'couchdb_default_server': '',
    'couchdb_storage_options': {},
    'swift_auth_url': '',
    'swift_auth_version': '1',
    'swift_container_name': '',
    'swift_key': '',
    'swift_username': '',
})


_original_webapi_auth_backends = settings.WEB_API_AUTH_BACKENDS

logger = logging.getLogger(__name__)


def load_site_config(
    full_reload: bool = False,
) -> Optional[SiteConfiguration]:
    """Load stored site configuration settings.

    This populates the Django settings object with any keys that need to be
    there.

    Args:
        full_reload (bool, optional):
            Whether to perform a full reload. This would bypass some
            settings comparisons where necessary.

    Returns:
        djblets.siteconfig.models.SiteConfiguration:
        The loaded site configuration, if any.
    """
    global _original_webapi_auth_backends

    def apply_setting(settings_key, db_key, default=None):
        """Apply the given siteconfig value to the Django settings object."""
        db_value = siteconfig.settings.get(db_key)

        if db_value:
            setattr(settings, settings_key, db_value)
        elif default:
            setattr(settings, settings_key, default)

    # If siteconfig needs to be saved back to the DB, set dirty=true
    dirty = False
    try:
        siteconfig = SiteConfiguration.objects.get_current()
    except SiteConfiguration.DoesNotExist:
        raise ImproperlyConfigured(
            "The site configuration entry does not exist in the database. "
            "You will need to re-create or upgrade your database.")
    except Exception as e:
        # We got something else. Likely, this doesn't exist yet and we're
        # doing a syncdb or something, so silently ignore.
        logger.error('Could not load siteconfig: %s' % e)
        return None

    # Store some original state needed to check logging later.
    old_logging_settings = {
        key: getattr(settings, log_settings_map[key], default)
        for key, default in log_settings_defaults.items()
    }

    # Populate defaults if they weren't already set.
    if not siteconfig.get_defaults():
        # We don't actually access the sso_backends registry until we're here,
        # because otherwise we might hit circular imports while building up URL
        # patterns.
        defaults.update(sso_backends.get_siteconfig_defaults())
        siteconfig.add_defaults(defaults)

    # The default value for DEFAULT_EMAIL_FROM (webmaster@localhost)
    # is less than good, so use a better one if it's set to that or if
    # we haven't yet set this value in siteconfig.
    mail_default_from = \
        siteconfig.settings.get('mail_default_from',
                                global_settings.DEFAULT_FROM_EMAIL)

    if (not mail_default_from or
            mail_default_from == global_settings.DEFAULT_FROM_EMAIL):
        domain = siteconfig.site.domain.split(':')[0]
        siteconfig.set('mail_default_from', 'noreply@' + domain)

    # STATIC_* and MEDIA_* must be different paths, and differ in meaning.
    # If site_static_* is empty or equal to media_static_*, we're probably
    # migrating from an earlier Review Board install.
    site_static_root = siteconfig.settings.get('site_static_root', '')
    site_media_root = siteconfig.settings.get('site_media_root')

    if site_static_root == '' or site_static_root == site_media_root:
        siteconfig.set('site_static_root', settings.STATIC_ROOT)

    site_static_url = siteconfig.settings.get('site_static_url', '')
    site_media_url = siteconfig.settings.get('site_media_url')

    if site_static_url == '' or site_static_url == site_media_url:
        siteconfig.set('site_static_url', settings.STATIC_URL)

    # Populate the settings object with anything relevant from the siteconfig.
    apply_django_settings(siteconfig, settings_map)

    # Check if we need to reload logging.
    if getattr(settings, 'RUNNING_TEST', False):
        # Never reload if running unit tests.
        logging_dirty = False
    elif full_reload:
        # Force a full reload of logging.
        logging_dirty = True
    else:
        # Check if any logging settings have changed. If so, reload logging.
        logging_dirty = any(
            siteconfig.get(key) != old_logging_settings[key]
            for key, default in log_settings_defaults.items()
        )

    if logging_dirty:
        # Logging may have changed, so restart logging.
        restart_logging()

    # Now for some more complicated stuff...
    haystack_connections['default'].reset_forwarding()

    # Site administrator settings
    apply_setting("ADMINS", None, (
        (siteconfig.get("site_admin_name", ""),
         siteconfig.get("site_admin_email", "")),
    ))

    apply_setting("MANAGERS", None, settings.ADMINS)

    # Explicitly base this off the STATIC_URL
    apply_setting("ADMIN_MEDIA_PREFIX", None, settings.STATIC_URL + "admin/")

    # Set the auth backends
    auth_backend_id = siteconfig.settings.get("auth_backend", "builtin")
    builtin_backend_obj = auth_backends.get('backend_id', 'builtin')
    builtin_backend = "%s.%s" % (builtin_backend_obj.__module__,
                                 builtin_backend_obj.__name__)

    if auth_backend_id == "custom":
        custom_backends = siteconfig.settings.get("auth_custom_backends")

        if isinstance(custom_backends, str):
            custom_backends = (custom_backends,)
        elif isinstance(custom_backends, list):
            custom_backends = tuple(custom_backends)

        settings.AUTHENTICATION_BACKENDS = custom_backends

        if builtin_backend not in custom_backends:
            settings.AUTHENTICATION_BACKENDS += (builtin_backend,)
    else:
        backend = auth_backends.get('backend_id', auth_backend_id)

        if backend and backend is not builtin_backend_obj:
            settings.AUTHENTICATION_BACKENDS = \
                ("%s.%s" % (backend.__module__, backend.__name__),
                 builtin_backend)
        else:
            settings.AUTHENTICATION_BACKENDS = (builtin_backend,)

        # If we're upgrading from a 1.x LDAP configuration, populate
        # ldap_uid and clear ldap_uid_mask
        if auth_backend_id == "ldap":
            if not hasattr(settings, 'LDAP_UID'):
                if hasattr(settings, 'LDAP_UID_MASK'):
                    # Get the username attribute from the old UID mask
                    # LDAP attributes can contain only alphanumeric
                    # characters and the hyphen and must lead with an
                    # alphabetic character. This is not dependent upon
                    # locale.
                    m = re.search("([a-zA-Z][a-zA-Z0-9-]+)=%s",
                                  settings.LDAP_UID_MASK)
                    if m:
                        # Assign LDAP_UID the value of the retrieved attribute
                        settings.LDAP_UID = m.group(1)
                    else:
                        # Couldn't match the old value?
                        # This should be impossible, but in this case, let's
                        # just guess a sane default and hope for the best.
                        settings.LDAP_UID = 'uid'

                else:
                    # Neither the old nor new value?
                    # This should be impossible, but in this case, let's just
                    # guess a sane default and hope for the best.
                    settings.LDAP_UID = 'uid'

                # Remove the LDAP_UID_MASK value
                settings.LDAP_UID_MASK = None

                siteconfig.set('auth_ldap_uid', settings.LDAP_UID)
                siteconfig.set('auth_ldap_uid_mask', settings.LDAP_UID_MASK)
                # Set the dirty flag so we save this back
                dirty = True

    # Add APITokenBackend to the list of auth backends. This one is always
    # present, and is used only for API requests.
    settings.AUTHENTICATION_BACKENDS += (
        'reviewboard.webapi.auth_backends.TokenAuthBackend',
    )

    # Reset the WebAPI auth backends in case OAuth2 has become disabled.
    settings.WEB_API_AUTH_BACKENDS = _original_webapi_auth_backends
    reset_auth_backends()

    if oauth2_service_feature.is_enabled():
        settings.AUTHENTICATION_BACKENDS += (
            'reviewboard.webapi.auth_backends.OAuth2TokenAuthBackend',
        )

        settings.WEB_API_AUTH_BACKENDS += (
            'djblets.webapi.auth.backends.oauth2_tokens'
            '.WebAPIOAuth2TokenAuthBackend',
        )

    _load_storage_settings(siteconfig)

    is_https = (
        siteconfig.settings.get('site_domain_method', 'http') == 'https'
    )

    settings.CSRF_COOKIE_SECURE = is_https
    settings.SESSION_COOKIE_SECURE = is_https

    if is_https:
        os.environ[str('HTTPS')] = str('on')
    else:
        os.environ[str('HTTPS')] = str('off')

    # Migrate over any legacy avatar backend settings.
    if avatar_services.migrate_settings(siteconfig):
        dirty = True

    # Save back changes if they have been made
    if dirty:
        siteconfig.save()

    # Reload privacy consent requirements
    recompute_privacy_consents()

    site_settings_loaded.send(sender=None)

    return siteconfig


def _load_storage_settings(
    siteconfig: SiteConfiguration,
) -> None:
    """Load settings for the storage backend.

    This will configure Django's STORAGES and the django-storage library
    for any storage settings configured for Review Board.

    Version Added:
        7.0

    Args:
        siteconfig (djblets.siteconfig.models.SiteConfiguration):
            The Site Configuration to load from.
    """
    # Set the storage backend
    settings.STORAGES['default'] = {
        'BACKEND': storage_backend_map.get(
            siteconfig.settings.get('storage_backend', 'builtin'),
            'builtin'),
    }

    # Load the S3 storage information.
    #
    # Note that these blow up if they're not the perfectly right types
    settings.AWS_QUERYSTRING_AUTH = siteconfig.get('aws_querystring_auth')
    settings.AWS_ACCESS_KEY_ID = str(
        siteconfig.get('aws_access_key_id'))
    settings.AWS_SECRET_ACCESS_KEY = str(
        siteconfig.get('aws_secret_access_key'))
    settings.AWS_STORAGE_BUCKET_NAME = str(
        siteconfig.get('aws_s3_bucket_name'))

    # The following converts the legacy django-storages Calling Format IDs
    # to modern Addressing Style strings.
    try:
        aws_calling_format = int(
            cast(int, siteconfig.get('aws_calling_format')))
    except ValueError:
        aws_calling_format = 0

    if aws_calling_format == 1:
        # Path
        settings.AWS_S3_ADDRESSING_STYLE = 'path'
    elif aws_calling_format == 2:
        # Subdomain
        settings.AWS_S3_ADDRESSING_STYLE = 'virtual'
    elif aws_calling_format == 3:
        # Vanity.
        #
        # We never fully supported this outside of adding custom settings
        # to settings_local.py. There isn't a direct equivalent anymore.
        # We'll go with the default of None.
        settings.AWS_S3_ADDRESSING_STYLE = None

    # Load the Swift storage information.
    settings.SWIFT_AUTH_URL = str(
        siteconfig.get('swift_auth_url'))
    settings.SWIFT_USERNAME = str(
        siteconfig.get('swift_username'))
    settings.SWIFT_KEY = str(
        siteconfig.get('swift_key'))

    try:
        settings.SWIFT_AUTH_VERSION = int(
            cast(int, siteconfig.get('swift_auth_version')))
    except ValueError:
        settings.SWIFT_AUTH_VERSION = 1

    settings.SWIFT_CONTAINER_NAME = str(
        siteconfig.get('swift_container_name'))

    # Reset the storage settings cache.
    #
    # Note that this is the same logic performed in django.test.signals.
    # Unfortunately, Django doesn't offer official API for clearing this.
    try:
        del storages.backends
    except AttributeError:
        pass

    storages._backends = None
    storages._storages = {}
    default_storage._wrapped = empty
