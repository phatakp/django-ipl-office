# Generated by Django 3.1.7 on 2021-03-30 03:42

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app_matches', '0007_auto_20210328_1729'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='bet',
            unique_together={('user', 'match')},
        ),
    ]
