# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('uofa', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(help_text='Required. 255 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, max_length=255, verbose_name='username', validators=[django.core.validators.RegexValidator(b'^[\\w.@+-]+$', 'Enter a valid username.', b'invalid')]),
        ),
    ]
