# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-08 05:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0006_auto_20171208_0547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='macros',
            name='unit_type',
            field=models.CharField(choices=[('i', 'Imperial'), ('m', 'Metric')], default='i', max_length=1),
        ),
    ]