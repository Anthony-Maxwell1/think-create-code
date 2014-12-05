# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uofa.fields
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('uofa', '0003_auto_20141205_0620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=uofa.fields.NullableCharField(null=True, default=None, max_length=255, blank=True, unique=True, verbose_name='username'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(help_text='Required. 255 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, max_length=255, verbose_name='user_id', validators=[django.core.validators.RegexValidator(b'^[\\w.@+-]+$', 'Enter a valid username.', b'invalid')]),
        ),
    ]
