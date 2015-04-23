# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0002_test_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='created',
            field=models.DateField(auto_now_add=True, default=datetime.datetime.now(tz=utc)),
            preserve_default=False,
        ),
    ]
