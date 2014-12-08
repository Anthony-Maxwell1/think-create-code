# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uofa.fields
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('uofa', '0004_auto_20141205_0857'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=uofa.fields.NullableCharField(unique=True, default=None, validators=[django.core.validators.RegexValidator(b'^[\\w.@+-]+$', 'Please enter a valid nickname.', b'invalid')], max_length=255, blank=True, help_text='255 characters or fewer. Letters, digits and @/./+/-/_ only.', null=True, verbose_name='nickname'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(help_text='Required. 255 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, max_length=255, verbose_name='username', validators=[django.core.validators.RegexValidator(b'^[\\w.@+-]+$', 'Enter a valid username.', b'invalid')]),
        ),
    ]
