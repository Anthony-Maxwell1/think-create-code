# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('exhibitions', '0002_exhibition_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exhibition',
            name='released_at',
            field=models.DateTimeField(default=None, help_text=django.utils.timezone.now, null=True, verbose_name=b'release date', blank=True),
        ),
    ]
