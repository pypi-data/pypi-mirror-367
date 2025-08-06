"""Views used to render e-mail previews."""

from typing import Any, Dict, Union

from django.http import HttpResponse
from django.views.generic.base import View

from reviewboard.notifications.email.decorators import preview_email


class BasePreviewEmailView(View):
    """Generic view used to preview rendered e-mails.

    This is a convenience for class-based views that wraps the
    :py:class:`@preview_email
    <reviewboard.notifications.email.decorators.preview_email>` decorator.
    """

    #: The function that will build the e-mail.
    #:
    #: This must be a class method or, if using an existing top-level function,
    #: :js:class:`staticmethod` must be used.
    build_email = None

    def get(
        self,
        *args,
        **kwargs,
    ) -> HttpResponse:
        """Handle a HTTP GET request.

        The request will render the e-mail.

        Args:
            *args (tuple):
                Positional arguments passed to the handler.

            **kwargs (dict):
                Keyword arguments passed to the handler.

        Returns:
            django.http.HttpResponse:
            The resulting HTTP response from the handler.
        """
        return preview_email(self.build_email)(self.get_email_data)(*args,
                                                                    **kwargs)

    def get_email_data(
        self,
        *args,
        **kwargs,
    ) -> Union[Dict[str, Any], HttpResponse]:
        """Return data used for the e-mail builder.

        The data returned will be passed to :py:attr:`build_email` to handle
        rendering the e-mail.

        This can also return a :py:class:`~django.http.HttpResponse`, which
        is useful for returning errors.

        Args:
            *args (tuple):
                Positional arguments passed to the handler.

            **kwargs (dict):
                Keyword arguments passed to the handler.

        Returns:
            object:
            The dictionary data to pass as keyword arguments to
            :py:attr:`build_email`, or an instance of
            :py:class:`~django.http.HttpResponse` to immediately return to
            the client.
        """
        return {}
