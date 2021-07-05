from datetime import timedelta

from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone


CustomUser = get_user_model()


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


def result_validator(value):
    teams = ('CSK', 'DC', 'RCB', 'RR', 'SRH', 'PBKS', 'KKR', 'MI')
    if value:
        for team in teams:
            if team in value and 'won' in value:
                return

        if "Match" in value:
            return
        else:
            raise ValidationError("Invalid result value")


class Match(models.Model):
    """Match in IPL 2021."""

    STATUS_CHOICES = [('C', 'Completed'),
                      ('S', 'Scheduled'),
                      ('A', 'Abandoned')
                      ]

    TYPE_CHOICES = [('L', 'League'),
                    ('E', 'Eliminator'),
                    ('F', 'Final'),
                    ('Q1', 'Qualifier1'),
                    ('Q2', 'Qualifier2'),
                    ]

    # Model Fields
    num = models.PositiveSmallIntegerField(unique=True)
    datetime = models.DateTimeField()
    home_team = models.ForeignKey('app_main.Team',
                                  related_name='home_teams',
                                  on_delete=models.CASCADE,
                                  blank=True, null=True)
    away_team = models.ForeignKey('app_main.Team',
                                  related_name='away_teams',
                                  on_delete=models.CASCADE,
                                  blank=True, null=True)
    home_team_score = models.CharField(
        max_length=20, blank=True, null=True, validators=[status_validator])
    away_team_score = models.CharField(
        max_length=20, blank=True, null=True, validators=[status_validator])
    venue = models.CharField(max_length=100)
    status = models.CharField(max_length=1,
                              choices=STATUS_CHOICES,
                              default='S',
                              db_index=True)
    typ = models.CharField(max_length=2,
                           choices=TYPE_CHOICES,
                           default='L',
                           db_index=True)
    winner = models.ForeignKey('app_main.Team',
                               related_name='winners',
                               on_delete=models.CASCADE,
                               blank=True, null=True)
    min_bet = models.PositiveSmallIntegerField(default=20)
    result = models.CharField(max_length=50,
                              default="Match yet to begin", validators=[result_validator])

    class Meta:
        """Meta definition for Match."""
        verbose_name_plural = 'Matches'
        ordering = ['datetime', ]

    def __str__(self):
        """Unicode representation of Match."""
        if self.home_team is not None:
            return f"{str(self.home_team)} vs {str(self.away_team)}"
        else:
            return f"{self.get_typ_display()}: TBC vs TBC"

    def get_absolute_url(self):
        return reverse('app_matches:detail', kwargs={'pk': self.id})

    @property
    def is_completed(self):
        return self.status == 'C'

    @property
    def is_scheduled(self):
        return self.status == 'S'

    @property
    def is_abandoned(self):
        return self.status == 'A'

    @property
    def is_started(self):
        return self.is_scheduled and not self.isWithinTime

    @property
    def is_final(self):
        return self.typ == 'F'

    @property
    def is_league(self):
        return self.typ == 'L'

    # For change of bet cutoff
    @property
    def isWithinTime(self):
        return timezone.localtime() < self.datetime

    # For Initial bet cutoff
    @property
    def isWithinBetCutoff(self):
        return (timezone.localtime() < (self.datetime - timedelta(minutes=60)))


class Bet(models.Model):
    STATUS_CHOICES = [('P', 'Placed'),
                      ('D', 'Defaulted'),
                      ('W', 'Won'),
                      ('L', 'Lost'),
                      ('R', 'No Result')]

    # Model Fields
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name="user_bets",
                             on_delete=models.CASCADE)

    match = models.ForeignKey('Match',
                              related_name="match_bets",
                              on_delete=models.CASCADE,
                              blank=True, null=True)

    bet_team = models.ForeignKey('app_main.Team',
                                 related_name="bet_teams",
                                 on_delete=models.CASCADE,
                                 blank=True,
                                 null=True)

    bet_amt = models.PositiveSmallIntegerField(default=0)

    win_amt = models.FloatField(default=0)

    lost_amt = models.FloatField(default=0)

    status = models.CharField(max_length=1,
                              default='P',
                              choices=STATUS_CHOICES,
                              db_index=True)

    create_time = models.DateTimeField(default=timezone.localtime,
                                       db_index=True)

    class Meta:
        unique_together = ('user', 'match')
        ordering = ['match', 'create_time', 'user']

    def __str__(self) -> str:
        if self.match is not None:
            return f"{self.user.name} for {str(self.match)}"
        else:
            return f"{self.user.name} for IPL Winner"

    @ property
    def is_placed(self):
        return self.status == 'P'

    @ property
    def is_won(self):
        return self.status == 'W'

    @ property
    def is_lost_or_default(self):
        return self.status == 'L' or self.status == 'D'
