"""Base class for general comment resources."""

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.timesince import timesince
from djblets.util.decorators import augment_method_from

from reviewboard.reviews.features import general_comments_feature
from reviewboard.reviews.models import GeneralComment
from reviewboard.webapi.base import WebAPIResource
from reviewboard.webapi.resources import resources
from reviewboard.webapi.resources.base_comment import BaseCommentResource


class BaseReviewGeneralCommentResource(BaseCommentResource):
    """Base class for general comment resources.

    Provides common fields and functionality for all general comment resources.
    The list of comments cannot be modified from this resource.
    """
    model = GeneralComment
    name = 'general_comment'

    model_parent_key = 'review_request'
    uri_object_key = 'comment_id'

    allowed_methods = ('GET',)

    required_features = [
        general_comments_feature,
    ]

    def get_queryset(self, request, review_request_id=None, *args, **kwargs):
        """Return a queryset for GeneralComment models.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

            review_request_id (int, optional):
                The review request ID used to filter the results. If set,
                only comments from the given review request that are public
                or owned by the requesting user will be included.

            *args (tuple):
                Additional positional arguments.

            **kwargs (dict):
                Additional keyword arguments.

        Returns:
            django.db.models.query.QuerySet:
            A queryset for GeneralComment models.
        """
        q = Q(review__isnull=False)

        if review_request_id is not None:
            try:
                review_request = resources.review_request.get_object(
                    request, review_request_id=review_request_id,
                    *args, **kwargs)
            except ObjectDoesNotExist:
                raise self.model.DoesNotExist

            q &= Q(review__review_request=review_request)

        return self.model.objects.filter(q)

    def serialize_public_field(self, obj, **kwargs):
        return obj.review.get().public

    def serialize_timesince_field(self, obj, **kwargs):
        return timesince(obj.timestamp)

    def serialize_user_field(self, obj, **kwargs):
        return obj.review.get().user

    @augment_method_from(WebAPIResource)
    def get(self, *args, **kwargs):
        """Returns information on the comment.

        This contains the comment text and the date/time the comment was
        made.
        """
        pass

    @augment_method_from(WebAPIResource)
    def get_list(self, *args, **kwargs):
        """Returns the list of general comments on a review request.

        This list of comments will cover all comments from all reviews
        on this review request.
        """
        pass
