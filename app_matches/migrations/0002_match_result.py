# Generated by Django 3.1.7 on 2021-03-20 11:21

import app_matches.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_matches', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='result',
            field=models.CharField(blank=True, max_length=50, null=True, validators=[app_matches.models.result_validator]),
        ),
    ]
