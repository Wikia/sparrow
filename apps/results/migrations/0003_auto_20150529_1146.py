# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0002_testrawresult'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testrawresult',
            name='data',
            field=jsonfield.fields.JSONField(default={}),
        ),
    ]
