# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-09 01:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0008_auto_20171208_0616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='macros',
            name='gender',
            field=models.CharField(choices=[('m', 'Male'), ('f', 'Female')], max_length=1),
        ),
    ]
