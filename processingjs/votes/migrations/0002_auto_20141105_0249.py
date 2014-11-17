# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='status',
            field=models.IntegerField(choices=[(1, b'Thumbs Up'), (10, b'Feature')]),
        ),
    ]
