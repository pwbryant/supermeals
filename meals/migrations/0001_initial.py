# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-24 19:31
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Macros',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(choices=[('m', 'Male'), ('f', 'Female')], default='m', max_length=1)),
                ('age', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(120)])),
                ('weight', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(300)])),
                ('height', models.IntegerField(validators=[django.core.validators.MinValueValidator(30), django.core.validators.MaxValueValidator(250)])),
                ('activity', models.IntegerField(choices=[('none', ''), ('light', ''), ('medium', ''), ('high', ''), ('very high', '')])),
                ('change_rate', models.DecimalField(decimal_places=2, max_digits=4)),
                ('fat_percent', models.DecimalField(decimal_places=2, max_digits=4)),
                ('protein_percent', models.DecimalField(decimal_places=2, max_digits=4)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MealTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_per_day', models.IntegerField()),
                ('daily_percent', models.DecimalField(decimal_places=2, max_digits=4)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
