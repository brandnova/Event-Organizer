# Generated by Django 5.1.3 on 2024-12-23 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_profile_account_locked_until_profile_email_verified_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='account_locked_until',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='email_verified',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='failed_login_attempts',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='last_password_change',
        ),
        migrations.AlterField(
            model_name='profile',
            name='bio',
            field=models.TextField(blank=True),
        ),
    ]
