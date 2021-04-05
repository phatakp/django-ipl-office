# Generated by Django 3.1.7 on 2021-03-18 06:46

import app_main.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('CSK', 'Chennai Super Kings'), ('DC', 'Delhi Capitals'), ('PBKS', 'Punjab Kings'), ('KKR', 'Kolkata Knightriders'), ('MI', 'Mumbai Indians'), ('RR', 'Rajasthan Royals'), ('RCB', 'Royal Challengers Bangalore'), ('SRH', 'Sunrisers Hyderabad')], max_length=4, unique=True)),
                ('logo', models.ImageField(upload_to='')),
                ('played', models.PositiveSmallIntegerField(default=0)),
                ('won', models.PositiveSmallIntegerField(default=0)),
                ('lost', models.PositiveSmallIntegerField(default=0)),
                ('no_res', models.PositiveSmallIntegerField(default=0)),
                ('nrr', models.FloatField(default=0)),
                ('for_status', models.CharField(default=' ', max_length=20, validators=[app_main.models.status_validator])),
                ('against_status', models.CharField(default=' ', max_length=20, validators=[app_main.models.status_validator])),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
