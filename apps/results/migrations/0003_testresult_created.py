# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0002_auto_20150422_1618'),
    ]

    operations = [
        migrations.AddField(
            model_name='testresult',
            name='created',
            field=models.DateField(auto_now_add=True, default=datetime.datetime.now(tz=utc)),
            preserve_default=False,
        ),
    ]
