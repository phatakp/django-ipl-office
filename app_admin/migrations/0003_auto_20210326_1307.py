# Generated by Django 3.1.7 on 2021-03-26 07:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_admin', '0002_iplstats'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='iplstats',
            options={'ordering': ['team', 'vs_team'], 'verbose_name_plural': 'IPLStats'},
        ),
        migrations.RemoveField(
            model_name='iplhistory',
            name='neutral_venue',
        ),
        migrations.RemoveField(
            model_name='iplstats',
            name='neutral_matches',
        ),
        migrations.RemoveField(
            model_name='iplstats',
            name='neutral_wins',
        ),
    ]