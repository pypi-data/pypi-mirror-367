from django.core.exceptions import ObjectDoesNotExist
from djblets.webapi.decorators import (webapi_response_errors,
                                       webapi_request_fields)
from djblets.webapi.errors import DOES_NOT_EXIST
from djblets.webapi.fields import DateTimeFieldType, StringFieldType

from reviewboard.certs.errors import CertificateVerificationError
from reviewboard.hostingsvcs.errors import HostingServiceError
from reviewboard.reviews.models import ReviewRequest
from reviewboard.scmtools.errors import SCMError
from reviewboard.webapi.base import WebAPIResource
from reviewboard.webapi.decorators import (webapi_check_login_required,
                                           webapi_check_local_site)
from reviewboard.webapi.errors import (REPO_INFO_ERROR,
                                       REPO_NOT_IMPLEMENTED,
                                       UNVERIFIED_HOST_CERT)
from reviewboard.webapi.resources import resources


class RepositoryCommitsResource(WebAPIResource):
    """Provides information on the commits in a repository.

    This will fetch a page of commits from the repository. Each page will
    usually be 30 items, but the exact count is dependent on the repository
    type. To paginate results, provide a ``start`` parameter with a value of
    the commit ID to start from. Usually this will be set to the ``parent``
    field from the last commit.

    Data on commits will not be available for all types of repositories.
    """

    added_in = '2.0'

    name = 'commits'
    policy_id = 'repository_commits'
    singleton = True
    allowed_methods = ('GET',)
    uri_template_name = 'repository_commits'
    mimetype_item_resource_name = 'repository-commits'

    # For this resource, the fields dictionary is not used for any
    # serialization. It's used solely for documentation.
    fields = {
        'id': {
            'type': StringFieldType,
            'description': 'The revision identifier of the commit.\n\n'
                           'The format depends on the repository type (it may '
                           'be a number, SHA-1 hash, or some other type). '
                           'This should be treated as a relatively opaque.',
        },
        'author_name': {
            'type': StringFieldType,
            'description': 'The real name or username of the author who made '
                           'the commit.',
        },
        'date': {
            'type': DateTimeFieldType,
            'description': 'The timestamp of the commit.',
        },
        'message': {
            'type': StringFieldType,
            'description': 'The commit message, if any.',
        },
        'parent': {
            'type': StringFieldType,
            'description': 'The revision of the parent commit. This may be '
                           'an empty string if this is the first revision in '
                           'the commit history for a repository or branch.',
        },
    }

    @webapi_check_local_site
    @webapi_check_login_required
    @webapi_response_errors(
        DOES_NOT_EXIST,
        REPO_INFO_ERROR,
        REPO_NOT_IMPLEMENTED,
        UNVERIFIED_HOST_CERT,
    )
    @webapi_request_fields(
        optional={
            'branch': {
                'type': StringFieldType,
                "description": "The ID of the branch to limit the commits "
                               "to, as provided by the 'id' field of the "
                               "repository branches API.",
                'added_in': '2.5',
            },
            'start': {
                'type': StringFieldType,
                'description': 'A commit ID to start listing from.',
            },
        }
    )
    def get(self, request, branch=None, start=None, *args, **kwargs):
        """Retrieves a set of commits from a particular repository.

        The ``start`` parameter is a commit ID to use as a starting point. This
        allows both pagination and logging of different branches. Successive
        pages of commit history can be fetched by using the ``parent`` field of
        the last entry as the ``start`` parameter for another request.
        """
        try:
            repository = resources.repository.get_object(request, *args,
                                                         **kwargs)
        except ObjectDoesNotExist:
            return DOES_NOT_EXIST

        try:
            items = repository.get_commits(branch=branch, start=start)
        except CertificateVerificationError as e:
            return UNVERIFIED_HOST_CERT.with_message(str(e)), {
                'certificate': e.certificate,
            }
        except (HostingServiceError, SCMError) as e:
            return REPO_INFO_ERROR.with_message(str(e))
        except NotImplementedError:
            return REPO_NOT_IMPLEMENTED

        commits = []
        commit_ids = []
        for commit in items:
            commits.append({
                'author_name': commit.author_name,
                'id': commit.id,
                'date': commit.date,
                'message': commit.message,
                'parent': commit.parent,
            })
            commit_ids.append(commit.id)

        by_commit_id = {}
        for obj in ReviewRequest.objects.filter(repository=repository,
                                                commit_id__in=commit_ids):
            by_commit_id[obj.commit_id] = obj

        for commit in commits:
            try:
                review_request = by_commit_id[commit['id']]
                commit['review_request_url'] = \
                    review_request.get_absolute_url()
            except KeyError:
                commit['review_request_url'] = ''

        return 200, {
            self.item_result_key: commits,
        }


repository_commits_resource = RepositoryCommitsResource()
