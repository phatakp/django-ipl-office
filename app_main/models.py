from django.core.exceptions import ValidationError
from django.db import models

from app_admin.models import IPLStats


def status_validator(value):
    if value:
        if '/' in value:
            vals = value.split('/')
            try:
                vals[0] = int(vals[0])
                vals[1] = float(vals[1])
            except:
                raise ValidationError("Invalid format")
        else:
            raise ValidationError('Invalid format')


class Team(models.Model):
    """Teams in IPL 2021"""

    TEAM_CHOICES = [('CSK', 'Chennai Super Kings'),
                    ('DC', 'Delhi Capitals'),
                    ('PBKS', 'Punjab Kings'),
                    ('KKR', 'Kolkata Knightriders'),
                    ('MI', 'Mumbai Indians'),
                    ('RR', 'Rajasthan Royals'),
                    ('RCB', 'Royal Challengers Bangalore'),
                    ('SRH', 'Sunrisers Hyderabad'),
                    ]

    name = models.CharField(max_length=4,
                            choices=TEAM_CHOICES,
                            unique=True)
    logo = models.ImageField(blank=True, null=True, upload_to='logo/')
    slogo = models.ImageField(blank=True, null=True, upload_to='slogo/')
    bg = models.ImageField(blank=True, null=True, upload_to='bg/')
    profile_bg = models.ImageField(blank=True, null=True, upload_to='profile/')
    played = models.PositiveSmallIntegerField(default=0)
    won = models.PositiveSmallIntegerField(default=0)
    lost = models.PositiveSmallIntegerField(default=0)
    no_res = models.PositiveSmallIntegerField(default=0)
    points = models.PositiveSmallIntegerField(default=0)
    nrr = models.FloatField(default=0)
    for_status = models.CharField(
        max_length=20, blank=True, null=True, validators=[status_validator])
    against_status = models.CharField(
        max_length=20, blank=True, null=True, validators=[status_validator])
    fore_color = models.CharField(max_length=10, blank=True, null=True)
    back_color = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        ordering = ['-points', '-nrr', 'name', ]

    def __str__(self):
        """Unicode representation of Team."""
        if self.name:
            return self.name
        else:
            return 'TBC'

    @property
    def total_win_pct(self):
        obj = IPLStats.objects.filter(
            team=self, vs_team__isnull=True).values('all_matches', 'all_wins')
        return int(obj[0]['all_wins']/obj[0]['all_matches']*100)

    @property
    def home_win_pct(self):
        obj = IPLStats.objects.filter(
            team=self, vs_team__isnull=True).values('home_matches', 'home_wins')
        return int(obj[0]['home_wins']/obj[0]['home_matches']*100)

    @property
    def away_win_pct(self):
        obj = IPLStats.objects.filter(
            team=self, vs_team__isnull=True).values('away_matches', 'away_wins')
        return int(obj[0]['away_wins']/obj[0]['away_matches']*100)

    @property
    def bat1st_win_pct(self):
        obj = IPLStats.objects.filter(
            team=self, vs_team__isnull=True).values('all_wins', 'bat_1st_wins')
        return int(obj[0]['bat_1st_wins']/obj[0]['all_wins']*100)


class Static(models.Model):
    entry = models.CharField(max_length=50, unique=True)
    value = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.entry
