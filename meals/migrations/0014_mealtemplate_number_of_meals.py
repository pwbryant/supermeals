# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-17 15:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0013_auto_20171213_0358'),
    ]

    operations = [
        migrations.AddField(
            model_name='mealtemplate',
            name='number_of_meals',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
