from django import template
from django.db.models import Q, Sum
from app_main.models import Static
from app_matches.models import Bet

import math

register = template.Library()


@register.filter
def first(name):
    return name.split()[0].capitalize()


@register.filter
def last(name):
    last_name = name.split()
    if len(last_name) > 1:
        return last_name[-1].capitalize()
    else:
        return ''


@register.filter
def abbr(name):
    names = name.split()
    if len(names) > 1:
        return names[0] + ' ' + names[-1][0]
    else:
        return names[0]


@register.filter
def minus100(value):
    return 100-value


@register.filter
def form_guide(user):
    return Bet.objects.filter(user=user).exclude(Q(match__isnull=True) |
                                                 Q(match__status='S')).select_related('user',
                                                                                      'match',
                                                                                      'bet_team').order_by('-match__num')[:5]


@register.filter
def remain_count(user):
    return [str(i) for i in range(5-form_guide(user).count())]


@register.filter
def ipl_winner_bet(user):
    bet = Bet.objects.get(user=user, match__isnull=True)
    return bet.win_amt if bet.status == 'W' else bet.lost_amt * -1


@register.filter
@register.filter
def ipl_kitty(user):
    pool_amt = Static.objects.get(entry='Pool-Amount').value
    bet_amt = Bet.objects.filter(
        match__isnull=True).aggregate(tot_amt=Sum('bet_amt'))['tot_amt']
    if bet_amt:
        return int(pool_amt + bet_amt)
    else:
        return pool_amt


@register.filter
def on_page(counter, page):
    if not page:
        page = 1

    return (page-1) * 10 + counter
