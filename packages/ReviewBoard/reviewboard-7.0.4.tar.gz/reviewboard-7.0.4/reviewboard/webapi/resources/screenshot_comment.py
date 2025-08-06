from djblets.util.decorators import augment_method_from

from reviewboard.webapi.resources.base_screenshot_comment import \
    BaseScreenshotCommentResource


class ScreenshotCommentResource(BaseScreenshotCommentResource):
    """Provides information on screenshots comments made on a review request.

    The list of comments cannot be modified from this resource. It's meant
    purely as a way to see existing comments that were made on a screenshot.
    These comments will span all public reviews.
    """
    uri_template_name = None
    uri_template_name_plural = 'screenshot_comments'

    model_parent_key = 'screenshot'
    uri_object_key = None

    def get_queryset(self, request, screenshot_id, *args, **kwargs):
        q = super(ScreenshotCommentResource, self).get_queryset(
            request, *args, **kwargs)
        q = q.filter(screenshot=screenshot_id)
        return q

    @augment_method_from(BaseScreenshotCommentResource)
    def get_list(self, *args, **kwargs):
        """Returns the list of screenshot comments on a screenshot.

        This list of comments will cover all comments made on this
        screenshot from all reviews.
        """
        pass


screenshot_comment_resource = ScreenshotCommentResource()
