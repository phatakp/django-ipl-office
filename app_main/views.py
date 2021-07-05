from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, FormView, TemplateView

from .forms import TeamChangeForm
from .models import Team, Static

CustomUser = get_user_model()
Match = apps.get_model('app_matches', 'Match')
Bet = apps.get_model('app_matches', 'Bet')
TeamChangeAudit = apps.get_model('app_users', 'TeamChangeAudit')


class HomeView(ListView):
    model = Team
    template_name = 'index.html'
    context_object_name = 'teams'

    def get_queryset(self):
        return Team.objects.all().order_by('-points', '-nrr', '-won', 'lost', 'played')

    def get_context_data(self, *args, **kwargs):
        context = super(HomeView, self).get_context_data(*args, **kwargs)
        extra_context = {'sch_active': '',
                         'dash_active': '',
                         'home_active': 'active',
                         'admin_active': '',
                         'rule_active': '',
                         'login_active': '',
                         }
        req = str(self.request.path).split('/')
        if 'team' in req:
            team_name = req[2]
            team = self.object_list.get(name=team_name)
        else:
            team = self.object_list[0]
        extra_context.update({'curr_team': team})
        context.update(extra_context)
        return context


class DashboardView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = "dashboard.html"
    login_url = reverse_lazy('app_users:login')
    context_object_name = 'users'

    def get_queryset(self):
        return CustomUser.objects.exclude(is_staff=True).order_by('-curr_amt',
                                                                  '-bets_won',
                                                                  'bets_lost', 'name')

    def get_context_data(self, *args, **kwargs):
        context = super(DashboardView, self).get_context_data(*args, **kwargs)
        extra_context = {'dash_active': 'active',
                         }

        # Current User Rank
        user_rank = [i+1 for i, cuser in enumerate(self.object_list)
                     if cuser == self.request.user][0]
        extra_context.update({'user_rank': user_rank})

        # Completed Match Count
        extra_context.update(
            {'match_count': Match.objects.exclude(status='S').count()})

        # Total Amount won/lost in bets
        totals = self.request.user.bets.aggregate(tot_win=Sum('win_amt'),
                                                  tot_lost=Sum('lost_amt'))
        extra_context.update({'amt_won': totals['tot_win'],
                              'amt_lost': totals['tot_lost']})

        # Next Scheduled Match
        next_match = Match.objects.filter(
            status='S').order_by(
                'num').first()
        extra_context.update({'next_match': next_match})

        # IPL Final Completed Flag
        extra_context.update(
            {'final_completed': Match.objects.get(typ='F').is_completed})

        # Pagination for Users
        extra_context.update(self.get_user_paginator(self.object_list))

        # Pagination for User Bet History
        extra_context.update(self.get_bet_paginator(self.request.user.bets))

        context.update(extra_context)
        return context

    def get_user_paginator(self, users):
        paginator = Paginator(users, 10)
        page = self.request.GET.get('page1', 1)

        try:
            context_dict = {'page1_obj': paginator.page(page),
                            }
        except PageNotAnInteger:
            context_dict = {'page1_obj': paginator.page(1)}
        except EmptyPage:
            context_dict = {'page1_obj': paginator.page(paginator.num_pages)}
        finally:
            context_dict.update({
                'user_paginator': paginator,
                'is_paginated': True
            })
            return context_dict

    def get_bet_paginator(self, bets):
        paginator = Paginator(bets, 10)
        page = self.request.GET.get('page2', 1)

        try:
            context_dict = {'page2_obj': paginator.page(page),
                            }
        except PageNotAnInteger:
            context_dict = {'page2_obj': paginator.page(1)}
        except EmptyPage:
            context_dict = {'page2_obj': paginator.page(paginator.num_pages)}
        finally:
            context_dict.update({
                'bet_paginator': paginator,
                'is_paginated': True
            })
            return context_dict

    # def get(self, request, *args, **kwargs):
    #     self.object_list = self.get_queryset()
    #     context = self.get_context_data(**kwargs)
    #     extra_context = {'sch_active': '',
    #                      'dash_active': 'active',
    #                      'home_active': '',
    #                      'admin_active': '',
    #                      'rule_active': '',
    #                      'login_active': '',
    #                      }

        # Completed Match Count
        # match_count = Match.objects.exclude(status='S').count()
        # extra_context.update({'match_count': match_count})

        # Current User Rank
        # for i, cuser in enumerate(self.object_list):
        #     if cuser == request.user:
        #         extra_context.update({'user_rank': i+1})

        # Current User Bets
        # bets = Bet.objects.filter(user=request.user).select_related('user',
        #                                                             'match', 'bet_team')
        # extra_context.update({'bets': bets})

        # Number of Bets Placed
        # bet_count = bets.exclude(match__isnull=True).count()
        # extra_context.update({'bet_count': bet_count})

        # Total Amount won in bets
        # amt_won = bets.aggregate(tot_win=Sum('win_amt'))['tot_win']
        # extra_context.update({'amt_won': amt_won})

        # Total Amount lost in bets
        # amt_lost = bets.aggregate(tot_lost=Sum('lost_amt'))['tot_lost']
        # extra_context.update({'amt_lost': amt_lost})

        # Next Scheduled Match
        # next_match = Match.objects.filter(datetime__gt=timezone.localtime(),
        #                                   status='S').order_by('num')[0]
        # extra_context.update({'next_match': next_match})

        # IPL Final Completed Flag
        # final_completed = Match.objects.get(typ='F').is_completed
        # extra_context.update({'final_completed': final_completed})

        # Pagination for Users and  Bet History
    #     extra_context.update({'bets': self.get_queryset_paginator(queryset=bets,
    #                                                               page_obj='pred_page')})
    #     extra_context.update({'users': self.get_queryset_paginator(queryset=self.object_list,
    #                                                                page_obj='user_page')})

    #     context.update(extra_context)
    #     return self.render_to_response(context)

    # def get_queryset_paginator(self, queryset, page_obj):
    #     if page_obj == 'user_page':
    #         user_paginator = Paginator(queryset, 10)
    #         user_page_num = self.request.GET.get(page_obj)
    #         return self.get_page_objects(user_paginator, user_page_num)
    #     if page_obj == 'pred_page':
    #         bet_paginator = Paginator(queryset, 10)
    #         bet_page_num = self.request.GET.get(page_obj)
    #         return self.get_page_objects(bet_paginator, bet_page_num)

    # def get_page_objects(self, paginator, page_num):
    #     try:
    #         page_obj = paginator.page(page_num)
    #         return page_obj
    #     except PageNotAnInteger:
    #         page_obj = paginator.page(1)
    #         return page_obj
    #     except EmptyPage:
    #         page_obj = paginator.page(paginator.num_pages)
    #         return page_obj


class TeamChangeView(LoginRequiredMixin, FormView):
    model = CustomUser
    template_name = "team_chg.html"
    login_url = reverse_lazy('app_users:login')
    form_class = TeamChangeForm

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        extra_context = {'sch_active': '',
                         'dash_active': 'active',
                         'home_active': '',
                         'admin_active': '',
                         'rule_active': '',
                         'login_active': '',
                         'user': self.request.user,
                         'change_text': self.get_change_text()
                         }

        context.update(extra_context)
        return self.render_to_response(context)

    def get_change_text(self):
        # Get all completed matches count
        complete_count = Match.objects.exclude(status='S').count()

        # No amount to be deducted when bet changed within first 12 matches
        if complete_count < 12:
            change_amt = 0
        else:
            change_amt = complete_count*5

        if self.request.method == 'POST':
            return f"{change_amt} points deducted from your account.", change_amt
        else:
            return f"{change_amt} points will be deducted for this change."

    @ transaction.atomic
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = TeamChangeForm(request.POST)

        extra_context = {'sch_active': '',
                         'dash_active': 'active',
                         'home_active': '',
                         'admin_active': '',
                         'rule_active': '',
                         'login_active': '',
                         'user': self.request.user,
                         'form': form,
                         }
        if form.is_valid():
            # Get message for amount deduction
            change_text, change_amt = self.get_change_text()
            extra_context.update({'change_text': change_text})

            # Get value of new team from form
            team = form.cleaned_data.get('team')
            if team == self.request.user.team:
                extra_context.update({'message': f'New value same as current',
                                      'msg_status': 'danger'})
            else:
                # Insert audit details for team change
                TeamChangeAudit.objects.create(user=self.request.user,
                                               old_team=self.request.user.team,
                                               new_team=team, amt_deducted=change_amt)

                # Save changes to User table
                self.request.user.team = team
                self.request.user.team_chgd = True
                self.request.user.curr_amt = F('curr_amt') - change_amt
                self.request.user.save(update_fields=['team',
                                                      'curr_amt', 'team_chgd'])

                # Update Pooled amount in Static table
                static_ = Static.objects.get(entry='Pool-Amount')
                static_.value = F('value') + change_amt
                static_.save(update_fields=['value'])

                # Update team on original bet placed for IPL Winner
                bet = Bet.objects.get(
                    user=self.request.user, match__isnull=True)
                bet.bet_team = team
                bet.save(update_fields=['bet_team'])

                extra_context.update({'message': f'Winner for IPL changed to {team}',
                                      'msg_status': 'success',
                                      'change_text': change_text, })

        context.update(extra_context)
        return render(request, self.template_name, context)


class RulesView(TemplateView):
    template_name = 'rules.html'

    def get(self, request, *args, **kwargs):
        extra_context = {'sch_active': '',
                         'dash_active': '',
                         'home_active': '',
                         'admin_active': '',
                         'rule_active': 'active',
                         'login_active': '',
                         }
        context = self.get_context_data(**kwargs)
        context.update(extra_context)
        return self.render_to_response(context)
