# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-10 22:51
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DeferredMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(null=True)),
                ('body', models.TextField(null=True)),
                ('data', jsonfield.fields.JSONField(null=True)),
                ('related_type', models.CharField(max_length=16, null=True)),
                ('related_id', models.PositiveIntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_id', models.TextField(unique=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
    ]
