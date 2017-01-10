# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-10 22:51
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import popo_attribute_tracker.attribute_tracker


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone_number', models.BinaryField(max_length=255, null=True, unique=True)),
                ('avatar', models.ImageField(null=True, upload_to='avatars/')),
                ('last_avatar_update', models.DateTimeField(auto_now_add=True)),
                ('is_hidden', models.BooleanField(default=False)),
                ('joined', models.DateTimeField(auto_now_add=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_validator', models.CharField(max_length=255, unique=True)),
                ('is_accepted', models.BooleanField(default=False)),
                ('is_hidden', models.BooleanField(default=False)),
                ('from_blocking', models.BooleanField(default=False)),
                ('to_blocking', models.BooleanField(default=False)),
                ('from_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_account', to=settings.AUTH_USER_MODEL)),
                ('to_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_account', to=settings.AUTH_USER_MODEL)),
            ],
            bases=(models.Model, popo_attribute_tracker.attribute_tracker.AttributeTrackerMixin),
        ),
        migrations.AddField(
            model_name='user',
            name='friends',
            field=models.ManyToManyField(through='user.Friendship', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
