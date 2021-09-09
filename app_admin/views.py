import os

from django.apps import apps
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.shortcuts import render
from django.views.generic import TemplateView

import openpyxl
import csv

from .models import IPLHistory, IPLStats
from .functions import (valid_row, match_date_time, match_no, match_team, match_typ_and_bet,
                        format_date, get_total_match_count_by_teams, get_away_match_count_by_teams,
                        get_home_match_count_by_teams, get_total_win_count_by_teams, get_home_win_count_by_teams,
                        get_away_win_count_by_teams, get_no_result_count_by_teams,
                        get_bat1st_win_count_by_teams, get_bat2nd_win_count_by_teams,
                        get_last5_count_by_teams)

Team = apps.get_model('app_main', 'Team')
Match = apps.get_model('app_matches', 'Match')
Bet = apps.get_model('app_matches', 'Bet')


class MainView(TemplateView):
    model = Match
    template_name = 'main.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        task_typ = context.get('typ', 'main')
        context['message'] = self.branch_to_task(task_typ)
        return self.render_to_response(context)

    def branch_to_task(self, task):
        if task == 'matchup':
            return self.upload_match_table()
        elif task == 'history':
            return self.upload_history_table()
        elif task == 'stats':
            return self.upload_stats_table()

    def delete_bets(self):
        bets = Bet.objects.filter(match__num__gt=29)
        for bet in bets:
            bet.user.curr_amt = F('curr_amt') + bet.bet_amt
            bet.user.save(update_fields=['curr_amt'])
            bet.delete()

    @transaction.atomic
    def upload_match_table(self):
        # Clear the Match Table
        # Match.objects.all().delete()
        self.delete_bets()
        Match.objects.filter(num__gt=29).delete()
        records = []

        excel_path = os.path.join(
            settings.BASE_DIR, 'Matches1.xlsx')
        wb = openpyxl.load_workbook(excel_path)
        ws = wb.active

        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i > 0:
                if valid_row(*row):
                    num = match_no(row[0])
                    date = match_date_time(row[1], row[4])
                    hteam = match_team(Team, row[2])
                    ateam = match_team(Team, row[3])
                    venue = row[5]
                    typ, min_bet = match_typ_and_bet(num)

                    if hteam and ateam:
                        records.append(Match(num=num, datetime=date,
                                             home_team=hteam, away_team=ateam,
                                             venue=venue, typ=typ, min_bet=min_bet))
                    else:
                        records.append(Match(num=num, datetime=date,
                                             venue=venue, typ=typ, min_bet=min_bet))
                else:
                    return f"Invalid row {row}"

        msg = Match.objects.bulk_create(records)
        return f'{len(msg)} Matches successfully uploaded'

    @transaction.atomic
    def upload_history_table(self):
        # Clear the History Table
        IPLHistory.objects.all().delete()
        records = []

        csv_path = os.path.join(
            settings.BASE_DIR, 'IPL_History.csv')
        with open(csv_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            # row = date, venue, neutral_venue, team1, team2, toss_winner, toss_decision, winner, result, result_margin, eliminator
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:
                    date = format_date(row[0])
                    venue = row[1]
                    hteam = match_team(Team, row[3])
                    ateam = match_team(Team, row[4])
                    if hteam and ateam:
                        toss_winner = match_team(Team, row[5])

                        # Batting first
                        if row[6] == 'bat':
                            bat_first = toss_winner
                        elif row[6] == 'field' and toss_winner == hteam:
                            bat_first = ateam
                        elif row[6] == 'field':
                            bat_first == hteam

                        if row[7] == 'NA':
                            winner = None
                            result = 'Match Abandoned'
                            status = 'A'
                        else:
                            winner = match_team(Team, row[7])
                            result = f'{winner.name} won by {row[9]} {row[8]}'
                            status = 'C'

                        records.append(IPLHistory(date=date, home_team=hteam, away_team=ateam,
                                                  venue=venue, status=status, winner=winner,
                                                  result=result, bat_first=bat_first))

        msg = IPLHistory.objects.bulk_create(records)
        return f'{len(msg)} Matches successfully uploaded'

    @transaction.atomic
    def upload_stats_table(self):
        # Clear the Stats Table
        IPLStats.objects.all().delete()
        records = []
        teams = Team.objects.all()
        for team1 in teams:
            records.append(IPLStats(team=team1,
                                    all_matches=get_total_match_count_by_teams(
                                        team1),
                                    home_matches=get_home_match_count_by_teams(
                                        team1),
                                    away_matches=get_away_match_count_by_teams(
                                        team1),
                                    all_wins=get_total_win_count_by_teams(
                                        team1),
                                    home_wins=get_home_win_count_by_teams(
                                        team1),
                                    away_wins=get_away_win_count_by_teams(
                                        team1),
                                    no_result=get_no_result_count_by_teams(
                                        team1),
                                    bat_1st_wins=get_bat1st_win_count_by_teams(
                                        team1),
                                    bat_2nd_wins=get_bat2nd_win_count_by_teams(
                                        team1),
                                    last5_wins=get_last5_count_by_teams(
                                        team1)
                                    )
                           )
            for team2 in teams:
                if team1 != team2:
                    records.append(IPLStats(team=team1, vs_team=team2,
                                            all_matches=get_total_match_count_by_teams(
                                                team1, team2),
                                            home_matches=get_home_match_count_by_teams(
                                                team1, team2),
                                            away_matches=get_away_match_count_by_teams(
                                                team1, team2),
                                            all_wins=get_total_win_count_by_teams(
                                                team1, team2),
                                            home_wins=get_home_win_count_by_teams(
                                                team1, team2),
                                            away_wins=get_away_win_count_by_teams(
                                                team1, team2),
                                            no_result=get_no_result_count_by_teams(
                                                team1, team2),
                                            bat_1st_wins=get_bat1st_win_count_by_teams(
                                                team1, team2),
                                            bat_2nd_wins=get_bat2nd_win_count_by_teams(
                                                team1, team2),
                                            last5_wins=get_last5_count_by_teams(
                                                team1, team2)
                                            )
                                   )

        msg = IPLStats.objects.bulk_create(records)
        return f'{len(msg)} Records successfully uploaded'
