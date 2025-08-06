import datetime
import time

from django.core.cache import cache
from django.contrib.auth.models import User
from django.db.models.aggregates import Count
from django.db.models.signals import post_save, post_delete
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from djblets.cache.backend import cache_memoize
from djblets.registries.registry import (ALREADY_REGISTERED,
                                         ATTRIBUTE_REGISTERED,
                                         DEFAULT_ERRORS,
                                         NOT_REGISTERED,
                                         OrderedRegistry,
                                         UNREGISTER)
from djblets.util.decorators import augment_method_from

from reviewboard import get_manual_url
from reviewboard.admin.cache_stats import get_cache_stats
from reviewboard.changedescs.models import ChangeDescription
from reviewboard.reviews.models import Comment, Group, Review, ReviewRequest
from reviewboard.scmtools.models import Repository


class BaseAdminWidget(object):
    """The base class for an Administration Dashboard widget.

    Widgets appear in the Administration Dashboard and can display useful
    information on the system, links to other pages, or even fetch data
    from external sites.

    There are a number of built-in widgets, but extensions can provide their
    own.

    Version Added::
        4.0:
        Introduced a a replacement for the legacy :py:attr:`Widget` class.
    """

    #: The unique ID of the widget.
    widget_id = None

    #: The name of the widget.
    #:
    #: This will be shown at the top of the widget.
    name = None

    #: The name of the template used to render the widget.
    template_name = 'admin/admin_widget.html'

    #: Additional CSS classes to apply to the widget.
    #:
    #: If set, this must be a string with a space-separated list of CSS
    #: classes.
    css_classes = None

    #: The name of the JavaScript view rendering the widget.
    js_view_class = 'RB.Admin.WidgetView'

    #: The name of the JavaScript model handling widget state.
    js_model_class = 'RB.Admin.Widget'

    def __init__(self):
        """Initialize the widget."""
        self.dom_id = None

    def can_render(self, request):
        """Return whether the widget can be rendered in the dashboard.

        Subclasses can override this to make certain widgets conditional.
        By default, widgets can always be rendered.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

        Returns:
            bool:
            ``True``, always.
        """
        return True

    def get_js_model_attrs(self, request):
        """Return attributes to pass to the JavaScript model.

        These attributes will be passed to the widget model when instantiated.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

        Returns:
            dict:
            The attributes to pass to the model.
        """
        return {}

    def get_js_model_options(self, request):
        """Return options to pass to the JavaScript model.

        These options will be passed to the widget model when instantiated.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

        Returns:
            dict:
            The options to pass to the model.
        """
        return {}

    def get_js_view_options(self, request):
        """Return options to pass to the JavaScript view.

        These options will be passed to the widget view when instantiated.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

        Returns:
            dict:
            The options to pass to the view.
        """
        return {}

    def get_extra_context(self, request):
        """Return extra context for the template.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

        Returns:
            dict:
            Extra context to pass to the template.
        """
        return {}

    def render(self, request):
        """Render the widget to a string.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

        Returns:
            django.utils.safestring.SafeText:
            The rendered widget HTML.
        """
        return render_to_string(
            template_name=self.template_name,
            context=dict({
                'widget': self,
            }, **self.get_extra_context(request)),
            request=request)


class AdminWidgetsRegistry(OrderedRegistry):
    """The registry managing all administration dashboard widgets."""

    lookup_attrs = ('widget_id',)

    default_errors = dict(DEFAULT_ERRORS, **{
        ALREADY_REGISTERED: _(
            'Could not register the administration widget %(item)s. This '
            'widget is already registered or its ID conflicts with another '
            'widget.'
        ),
        ATTRIBUTE_REGISTERED: _(
            'Could not register the administration widget %(item)s: Another '
            'widget (%(duplicate)s) is already registered with the same ID.'
        ),
        NOT_REGISTERED: _(
            'No administration widget was found with an ID of '
            '"%(attr_value)s".'
        ),
        UNREGISTER: _(
            'Could not unregister the administration widget %(item)s: This '
            'widget has not been registered.'
        ),
    })

    @augment_method_from(OrderedRegistry)
    def register(self, admin_widget_cls):
        """Register a new administration widget class.

        Args:
            admin_widget_cls (type):
                The widget class to register. This must be a subclass of
                :py:class:`BaseAdminWidget`.

        Raises:
            djblets.registries.errors.RegistrationError:
                The :py:attr:`BaseAdminWidget.widget_id` value is missing on
                the class.

            djblets.registries.errors.AlreadyRegisteredError:
                This widget, or another with the same ID, was already
                registered.
        """
        pass

    @augment_method_from(OrderedRegistry)
    def unregister(self, admin_widget_cls):
        """Unregister an administration widget class.

        Args:
            admin_widget_cls (type):
                The widget class to unregister. This must be a subclass of
                :py:class:`BaseAdminWidget`.

        Raises:
            djblets.registries.errors.ItemLookupError:
                This widget was not registered.
        """
        pass

    def get_widget(self, widget_id):
        """Return a widget class with the specified ID.

        Args:
            widget_id (unicode):
                The ID of the widget to return.

        Returns:
            type:
            The subclass of :py:class:`BaseAdminWidget` that was registered
            with the given ID, if found. If the widget was not found, this
            will return ``None``.
        """
        try:
            return self.get('widget_id', widget_id)
        except self.lookup_error_class:
            return None

    def get_defaults(self):
        """Return the default widgets for the administration dashboard.

        Returns:
            list of type:
            The list of default widgets.
        """
        return [
            NewsWidget,
            ActivityGraphWidget,
            RepositoriesWidget,
            UserActivityWidget,
            ServerCacheWidget,
        ]


def get_sync_num():
    """Get the sync_num, which is number to sync.

    sync_num is number of update and initialized to 1 every day.
    """
    KEY = datetime.date.today()
    cache.add(KEY, 1)
    return cache.get(KEY)


def _increment_sync_num(*args, **kwargs):
    """Increment the sync_num."""
    KEY = datetime.date.today()

    if cache.get(KEY) is not None:
        cache.incr(KEY)


class UserActivityWidget(BaseAdminWidget):
    """A widget displaying stats on how often users interact with Review Board.

    This is displayed as a pie graph, with a legend alongside it breaking
    down the activity into 1-6 day, 7-29 day, 30-59 day, 60-89 day, and 90+
    day ranges.
    """

    widget_id = 'user-activity-widget'
    name = _('User Activity')
    js_view_class = 'RB.Admin.UserActivityWidgetView'
    css_classes = 'rb-c-admin-user-activity-widget'

    def get_js_model_attrs(self, request):
        """Return data for the JavaScript model.

        This will calculate the user activity in the various time ranges,
        and return the data for use in a rendered chart.

        Args:
            request (django.http.HttpRequest, unused):
                The HTTP request from the client.

        Returns:
            dict:
            Data for the JavaScript model,.
        """
        now = timezone.now()
        users = User.objects

        week = datetime.timedelta(days=7)
        day = datetime.timedelta(days=1)
        month = datetime.timedelta(days=30)
        two_months = datetime.timedelta(days=60)
        three_months = datetime.timedelta(days=90)

        one_day = (now - week, now + day)
        seven_days = (now - month, now - week)
        thirty_days = (now - two_months, now - month)
        sixty_days = (now - three_months, now - two_months)
        ninety_days = now - three_months

        return {
            'now': users.filter(last_login__range=one_day).count(),
            'sevenDays': users.filter(last_login__range=seven_days).count(),
            'thirtyDays': users.filter(last_login__range=thirty_days).count(),
            'sixtyDays': users.filter(last_login__range=sixty_days).count(),
            'ninetyDays': users.filter(last_login__lte=ninety_days).count(),
            'total': users.count()
        }


class RepositoriesWidget(BaseAdminWidget):
    """A widget displaying the most recent repositories.

    This widget displays a grid of the most recent repositories and their
    services/types.
    """

    #: The maximum number of repositories shown in the widget.
    MAX_REPOSITORIES = 8

    widget_id = 'repositories-widget'
    name = _('Repositories')
    css_classes = 'rb-c-admin-repositories-widget'
    template_name = 'admin/widgets/repositories.html'

    def get_extra_context(self, request):
        """Return extra context for the template.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

        Returns:
            dict:
            Extra context to pass to the template.
        """
        extra_context = cache_memoize(
            'admin-widget-repos-data',
            lambda: self._get_repositories_data(request))
        extra_context['add_repo_docs_url'] = \
            '%sadmin/configuration/repositories/' % get_manual_url()

        return extra_context

    def _get_repositories_data(self, request):
        """Return data on the repositories for the widget.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

        Returns:
            dict:
            Information on the repositories, for use as template context.
        """
        queryset = Repository.objects.accessible(request.user)
        total_repositories = queryset.count()

        if total_repositories > 0:
            queryset = (
                queryset
                .only('id', 'hosting_account_id', 'name', 'tool_id')
                .select_related('hosting_account')
                [:self.MAX_REPOSITORIES]
            )
        else:
            queryset = Repository.objects.none()

        repositories_info = []

        for repository in queryset:
            hosting_service = repository.hosting_service
            scmtool_class = repository.scmtool_class
            service_name = scmtool_class.name

            if hosting_service:
                service_name = _('%(hosting_service)s (%(tool)s)') % {
                    'hosting_service': hosting_service.name,
                    'tool': service_name,
                }

            repositories_info.append({
                'id': repository.pk,
                'name': repository.name,
                'service': service_name,
            })

        return {
            'repositories': repositories_info,
            'total_repositories': total_repositories,
        }


class ServerCacheWidget(BaseAdminWidget):
    """Cache statistics widget.

    Displays a list of memcached statistics, if available.
    """

    widget_id = 'server-cache-widget'
    name = _('Server Cache')
    template_name = 'admin/widgets/server_cache.html'

    def get_extra_context(self, request):
        """Return extra context for the template.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

        Returns:
            dict:
            Extra context to pass to the template.
        """
        context = super(ServerCacheWidget, self).get_extra_context(request)

        uptime = {}
        cache_stats = get_cache_stats()

        if cache_stats:
            for hosts, stats in cache_stats:
                uptime_secs = stats['uptime']

                if uptime_secs > 86400:
                    uptime['value'] = uptime_secs / 60 / 60 / 24
                    uptime['unit'] = _('days')
                elif uptime_secs > 3600:
                    uptime['value'] = uptime_secs / 60 / 60
                    uptime['unit'] = _('hours')
                else:
                    uptime['value'] = uptime_secs / 60
                    uptime['unit'] = _('minutes')

        context['cache_stats'] = cache_stats
        context['uptime'] = uptime

        return context


class NewsWidget(BaseAdminWidget):
    """A widget displaying the latest Review Board news headlines."""

    widget_id = 'news'
    name = _('Review Board News')
    css_classes = 'rb-c-admin-news-widget'
    js_view_class = 'RB.Admin.NewsWidgetView'
    js_model_class = 'RB.Admin.NewsWidget'

    def get_js_model_attrs(self, request):
        """Return attributes to pass to the JavaScript model.

        These contain URLs for the RSS feed and the public news page.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

        Returns:
            dict:
            The attributes to pass to the model.
        """
        return {
            'rssURL': 'https://www.reviewboard.org/news/feed/rss/latest/',
            'newsURL': 'https://www.reviewboard.org/news/',
            'subscribeURL': 'https://www.reviewboard.org/mailing-lists/',
        }


def dynamic_activity_data(request):
    """Large database activity widget helper.

    This method serves as a helper for the activity widget, it's used with for
    AJAX requests based on date ranges passed to it.
    """
    direction = request.GET.get('direction')
    range_end = request.GET.get('range_end')
    range_start = request.GET.get('range_start')
    days_total = 30

    # Convert the date from the request.
    #
    # This takes the date from the request in YYYY-MM-DD format and
    # converts into a format suitable for QuerySet later on.
    if range_end:
        range_end = datetime.datetime.fromtimestamp(
            time.mktime(time.strptime(range_end, "%Y-%m-%d")))

    if range_start:
        range_start = datetime.datetime.fromtimestamp(
            time.mktime(time.strptime(range_start, "%Y-%m-%d")))

    if direction == "next" and range_end:
        new_range_start = range_end
        new_range_end = \
            new_range_start + datetime.timedelta(days=days_total)
    elif direction == "prev" and range_start:
        new_range_start = range_start - datetime.timedelta(days=days_total)
        new_range_end = range_start
    elif direction == "same" and range_start and range_end:
        new_range_start = range_start
        new_range_end = range_end
    else:
        new_range_end = datetime.datetime.now() + datetime.timedelta(days=1)
        new_range_start = new_range_end - datetime.timedelta(days=days_total)

    current_tz = timezone.get_current_timezone()
    new_range_start = timezone.make_aware(new_range_start, current_tz)
    new_range_end = timezone.make_aware(new_range_end, current_tz)

    response_data = {
        "range_start": new_range_start.strftime("%Y-%m-%d"),
        "range_end": new_range_end.strftime("%Y-%m-%d")
    }

    def large_stats_data(range_start, range_end):
        def get_objects(model_name, timestamp_field, date_field):
            """Perform timestamp based queries.

            This method receives a dynamic model name and performs a filter
            query. Later the results are grouped by day and prepared for the
            charting library.
            """
            args = '%s__range' % timestamp_field
            q = model_name.objects.filter(**{
                args: (range_start, range_end)
            })
            q = q.extra({timestamp_field: date_field})
            q = q.values(timestamp_field)
            q = q.annotate(created_count=Count('pk'))
            q = q.order_by(timestamp_field)

            data = []

            for obj in q:
                data.append([
                    time.mktime(time.strptime(
                        str(obj[timestamp_field]),
                        "%Y-%m-%d")) * 1000,
                    obj['created_count']
                ])

            return data

        comment_array = get_objects(Comment, "timestamp", "date(timestamp)")
        change_desc_array = get_objects(ChangeDescription, "timestamp",
                                        "date(timestamp)")
        review_array = get_objects(Review, "timestamp", "date(timestamp)")
        rr_array = get_objects(ReviewRequest, "time_added", "date(time_added)")

        return {
            'change_descriptions': change_desc_array,
            'comments': comment_array,
            'reviews': review_array,
            'review_requests': rr_array
        }

    stats_data = large_stats_data(new_range_start, new_range_end)

    return {
        "range": response_data,
        "activity_data": stats_data
    }


class ActivityGraphWidget(BaseAdminWidget):
    """Detailed database statistics graph widget.

    Shows the latest database activity for multiple models in the form of
    a graph that can be navigated by date.

    This widget shows a daily view of creation activity for a list of models.
    All displayed widget data is computed on demand, rather than up-front
    during creation of the widget.
    """

    widget_id = 'activity-graph-widget'
    name = _('Review Board Activity')
    js_model_class = 'RB.Admin.ServerActivityWidget'
    js_view_class = 'RB.Admin.ServerActivityWidgetView'
    css_classes = 'rb-c-admin-server-activity-widget'


def init_widgets():
    """Initialize the widgets subsystem.

    This will listen for events in order to manage the widget caches.
    """
    post_save.connect(_increment_sync_num, sender=Group)
    post_save.connect(_increment_sync_num, sender=Repository)
    post_delete.connect(_increment_sync_num, sender=Group)
    post_delete.connect(_increment_sync_num, sender=Repository)


#: The registry of available administration widgets.
admin_widgets_registry = AdminWidgetsRegistry()
