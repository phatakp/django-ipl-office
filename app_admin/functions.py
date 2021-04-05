from datetime import datetime

from django.db.models import Q

from .models import IPLHistory


teams = {'Mumbai Indians': 'MI',
         'Rajasthan Royals': 'RR',
         'Delhi Capitals': 'DC',
         'Delhi Daredevils': 'DC',
         'Kolkata Knight Riders': 'KKR',
         'Punjab Kings': 'PBKS',
         'Kings XI Punjab': 'PBKS',
         'Royal Challengers Bangalore': 'RCB',
         'Chennai Super Kings': 'CSK',
         'Sunrisers Hyderabad': 'SRH',
         'Deccan Chargers': 'SRH',
         'TBC': None,
         }


def valid_row(*args):
    for i, arg in enumerate(args):
        if i == 0 and 'Match' in arg:  # Match Number
            continue
        elif i == 1 and '2021' in arg:  # Match Date
            continue
        elif i in (2, 3) and arg in teams:  # Match Teams
            continue
        elif i == 4 and 'IST' in arg:  # Match Time
            continue
        elif i == 5 and arg:  # Match Venue
            continue
        else:
            return False
    return True


def match_no(num):
    return int(num.split()[1])


def match_date_time(date, time):
    date_str = date.split()
    time_str = time.split()
    tm, tz = time_str[0], time_str[1]
    tms = tm.split(':')
    day = date_str[1][:-2].zfill(2)
    date_str[1] = day
    date = ' '.join(date_str + tms)
    return datetime.strptime(date, "%A, %d %B %Y %H %M")


def match_team(Team, name):
    if name not in ('TBC', 'Pune Warriors',
                    'Rising Pune Supergiants',
                    'Rising Pune Supergiant',
                    'Gujarat Lions',
                    'Kochi Tuskers Kerala'):
        return Team.objects.get(name=teams[name])


def match_typ_and_bet(num):
    typ_and_bet = {57: ('Q1', 50),
                   58: ('E', 50),
                   59: ('Q2', 50),
                   60: ('F', 150),
                   }

    if num > 56:
        return typ_and_bet[num]
    elif num > 28:
        return ('L', 30)
    else:
        return ('L', 20)


# For History Table
def format_date(date_str):
    date = date_str.split('/')
    date[0] = date[0].zfill(2)
    date[1] = date[1].zfill(2)
    date = ' '.join(date)
    return datetime.strptime(date, "%m %d %Y").date()

# For Stats Table


def get_total_match_count_by_teams(team1, team2=None):
    if team2:
        return IPLHistory.objects.filter(Q(home_team=team1, away_team=team2) |
                                         Q(home_team=team2, away_team=team1)).count()
    else:
        return IPLHistory.objects.filter(Q(home_team=team1) |
                                         Q(away_team=team1)).count()


def get_home_match_count_by_teams(team1, team2=None):
    if team2:
        return IPLHistory.objects.filter(home_team=team1, away_team=team2).count()
    else:
        return IPLHistory.objects.filter(home_team=team1).count()


def get_away_match_count_by_teams(team1, team2=None):
    if team2:
        return IPLHistory.objects.filter(away_team=team1, home_team=team2).count()
    else:
        return IPLHistory.objects.filter(away_team=team1).count()


def get_total_win_count_by_teams(team1, team2=None):
    if team2:
        return IPLHistory.objects.filter(Q(home_team=team1, away_team=team2) |
                                         Q(home_team=team2, away_team=team1)).filter(winner=team1).count()
    else:
        return IPLHistory.objects.filter(winner=team1).count()


def get_home_win_count_by_teams(team1, team2=None):
    if team2:
        return IPLHistory.objects.filter(home_team=team1, away_team=team2, winner=team1).count()
    else:
        return IPLHistory.objects.filter(home_team=team1, winner=team1).count()


def get_away_win_count_by_teams(team1, team2=None):
    if team2:
        return IPLHistory.objects.filter(home_team=team2, away_team=team1, winner=team1).count()
    else:
        return IPLHistory.objects.filter(away_team=team1, winner=team1).count()


def get_no_result_count_by_teams(team1, team2=None):
    if team2:
        return IPLHistory.objects.filter(Q(home_team=team1, away_team=team2) |
                                         Q(home_team=team2, away_team=team1)).filter(winner__isnull=True).count()
    else:
        return IPLHistory.objects.filter(Q(home_team=team1) |
                                         Q(away_team=team1)).filter(winner__isnull=True).count()


def get_bat1st_win_count_by_teams(team1, team2=None):
    if team2:
        return IPLHistory.objects.filter(Q(home_team=team1, away_team=team2) |
                                         Q(home_team=team2, away_team=team1)).filter(winner=team1,
                                                                                     bat_first=team1).count()
    else:
        return IPLHistory.objects.filter(winner=team1, bat_first=team1).count()


def get_bat2nd_win_count_by_teams(team1, team2=None):
    if team2:
        return IPLHistory.objects.filter(Q(home_team=team1, away_team=team2, winner=team1) |
                                         Q(home_team=team2, away_team=team1, winner=team1)).exclude(
                                             bat_first=team1).count()
    else:
        return IPLHistory.objects.filter(winner=team1).exclude(bat_first=team1).count()


def get_last5_count_by_teams(team1, team2=None):
    if team2:
        last5 = IPLHistory.objects.filter(Q(home_team=team1, away_team=team2) |
                                          Q(home_team=team2, away_team=team1)).exclude(winner__isnull=True).order_by('-date')[:5]
    else:
        last5 = IPLHistory.objects.filter(Q(home_team=team1) |
                                          Q(away_team=team1)).exclude(winner__isnull=True).order_by('-date')[:5]
    wins = 0
    for match in last5:
        if match.winner == team1:
            wins += 1

    return wins
