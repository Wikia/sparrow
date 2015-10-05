# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0003_auto_20150529_1146'),
    ]

    operations = [
        migrations.RenameField(
            model_name='testrawresult',
            old_name='source',
            new_name='generator',
        ),
        migrations.AddField(
            model_name='testrawresult',
            name='context',
            field=jsonfield.fields.JSONField(default={}),
        ),
    ]
