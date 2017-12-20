# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-13 03:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0012_auto_20171212_0609'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mealtemplate',
            name='cals',
        ),
        migrations.AddField(
            model_name='mealtemplate',
            name='cals_percent',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=4),
            preserve_default=False,
        ),
    ]