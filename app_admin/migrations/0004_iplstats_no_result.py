# Generated by Django 3.1.7 on 2021-03-26 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_admin', '0003_auto_20210326_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='iplstats',
            name='no_result',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
