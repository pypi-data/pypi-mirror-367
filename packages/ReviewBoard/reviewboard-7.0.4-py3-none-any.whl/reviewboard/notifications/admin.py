from django.utils.translation import gettext_lazy as _

from reviewboard.admin import ModelAdmin, admin_site
from reviewboard.notifications.forms import WebHookTargetForm
from reviewboard.notifications.models import WebHookTarget


class WebHookTargetAdmin(ModelAdmin):
    form = WebHookTargetForm

    list_display = ('url', 'enabled')
    filter_horizontal = ('repositories',)
    fieldsets = (
        (_('General Information'), {
            'fields': (
                'enabled',
                'url',
                'events',
                'apply_to',
                'repositories',
            ),
        }),
        (_('Payload'), {
            'fields': (
                'encoding',
                'use_custom_content',
                'custom_content',
                'secret',
            ),
        }),
        (_('Advanced'), {
            'fields': (
                'local_site',
                'extra_data',
            ),
            'classes': ['collapse'],
        }),
    )
    raw_id_fields = ('local_site',)


admin_site.register(WebHookTarget, WebHookTargetAdmin)
