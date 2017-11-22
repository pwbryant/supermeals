# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-22 05:02
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('meals', '0004_delete_mm_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Macros',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(choices=[('male', 'male'), ('female', 'female')], max_length=6)),
                ('age', models.IntegerField(validators=[django.core.validators.MaxValueValidator(120)])),
                ('weight', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(300)])),
                ('height', models.IntegerField(validators=[django.core.validators.MinValueValidator(30), django.core.validators.MaxValueValidator(250)])),
            ],
        ),
    ]