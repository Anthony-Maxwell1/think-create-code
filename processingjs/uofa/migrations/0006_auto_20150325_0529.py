# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('uofa', '0005_auto_20141208_0711'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='time_zone',
            field=models.CharField(default=None, max_length=255, blank=True, help_text='Timezone to use when displaying dates and times.', null=True, verbose_name='timezone'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site and have Staff Member group permissions.', verbose_name='staff status'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(help_text='Required. 255 characters or fewer. Letters, digits and @.+:_- only.', unique=True, max_length=255, verbose_name='username', validators=[django.core.validators.RegexValidator(b'^[\\w.@+:-]+$', 'Enter a valid username.', b'invalid')]),
        ),
    ]
