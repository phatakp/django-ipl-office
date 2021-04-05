from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import TeamChangeAudit

CustomUser = get_user_model()


@admin.register(TeamChangeAudit)
class TeamChangeAuditAdmin(admin.ModelAdmin):
    list_display = ('user', 'old_team', 'new_team',
                    'amt_deducted', 'create_time')
    list_filter = ('user',)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'name', 'team', 'curr_amt', 'bets_won',
                    'bets_lost', 'team_chgd', 'is_ipl_admin', 'is_staff', 'is_active',)
    list_filter = ('email', 'name', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'name', 'password')}),
        ('Permissions', {'fields': ('curr_amt', 'bets_won',
                                    'bets_lost', 'team_chgd', 'is_ipl_admin',
                                    'is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'team', 'curr_amt', 'bets_won',
                       'bets_lost', 'team_chgd', 'is_staff', 'is_active',)}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
