# Generated by Django 4.0.4 on 2022-05-11 19:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('OTA', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userinfo',
            old_name='repoter',
            new_name='reporter',
        ),
    ]
