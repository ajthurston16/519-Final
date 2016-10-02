'''
Created on Jul 9, 2016

@author: Alex
'''
import requests
from bs4 import BeautifulSoup
from TeamSimulation import code_to_number, number_to_code, num_wins
import TeamSimulation
import numpy as np
import pandas as pd
import cProfile
import pstats
import StringIO
import sys
import datetime


def pace_off_def_ratings():
    stats_list = []
    url_base = 'http://www.basketball-reference.com/play-index/tsl_finder.cgi?request=1&match=single&type=advanced&lg_id=NBA&year_min=2015&year_max=2015&franch_id=&c1stat=&c1comp=gt&c1val=&c2stat=&c2comp=gt&c2val=&c3stat=&c3comp=gt&c3val=&c4stat=&c4comp=gt&c4val=&order_by=team_name'
    r = requests.get(url_base)
    soup = BeautifulSoup(r.text, 'lxml')
    teams = soup.findAll("tr", class_=[u''])[2:]
    for team in teams:
        if team['class'] == [u'', u'thead']:
            continue
        raw_stats = team.find_all("td")
        # The strength of schedule, pace/tempo per 48 mins, the defensive and
        # offensive efficiences
        sos, pace_48, off_eff_100, def_eff_100 =\
            float(raw_stats[9].get_text()),\
            float(raw_stats[11].get_text()),\
            float(raw_stats[12].get_text()),\
            float(raw_stats[13].get_text())
        stats_list.append((sos, pace_48, off_eff_100, def_eff_100))
    id_to_ratings = dict(zip(xrange(29, -1, -1), stats_list))
    return id_to_ratings


def calculate_percentages():
    # Find the NBA average pace/defensive/offensive ratings, and use these to
    # give each team an over/under percentage
    id_to_ratings = pace_off_def_ratings()
    avg_pace = sum(b for _, b, _, _ in id_to_ratings.values()) / 30
    avg_off = sum(c for _, _, c, _ in id_to_ratings.values()) / 30
    avg_def = sum(d for _, _, _, d in id_to_ratings.values()) / 30
    averages_listed = list((a, b / avg_pace, c / avg_off, d / avg_def) for a, b, c, d in id_to_ratings.values())
    id_to_percentage = dict(zip(xrange(0, 30), averages_listed))
    return id_to_percentage, (avg_pace, avg_off, avg_def)


def final_score(team1_pcts, team2_pcts, avgs):
    # Given two teams percentages, calculate their expected outputs
    # Team 1 output = team 1 off_pct * team 2 def_pct * NBA avg off_pts
    team1_output = team1_pcts[2] * team2_pcts[3] * avgs[1]
    team2_output = team2_pcts[2] * team1_pcts[3] * avgs[1]
    # Next, calculate expected pace
    expected_pace = team1_pcts[1] * team2_pcts[1] * avgs[0]
    # Return the final scores, normalized from 100 posessions to the expected
    # pace of the game
    return (team1_output * (expected_pace / 100), team2_output *
            (expected_pace / 100))


def simulation(all_games):
    # Note these are the 2016 averages, and we are making a prediction on the
    # 2016 season for testing purposes
    pcts, avgs = calculate_percentages()
    table_format = []
    # Initialize a table format here
    # This cuts down on function references, but not as quick as a list comp
    extend_table = table_format.extend
    for game in all_games:
        team_id, opp_id = game[0], game[1]
        target = game[15] - game[42]
        team_output, opp_output = final_score(pcts[team_id],
                                              pcts[opp_id], avgs)
        extend_table([number_to_code[team_id], team_output - opp_output,
                      target])
    table_format = np.reshape(table_format, (-1, 3))
    return table_format
pass


def initialize():
    # Borrow from TeamSimulation to create a cache of seasonal games
    # DON'T FORGET TO CHANGE THE DATES IF YOU WANT THIS CACHE TO BE FOR 2015-6
    global code_to_number
    global number_to_code
    _, code_to_number, number_to_code = TeamSimulation.main()
    from_date = datetime.datetime(2015, 10, 27)
    to_date = datetime.datetime(2016, 4, 14)
    all_games, _ = TeamSimulation.create_matrix(from_date, to_date, 2016)
    print ('Training set is shape {}').format(all_games.shape)
    return all_games
    pass

# Don't think the cache is actually working here. Problem with local variables
def wrapper():
    all_games_cache = None
    writer = None
    while True:
        if all_games_cache is None:
            all_games_cache = initialize()
            writer = pd.ExcelWriter('Pythag_Spread_Results.xlsx')
        print('Cache Established')
        pr = cProfile.Profile()
        pr.enable()
        table_format = simulation(all_games_cache)
        # Write results to an excel file, which is done with the pandas package
        table = pd.DataFrame(table_format, columns=['Team', 'Prediction',
                                                'Target'])
        table.to_excel(writer,'S2016_PCTS2015')
        writer.save()
        print('Results Written')
        pr.disable()
        s = StringIO.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats()
        print s.getvalue()
        print "Press enter to re-run the script, CTRL-C to exit"
        sys.stdin.readline()
        reload(TeamSimulation)
    pass


wrapper()
