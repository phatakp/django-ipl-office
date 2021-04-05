# Generated by Django 3.1.7 on 2021-03-30 13:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_main', '0010_auto_20210330_1442'),
        ('app_users', '0005_customuser_is_ipl_admin'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamChangeAudit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('new_team', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='new_teams', to='app_main.team')),
                ('old_team', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='old_teams', to='app_main.team')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='team_changes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('user', 'create_time'),
            },
        ),
    ]
