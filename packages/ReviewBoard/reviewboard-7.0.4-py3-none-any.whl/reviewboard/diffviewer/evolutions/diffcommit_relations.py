"""Added DiffCommit-related fields to DiffSet and FileDiff.

Version Added:
    4.0
"""

from django_evolution.mutations import AddField
from django.db import models
from djblets.db.fields import RelationCounterField


MUTATIONS = [
    AddField('DiffSet', 'commit_count', RelationCounterField, null=True),
    AddField('DiffSet', 'file_count', RelationCounterField, null=True),
    AddField('DiffCommit', 'file_count', RelationCounterField, null=True),
    AddField('FileDiff', 'commit', models.ForeignKey, null=True,
             related_model='diffviewer.DiffCommit'),
]
