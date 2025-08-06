from __future__ import unicode_literals

from django.db import models
from django_evolution.mutations import AddField, MoveToDjangoMigrations


MUTATIONS = [
    AddField('MoveToMigrationsAppTestModel', 'added_field',
             models.BooleanField, initial=False),
    MoveToDjangoMigrations(),
]
