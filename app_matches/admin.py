from django.contrib import admin

from .models import Match, Bet


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('num', 'datetime', 'home_team', 'away_team',
                    'home_team_score', 'away_team_score', 'venue',
                    'status', 'typ', 'winner', 'min_bet', 'result')
    list_filter = ('home_team', 'away_team', 'winner', 'venue')


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ('user', 'match', 'bet_team', 'bet_amt',
                    'status', 'win_amt', 'lost_amt', 'create_time')
    list_filter = ('user', 'match', 'status', 'bet_team')
