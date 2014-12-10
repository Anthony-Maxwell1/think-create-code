# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exhibitions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='exhibition',
            name='image',
            field=models.ImageField(default=None, upload_to=b'not required', blank=True, help_text='Max file size 4MB.', null=True),
            preserve_default=True,
        ),
    ]
