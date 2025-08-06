"""URLs for the reviews app."""

from django.conf import settings
from django.urls import include, path, re_path

from reviewboard.reviews import views


download_diff_urls = [
    path('orig/',
         views.DownloadDiffFileView.as_view(
             file_type=views.DownloadDiffFileView.TYPE_ORIG),
         name='download-orig-file'),

    path('new/',
         views.DownloadDiffFileView.as_view(
             file_type=views.DownloadDiffFileView.TYPE_MODIFIED),
         name='download-modified-file'),
]


diff_fragment_urls = [
    path('', views.ReviewsDiffFragmentView.as_view(),
         name='view-diff-fragment'),

    path('patch-error-bundle/',
         views.ReviewsDownloadPatchErrorBundleView.as_view(),
         name='patch-error-bundle'),
]


diffviewer_revision_urls = [
    path('',
         views.ReviewsDiffViewerView.as_view(),
         name="view-diff-revision"),

    path('raw/',
         views.DownloadRawDiffView.as_view(),
         name='raw-diff-revision'),

    re_path(r'^fragment/(?P<filediff_id>\d+)/(?:chunk/(?P<chunk_index>\d+)/)?',
            include(diff_fragment_urls)),

    path('download/<int:filediff_id>/',
         include(download_diff_urls)),
]


diffviewer_interdiff_urls = [
    path('',
         views.ReviewsDiffViewerView.as_view(),
         name="view-interdiff"),

    re_path(r'^fragment/(?P<filediff_id>\d+)(?:-(?P<interfilediff_id>\d+))?/'
            r'(?:chunk/(?P<chunk_index>\d+)/)?',
            include(diff_fragment_urls)),
]


diffviewer_urls = [
    path('', views.ReviewsDiffViewerView.as_view(), name='view-diff'),

    path('raw/', views.DownloadRawDiffView.as_view(), name='raw-diff'),

    path('<int:revision>/',
         include(diffviewer_revision_urls)),

    path('<int:revision>-<int:interdiff_revision>/',
         include(diffviewer_interdiff_urls)),
]


file_attachment_urls = [
    path('<int:file_attachment_id>/',
         views.ReviewFileAttachmentView.as_view(),
         name='file-attachment'),

    path('<int:file_attachment_diff_id>-<int:file_attachment_id>/',
         views.ReviewFileAttachmentView.as_view(),
         name='file-attachment'),

    path('<int:file_attachment_id>/download/',
         views.DownloadFileAttachmentView.as_view(),
         name='download-file-attachment'),
]


bugs_urls = [
    path('', views.BugURLRedirectView.as_view(), name='bug_url'),
    path('infobox/', views.BugInfoboxView.as_view(), name='bug_infobox'),
]


review_request_urls = [
    # Review request detail
    path('',
         views.ReviewRequestDetailView.as_view(),
         name='review-request-detail'),

    path('_updates/',
         views.ReviewRequestUpdatesView.as_view(),
         name='review-request-updates'),

    # Review request diffs
    path('diff/', include(diffviewer_urls)),

    # Fragments
    re_path(r'^_fragments/diff-comments/(?P<comment_ids>[\d,]+)/$',
            views.CommentDiffFragmentsView.as_view(),
            name='diff-comment-fragments'),

    # File attachments
    path('file/', include(file_attachment_urls)),

    # Screenshots
    path('s/<int:screenshot_id>/',
         views.ReviewScreenshotView.as_view(),
         name='screenshot'),

    # Bugs
    re_path(r'^bugs/(?P<bug_id>[\w\.-]+)/', include(bugs_urls)),

    # Review Request infobox
    path('infobox/',
         views.ReviewRequestInfoboxView.as_view(),
         name='review-request-infobox'),
]


if settings.DEBUG and not settings.PRODUCTION:
    review_request_urls += [
        # E-mail previews
        re_path(r'^preview-email/(?P<message_format>text|html)/$',
                views.PreviewReviewRequestEmailView.as_view(),
                name='preview-review-request-email'),

        re_path(r'^changes/(?P<changedesc_id>\d+)/preview-email/'
                r'(?P<message_format>text|html)/$',
                views.PreviewReviewRequestEmailView.as_view(),
                name='preview-review-request-email'),

        re_path(r'^batch-email/(?P<message_format>text|html)/',
                views.PreviewBatchEmailView.as_view(),
                name='preview-batch-email'),

        re_path(r'^reviews/(?P<review_id>\d+)/preview-email/'
                r'(?P<message_format>text|html)/$',
                views.PreviewReviewEmailView.as_view(),
                name='preview-review-email'),

        re_path(r'^reviews/(?P<review_id>\d+)/replies/(?P<reply_id>\d+)/'
                r'preview-email/(?P<message_format>text|html)/$',
                views.PreviewReplyEmailView.as_view(),
                name='preview-review-reply-email'),
    ]


urlpatterns = [
    path('new/',
         views.NewReviewRequestView.as_view(),
         name='new-review-request'),

    path('_batch/',
         views.BatchOperationView.as_view(),
         name='batch-operation'),

    path('<int:review_request_id>/',
         include(review_request_urls)),
]
