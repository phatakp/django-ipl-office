from django.db.models import Sum, F
from django.utils import timezone

from .models import Bet
from app_main.models import Static
from app_users.models import CustomUser
from app_admin.models import IPLHistory, IPLStats
from app_admin.functions import (get_total_match_count_by_teams, get_away_match_count_by_teams,
                                 get_home_match_count_by_teams, get_total_win_count_by_teams, get_home_win_count_by_teams,
                                 get_away_win_count_by_teams, get_no_result_count_by_teams,
                                 get_bat1st_win_count_by_teams, get_bat2nd_win_count_by_teams,
                                 get_last5_count_by_teams)


def reduce_from_user(user, amt):
    user.curr_amt = F('curr_amt') - amt
    user.save(update_fields=['curr_amt'])

# Change Amount and/or Team on Bet table


def update_bet_details(bet, team):
    bet.bet_amt = bet.match.min_bet
    bet.bet_team = team
    bet.create_time = timezone.localtime()
    bet.save(update_fields=['bet_amt', 'bet_team', 'create_time'])

    reduce_from_user(bet.user, amt=10)
    Static.objects.get(
        entry='Pool-Amount').update(value=F('value')+10)
# Insert into Bet table


def insert_bet_details(user, match, team, default=False):
    Bet.objects.create(user=user, match=match, bet_amt=match.min_bet,
                       bet_team=team, status="D" if default else "P",
                       create_time=timezone.localtime())
    reduce_from_user(user, amt=match.min_bet)

# Valid placed bet for a match


def bet_for_match_exists(user, match):
    return Bet.objects.filter(user=user,
                              match=match, status='P').exists()


def validate_and_save_bet(user, match, team):
    if bet_for_match_exists(user, match):
        if match.isWithinTime:  # Match start time / Bet change cutoff

            # New amount should atleast be double of existing bet amount
            bet = Bet.objects.get(user=user, match=match)
            update_bet_details(bet, team)
            return f"Changed Prediction: {team.name}", True
        else:
            return f"Past cutoff for Prediction change", False

    # No existing bet
    elif match.isWithinBetCutoff:  # within 60mins

        insert_bet_details(user, match, team)
        return f"Current Prediction: {team.name}", True
    else:
        return f"Past cutoff for Prediction", False

# For / Against status calculation


def get_new_status(team, match_status, against=True):
    match_runs = int(match_status.split('/')[0])
    match_balls = float(match_status.split('/')[1])

    if against:
        curr_status = team.against_status
    else:
        curr_status = team.for_status

    if curr_status:
        curr_runs = int(curr_status.split('/')[0])
        curr_balls = float(curr_status.split('/')[1])
        new_status = f"{curr_runs+match_runs}/{curr_balls+match_balls}"
        return new_status
    else:
        new_status = f"{match_runs}/{match_balls}"
        return new_status

# NRR calculation


def get_nrr(for_status, against_status):
    # NRR = For Runs / For Overs - Against Runs / Against Overs
    for_runs = int(for_status.split('/')[0])
    for_balls = float(for_status.split('/')[1])
    against_runs = int(against_status.split('/')[0])
    against_balls = float(against_status.split('/')[1])
    for_rr = for_runs/for_balls
    against_rr = against_runs/against_balls
    return for_rr - against_rr


def update_team_table(team, for_score=None, against_score=None, win=True, abandoned=False):
    team.played = F('played') + 1
    if abandoned:  # For abandoned match
        team.no_res = F('no_res') + 1
        team.points = F('points') + 1
        team.save(update_fields=['played', 'no_res', 'points'])
    else:  # For completed match
        team.for_status = get_new_status(team, for_score, against=False)
        team.against_status = get_new_status(team, against_score)
        team.nrr = get_nrr(team.for_status, team.against_status)

        if win:
            team.won = F('won') + 1
            team.points = F('points') + 2
        else:
            team.lost = F('lost') + 1

        team.save(update_fields=['played', 'won', 'lost', 'points',
                                 'nrr', 'for_status', 'against_status'])


def update_team_info(match, winner, home_score, away_score):
    # Home Team Winner
    if winner and winner == match.home_team:
        update_team_table(match.home_team, home_score, away_score, win=True)
        update_team_table(match.away_team, away_score, home_score, win=False)
    # Away Team Winner
    if winner and winner == match.away_team:
        update_team_table(match.home_team, home_score, away_score, win=False)
        update_team_table(match.away_team, away_score, home_score, win=True)
    # Match Abandoned
    elif not winner:
        update_team_table(match.home_team, abandoned=True)
        update_team_table(match.away_team, abandoned=True)


def update_match_info(match, winner, result, home_score, away_score):
    if winner:  # Completed Match
        match.winner = winner
        match.status = 'C'
        match.result = result
        match.home_team_score = home_score
        match.away_team_score = away_score
        match.save(update_fields=['winner', 'status', 'result',
                                  'home_team_score', 'away_team_score'])
    else:  # Abandoned Match
        match.status = 'A'
        match.result = 'Match Abandoned'
        match.save(update_fields=['status', 'result', ])

    # Update Team table only for league matches
    if match.is_league:
        update_team_info(match, winner, home_score, away_score)
    return match


def update_bet_table(bet, amt, win=True):
    if win:
        bet.win_amt = amt
        bet.status = 'W'

        # Increment user total amount
        user = bet.user
        user.curr_amt = F('curr_amt') + amt
        user.bets_won = F('bets_won') + 1

        # Save to DB
        bet.save(update_fields=['win_amt', 'status'])
        user.save(update_fields=['curr_amt', 'bets_won'])
    else:
        bet.lost_amt = amt
        bet.status = 'L'

        # Decrease user total amount
        user = bet.user
        user.bets_lost = F('bets_lost') + 1

        # Save to DB
        bet.save(update_fields=['lost_amt', 'status'])
        user.save(update_fields=['bets_lost'])


def settle_bets(match, winner):
    # Get all bets for Match
    match_bets = Bet.objects.filter(match=match).select_related('user',
                                                                'match', 'bet_team')
    total_bet_amt = match_bets.aggregate(
        tot_amt=Sum('bet_amt'))['tot_amt']

    if winner:  # Match Completed
        # Get winning bets and losing bets
        winning_bets = match_bets.filter(bet_team=winner)
        losing_bets = match_bets.exclude(bet_team=winner)

        # Get total win amount and total loss amount
        winners = winning_bets.count()

        if winners:  # Winner found
            for bet in winning_bets:
                amt = total_bet_amt / winners
                update_bet_table(bet, amt, win=True)
            for bet in losing_bets:
                update_bet_table(bet, bet.bet_amt, win=False)
        else:  # All losers (bet on same time)
            for bet in match_bets:
                bet.status = 'R'
                bet.save(update_fields=['status'])
            static_ = Static.objects.get(
                entry='Pool-Amount')
            static_.value = F('value')+total_bet_amt
            static_.save(update_fields=['value'])

    else:  # Match Abandoned
        for bet in match_bets:
            bet.status = 'R'
            bet.save(update_fields=['status'])
        static_ = Static.objects.get(
            entry='Pool-Amount')
        static_.value = F('value')+total_bet_amt
        static_.save(update_fields=['value'])


def add_default_bets(match):
    # Add default bets for all players where no match bet exists
    all_users = CustomUser.objects.exclude(is_staff=True)
    for user in all_users:
        if not bet_for_match_exists(user, match):
            insert_bet_details(user, match,
                               team=None, default=True)


def default_bets_placed(match):
    # Check if number of bets for match is same as number of players
    player_count = CustomUser.objects.exclude(is_staff=True).count()
    bet_placed_count = Bet.objects.filter(match=match).count()
    return player_count == bet_placed_count


def valid_score(score):
    if score and '/' in score:
        vals = score.split('/')
        try:
            vals[0] = int(vals[0])
            vals[1] = float(vals[1])
            return True
        except:
            return False
    else:
        return False


def valid_result(match, winner, result):
    if result:
        if winner:
            for name in (match.home_team.name, match.away_team.name):
                if name in result and 'won' in result:
                    return True
        elif 'Match' in result:
            return True
    return False


def valid_winner(match, winner):
    return not winner or (winner and winner in (match.home_team, match.away_team))


def insert_to_history(match):
    if match.winner:
        if 'runs' in match.result:
            bat_first = match.winner
        elif match.winner == match.home_team:
            bat_first = match.away_team
        else:
            bat_first = match.home_team
    else:
        bat_first = None
    IPLHistory.objects.create(date=match.datetime.date(),
                              home_team=match.home_team,
                              away_team=match.away_team,
                              venue=match.venue,
                              status=match.status,
                              winner=match.winner,
                              result=match.result,
                              bat_first=bat_first)


def update_stats(match):
    for team1 in (match.home_team, match.away_team):
        IPLStats.objects.filter(team=team1, vs_team__isnull=True).update(
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
        for team2 in (match.home_team, match.away_team):
            IPLStats.objects.filter(team=team1, vs_team=team2).update(
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


def validate_and_save_match_winner(match, winner, result, home_score, away_score):
    if valid_winner(match, winner):
        if valid_result(match, winner, result):
            if (winner and valid_score(home_score) and valid_score(away_score)) or not winner:
                if not default_bets_placed(match):
                    add_default_bets(match)

                # Calculate and settle bet amounts
                settle_bets(match, winner)

                # Update Match status
                match = update_match_info(match, winner, result,
                                          home_score, away_score)
                # Insert Match details to history
                insert_to_history(match)

                # Update Stats
                update_stats(match)
                return f'Match Details Updated successfully ', True
            else:
                return f'Invalid Score - {home_score} or {away_score}', False
        else:
            return f'Invalid Result - {result}', False
    else:
        return f'Invalid Winner Selected - {winner.name}', False

# Settle bets for IPL Winner


def update_final_match(winner):
    # Get pooled amount from Static table
    pool_amount = Static.objects.get(
        entry='Pool-Amount').value

    # Get all bets for IPL Winner
    match_bets = Bet.objects.filter(match__isnull=True).select_related('user',
                                                                       'match', 'bet_team')
    total_bet_amt = match_bets.aggregate(tot_amt=Sum('bet_amt'))['tot_amt']

    if winner:  # Match Completed

        # Get winning bets and losing bets
        winning_bets = match_bets.filter(bet_team=winner)
        losing_bets = match_bets.exclude(bet_team=winner)
        winners = winning_bets.count()

        if winners:  # Winner found
            total_bet_amt += pool_amount
            for bet in winning_bets:
                amt = total_bet_amt / winners
                update_bet_table(bet, amt, win=True)
            for bet in losing_bets:
                update_bet_table(bet, bet.bet_amt, win=False)

        elif pool_amount:
            winning_bets = match_bets.filter(user__team_chgd=False)
            losing_bets = match_bets.filter(user__team_chgd=True)
            winners = winning_bets.count()
            if winners:
                for bet in winning_bets:
                    amt = pool_amount / winners
                    update_bet_table(bet, amt, win=True)
            for bet in losing_bets:
                bet.status = 'R'
                bet.save(update_fields=['status'])

        else:  # All winners (bet on same time)
            for bet in match_bets:
                bet.status = 'R'
                bet.save(update_fields=['status'])

    elif pool_amount:
        winning_bets = match_bets.filter(user__team_chgd=False)
        losing_bets = match_bets.filter(user__team_chgd=True)
        winners = winning_bets.count()
        if winners:  # Players who did not change IPL winner
            for bet in winning_bets:
                amt = pool_amount / winners
                update_bet_table(bet, amt, win=True)
        for bet in losing_bets:
            bet.status = 'R'
            bet.save(update_fields=['status'])
    else:
        for bet in match_bets:
            bet.status = 'R'
            bet.save(update_fields=['status'])
