# Generated by Django 3.1.7 on 2021-03-23 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_main', '0006_auto_20210322_1547'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='profile_bg',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
