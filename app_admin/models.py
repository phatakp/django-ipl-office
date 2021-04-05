from django.db import models
from django.core.exceptions import ValidationError


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


class IPLHistory(models.Model):
    """Match History Data for IPL."""

    STATUS_CHOICES = [('C', 'Completed'),
                      ('A', 'Abandoned')
                      ]

    # Model Fields
    date = models.DateField()
    home_team = models.ForeignKey('app_main.Team',
                                  related_name='home_teams_history',
                                  on_delete=models.CASCADE)
    away_team = models.ForeignKey('app_main.Team',
                                  related_name='away_teams_history',
                                  on_delete=models.CASCADE)
    venue = models.CharField(max_length=100)
    status = models.CharField(max_length=1,
                              choices=STATUS_CHOICES,
                              default='C',
                              db_index=True)
    winner = models.ForeignKey('app_main.Team',
                               related_name='winners_history',
                               on_delete=models.CASCADE,
                               blank=True, null=True)
    bat_first = models.ForeignKey('app_main.Team',
                                  related_name='first_batters',
                                  on_delete=models.CASCADE,
                                  blank=True, null=True)
    result = models.CharField(max_length=50,
                              validators=[result_validator])

    class Meta:
        """Meta definition for Match."""
        unique_together = ('date', 'home_team', 'away_team')
        verbose_name_plural = 'IPLMatchHistory'
        ordering = ['date', ]

    def __str__(self):
        """Unicode representation of Match."""
        return f"{str(self.home_team)} vs {str(self.away_team)} on {self.date}"


class IPLStats(models.Model):
    team = models.ForeignKey('app_main.Team',
                             related_name='stats_teams',
                             on_delete=models.CASCADE)
    vs_team = models.ForeignKey('app_main.Team',
                                related_name='vs_stats_teams',
                                blank=True, null=True,
                                on_delete=models.CASCADE)
    all_matches = models.PositiveSmallIntegerField(default=0)
    home_matches = models.PositiveSmallIntegerField(default=0)
    away_matches = models.PositiveSmallIntegerField(default=0)
    all_wins = models.PositiveSmallIntegerField(default=0)
    home_wins = models.PositiveSmallIntegerField(default=0)
    away_wins = models.PositiveSmallIntegerField(default=0)
    no_result = models.PositiveSmallIntegerField(default=0)
    bat_1st_wins = models.PositiveSmallIntegerField(default=0)
    bat_2nd_wins = models.PositiveSmallIntegerField(default=0)
    last5_wins = models.PositiveSmallIntegerField(default=0)

    class Meta:
        """Meta definition for Stats."""
        unique_together = ('team', 'vs_team')
        verbose_name_plural = 'IPLStats'
        ordering = ['team', 'vs_team']

    def __str__(self):
        """Unicode representation of Match."""
        if self.vs_team:
            return f"{str(self.team)} vs {str(self.vs_team)}"
        else:
            return f"{str(self.team)}"
