# Generated by Django 3.1.7 on 2021-03-19 13:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_main', '0005_team_slogo'),
        ('app_users', '0002_player'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'ordering': ['-curr_amt', 'name']},
        ),
        migrations.AddField(
            model_name='customuser',
            name='bets_lost',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='customuser',
            name='bets_won',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='customuser',
            name='curr_amt',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='customuser',
            name='team',
            field=models.ForeignKey(blank='True', null='True', on_delete=django.db.models.deletion.CASCADE, related_name='teams', to='app_main.team'),
            preserve_default='True',
        ),
        migrations.AddField(
            model_name='customuser',
            name='team_chgd',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='Player',
        ),
    ]
