from django.contrib import admin

from .models import Team, Static


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'played', 'won', 'lost',
                    'no_res', 'points', 'nrr',
                    'for_status', 'against_status',
                    'fore_color', 'back_color')


@admin.register(Static)
class StaticAdmin(admin.ModelAdmin):
    list_display = ('entry', 'value',)
