# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-30 04:02
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0002_auto_20171029_1656'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='User',
            new_name='MM_user',
        ),
    ]
