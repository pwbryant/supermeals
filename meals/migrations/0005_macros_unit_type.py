# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-08 05:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0004_auto_20171127_0336'),
    ]

    operations = [
        migrations.AddField(
            model_name='macros',
            name='unit_type',
            field=models.CharField(choices=[('i', 'Imperial'), ('m', 'Metric')], default='i', max_length=1),
        ),
    ]