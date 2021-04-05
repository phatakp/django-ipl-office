from datetime import timedelta

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView

from .forms import MatchFilterForm, BetForm, MatchWinnerForm
from .models import Match, Bet
from .validations import add_default_bets, validate_and_save_bet, validate_and_save_match_winner, update_final_match
from app_admin.models import IPLStats

Team = apps.get_model('app_main', 'Team')
IPLHistory = apps.get_model('app_admin', 'IPLHistory')


class ScheduleView(ListView):
    model = Match
    template_name = 'schedule.html'
    context_object_name = 'matches'

    def get_queryset(self):
        return Match.objects.select_related('home_team', 'away_team', 'winner')

    def get(self, request, *args, **kwargs):
        extra_context = {'fix_active': '',
                         'res_active': '',
                         'sch_active': 'active',
                         'dash_active': '',
                         'home_active': '',
                         'admin_active': '',
                         'login_active': '',
                         'form': MatchFilterForm(),
                         }
        if kwargs['typ'] == 'fix':
            self.object_list = self.get_queryset().filter(status='S')
            extra_context.update({'fix_active': 'active'})
        else:
            self.object_list = self.get_queryset().exclude(status='S')
            extra_context.update({'res_active': 'active'})

        context = self.get_context_data(**kwargs)
        context.update(extra_context)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        extra_context = {'fix_active': '',
                         'res_active': '',
                         'sch_active': 'active',
                         'dash_active': '',
                         'home_active': '',
                         'admin_active': '',
                         'login_active': '',
                         }
        if kwargs['typ'] == 'fix':
            self.object_list = self.get_queryset().filter(status='S')
            extra_context.update({'fix_active': 'active'})
        else:
            self.object_list = self.get_queryset().exclude(status='S')
            extra_context.update({'res_active': 'active'})
        context = self.get_context_data(**kwargs)
        form = MatchFilterForm(request.POST)
        extra_context.update({'form': form})

        if form.is_valid():
            # Get team details from form
            hteam = form.cleaned_data.get('home_team', None)
            ateam = form.cleaned_data.get('away_team', None)

            if hteam is not None:
                if ateam is None:  # Only Home team present
                    extra_context.update(
                        {'matches': self.object_list.filter(home_team=hteam)})

                else:  # Both Home and Away team present
                    extra_context.update(
                        {'matches': self.object_list.filter(home_team=hteam,
                                                            away_team=ateam)})
            else:
                if ateam is not None:  # Only Away team present
                    extra_context.update(
                        {'matches': self.object_list.filter(away_team=ateam)})

        context.update(extra_context)
        return render(request, self.template_name, context)


class MatchDetailView(LoginRequiredMixin, DetailView):
    model = Match
    template_name = 'match_detail.html'
    login_url = reverse_lazy('app_users:login')
    redirect_field_name = 'match_detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        extra_context = {'form': BetForm(prefix=self.object),
                         'winner_form': MatchWinnerForm(),
                         'home_form_all': self.form_guide(self.object.home_team),
                         'away_form_all': self.form_guide(self.object.away_team),
                         'vs_form': self.form_guide(self.object.home_team, self.object.away_team),
                         'cutoff': self.object.datetime - timedelta(minutes=60),
                         'home_total_wins': self.total_wins(self.object.home_team, self.object.away_team),
                         'home_home_wins': self.home_wins(self.object.home_team, self.object.away_team),
                         'home_away_wins': self.away_wins(self.object.home_team, self.object.away_team),
                         'home_bat1st_wins': self.bat1st_wins(self.object.home_team, self.object.away_team),
                         'away_bat1st_wins': self.bat1st_wins(self.object.away_team, self.object.home_team),
                         'home_bat1st_chances': self.win_chances(self.object.home_team, self.object.away_team),
                         'home_bat2nd_chances': self.win_chances(self.object.home_team, self.object.away_team, bat_first=False),
                         }

        # Display Current bet if present
        if self.user_bet_for_match_exists():
            bet = Bet.objects.get(user=request.user, match=self.object)
            context['message'] = f'<strong>Current Prediction: {bet.bet_team.name}.</strong> <br> 10 points to be deducted if team changed.'
            context['msg_status'] = 'success'
        else:
            context['message'] = f'No Prediction made yet'
            context['msg_status'] = 'danger'

        match_bets = self.bets()
        extra_context.update(
            {'match_bets': self.get_queryset_paginator(match_bets)})

        context.update(extra_context)
        return self.render_to_response(context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)

        form = BetForm(request.POST, prefix=self.object)
        winner_form = MatchWinnerForm(request.POST)
        extra_context = {'form': form,
                         'winner_form': winner_form,
                         'home_form_all': self.form_guide(self.object.home_team),
                         'away_form_all': self.form_guide(self.object.away_team),
                         'vs_form': self.form_guide(self.object.home_team, self.object.away_team),
                         'cutoff': self.object.datetime - timedelta(minutes=60),
                         'home_total_wins': self.total_wins(self.object.home_team, self.object.away_team),
                         'home_home_wins': self.home_wins(self.object.home_team, self.object.away_team),
                         'home_away_wins': self.away_wins(self.object.home_team, self.object.away_team),
                         'home_bat1st_wins': self.bat1st_wins(self.object.home_team, self.object.away_team),
                         'away_bat1st_wins': self.bat1st_wins(self.object.away_team, self.object.home_team),
                         'home_bat1st_chances': self.win_chances(self.object.home_team, self.object.away_team),
                         'home_bat2nd_chances': self.win_chances(self.object.home_team, self.object.away_team, bat_first=False),
                         }
        match_bets = self.bets()
        extra_context.update(
            {'match_bets': self.get_queryset_paginator(match_bets)})

        if request.user.is_ipl_admin:
            # Match Winner Update Process
            if 'winner-form' in request.POST and winner_form.is_valid():
                if self.object.isWithinTime:  # Match has not yet started
                    extra_context.update({'win_message': 'Cutoff for Match not passed yet',
                                          'win_msg_status': 'danger'})
                else:
                    # Get form details
                    winner = winner_form.cleaned_data.get('winner', None)
                    home_score = winner_form.cleaned_data.get(
                        'home_team_score', None)
                    away_score = winner_form.cleaned_data.get(
                        'away_team_score', None)
                    result = winner_form.cleaned_data.get('result', None)

                    # Convert winner to Team object
                    if winner is not None:
                        winner = Team.objects.get(name=winner)

                    # Validate and Save details to Match table. Also settle bets
                    msg, status = validate_and_save_match_winner(self.object, winner, result,
                                                                 home_score, away_score)

                    # For final match, also settle IPL winner bets
                    if self.object.is_final:
                        update_final_match(winner)

                    extra_context.update({'win_message': msg,
                                          'win_msg_status': 'success' if status else 'danger'})

        # Bet Entry Process
        if 'bet-form' in request.POST and form.is_valid():
            # Get form values
            team_name = self.request.POST.get('team-name', None)
            team = Team.objects.get(name=team_name)

            # Validate and save details to Bet table
            msg, status = validate_and_save_bet(self.request.user,
                                                self.object, team)
            extra_context.update({'message': msg,
                                  'msg_status': 'success' if status else 'danger'})

        context.update(extra_context)
        return render(request, self.template_name, context)

    def user_bet_for_match_exists(self):
        return Bet.objects.filter(user=self.request.user,
                                  match=self.object, status='P').exists()

    def form_guide(self, team1, team2=None):
        # Get list of latest 5 completed matches for the team
        if team2:
            return IPLHistory.objects.filter(Q(home_team=team1, away_team=team2) |
                                             Q(home_team=team2, away_team=team1)).exclude(winner__isnull=True).order_by('-date')[:5]
        else:
            return IPLHistory.objects.filter(Q(home_team=team1) |
                                             Q(away_team=team1)).exclude(winner__isnull=True).order_by('-date')[:5]

    def total_wins(self, team1, team2):
        # Total Win Percentage
        obj = IPLStats.objects.filter(
            team=team1, vs_team=team2).values('all_matches', 'all_wins')
        return int(obj[0]['all_wins']/obj[0]['all_matches']*100)

    def home_wins(self, team1, team2=None):
        # Home Win Percentage
        obj = IPLStats.objects.filter(
            team=team1, vs_team=team2).values('home_matches', 'home_wins')
        return int(obj[0]['home_wins']/obj[0]['home_matches']*100)

    def away_wins(self, team1, team2=None):
        # Away Win Percentage
        obj = IPLStats.objects.filter(
            team=team1, vs_team=team2).values('away_matches', 'away_wins')
        return int(obj[0]['away_wins']/obj[0]['away_matches']*100)

    def bat1st_wins(self, team1, team2=None):
        # Win Percentage while batting first
        obj = IPLStats.objects.filter(
            team=team1, vs_team=team2).values('all_wins', 'bat_1st_wins')
        return int(obj[0]['bat_1st_wins']/obj[0]['all_wins']*100)

    def bets(self):
        if self.object.isWithinBetCutoff:
            return Bet.objects.filter(user=self.request.user, match=self.object).select_related('user',
                                                                                                'match',
                                                                                                'bet_team')

        else:
            return Bet.objects.filter(match=self.object).select_related('user',
                                                                        'match',
                                                                        'bet_team').order_by('create_time')

    def get_queryset_paginator(self, match_bets):
        paginator = Paginator(match_bets, 2)
        page = self.request.GET.get('page')

        try:
            page_obj = paginator.page(page)
            return page_obj
        except PageNotAnInteger:
            page_obj = paginator.page(1)
            return page_obj
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
            return page_obj

    def win_chances(self, team1, team2, bat_first=True):

        def weighted_formula(last5_wins, bat_wins, all_wins, all_matches, home_wins, home_matches):
            # Average of (35% of LATEST_WIN_PCT) + (25% of BAT_1_OR_2_WIN_PCT) + (25% of HOME_WIN_PCT) + (15% of ALL_WIN_PCT)
            return (0.35 * (last5_wins/5) +
                    0.25 * (bat_wins/all_wins) +
                    0.25 * (home_wins/home_matches) +
                    0.15 * (all_wins/all_matches)
                    ) / 4 * 100

        # Predict Win Chances while Batting first and Second w.r.t team as home team
        team_avg = dict()
        for t1 in (team1, team2):
            overall = IPLStats.objects.get(team=t1, vs_team__isnull=True)
            overall_avg = weighted_formula(overall.last5_wins,
                                           overall.bat_1st_wins if bat_first else overall.bat_2nd_wins,
                                           overall.all_wins, overall.all_matches,
                                           overall.home_wins, overall.home_matches)
            for t2 in (team1, team2):
                if t1 != t2:
                    versus = IPLStats.objects.get(team=t1, vs_team=t2)
                    versus_avg = weighted_formula(versus.last5_wins,
                                                  versus.bat_1st_wins if bat_first else versus.bat_2nd_wins,
                                                  versus.all_wins, versus.all_matches,
                                                  versus.home_wins, versus.home_matches)

                    # Get average win for a team
                    team_avg[t1] = (overall_avg + versus_avg)/2

        # Get ratio of both team average wins
        frac = team_avg[team1]/team_avg[team2]
        return int(100 - (100/(1+frac)))
