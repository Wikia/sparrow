# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_auto_20150424_1258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
