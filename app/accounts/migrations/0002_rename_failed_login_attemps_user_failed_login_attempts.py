# Generated by Django 5.1.6 on 2025-03-16 19:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='failed_login_attemps',
            new_name='failed_login_attempts',
        ),
    ]
