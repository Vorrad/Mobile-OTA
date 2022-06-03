# Generated by Django 4.0.4 on 2022-05-11 20:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OTA', '0006_alter_userinfo_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='noserInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default=datetime.datetime.now)),
                ('name', models.TextField(max_length=64)),
                ('device', models.TextField(max_length=64)),
                ('version', models.TextField(max_length=64)),
                ('reporter', models.TextField(max_length=128)),
            ],
        ),
    ]