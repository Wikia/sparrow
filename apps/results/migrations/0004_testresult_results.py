# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0003_testresult_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='testresult',
            name='results',
            field=jsonfield.fields.JSONField(default={}),
        ),
    ]
