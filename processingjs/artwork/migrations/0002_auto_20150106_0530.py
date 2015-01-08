# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artwork', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artwork',
            name='shared',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
