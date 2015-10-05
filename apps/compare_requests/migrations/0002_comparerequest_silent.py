# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('compare_requests', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comparerequest',
            name='silent',
            field=models.BooleanField(default=False),
        ),
    ]
