"""Management command to reset review request counters on accounts."""

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from reviewboard.accounts.admin import fix_review_counts


class Command(BaseCommand):
    """Management command to reset review request counters on accounts."""

    help = _('Resets all review request-related counters on accounts.')

    def handle(self, **options):
        """Handle the command.

        Args:
            **options (dict, unused):
                Options parsed on the command line. For this command, no
                options are available.
        """
        fix_review_counts()
