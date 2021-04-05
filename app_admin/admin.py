from django.contrib import admin
from .models import IPLHistory, IPLStats


@admin.register(IPLHistory)
class IPLHistoryAdmin(admin.ModelAdmin):
    list_display = ('date', 'home_team', 'away_team',
                    'venue', 'status', 'winner', 'bat_first',
                    'result')
    list_filter = ('home_team', 'away_team', 'winner',
                   'venue', 'bat_first', 'status')


@admin.register(IPLStats)
class IPLStatsAdmin(admin.ModelAdmin):
    list_display = ('team', 'vs_team',
                    'all_matches', 'home_matches', 'away_matches',
                    'all_wins', 'home_wins', 'away_wins',
                    'bat_1st_wins', 'bat_2nd_wins', 'last5_wins')
    list_filter = ('team', 'vs_team')
