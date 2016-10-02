'''
Created on Jul 14, 2016

@author: Alex
'''
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
from TeamSimulation import create_matrix
import TeamSimulation

# Covers.com lists team by division, not alphabetically. This order to be used
header_listings = ['BOS', 'BRK', 'NYK', 'PHI',
                   'TOR', 'CHI', 'CLE', 'DET', 'IND', 'MIL', 'ATL', 'CHO',
                   'MIA', 'ORL', 'WAS',
                   'DEN', 'MIN', 'OKC', 'POR', 'UTA', 'GSW', 'LAC', 'LAL',
                   'PHO', 'SAC', 'DAL',
                   'HOU', 'MEM', 'NOP', 'SAS']


def team_extensions():
    # ========================================================================
    # Covers.com assigns url ids to NBA teams in what seems like an
    # inconsistent way
    # Here we find these ids from a header page so we can construct the urls
    # ========================================================================
    header_url = 'http://www.covers.com/pageLoader/pageLoader.aspx?page=/' +\
        'data/nba/teams/teams.html'
    r = requests.get(header_url)
    soup = BeautifulSoup(r.text, 'lxml')
    # The indices of the needed links on the header page
    links = soup.find_all('a')[39:69]
    return [link['href'][49:] for link in links]


def scrape_betting_lines(season):
    base_url = 'http://www.covers.com/pageLoader/pageLoader.aspx?page=/data' +\
        '/nba/teams/pastresults/' + str(season) + '-' + str(season + 1) + '/'
    team_exts = team_extensions()
    r = requests.get
    # Will store betting lines in a dict of dicts:
    # {k = franchise code: v = {k = date: v = betting line...}...}
    all_game_dicts = []
    for ext in team_exts:
        url = base_url + ext
        print url
        req = r(url)
        soup = BeautifulSoup(req.text, 'lxml')
        games = soup.find_all('tr', class_='datarow')
        game_dict = {}
        for game in games:
            raw_data = [str(tag.text).strip() for tag in game.find_all('td')]
            spread_outcome = raw_data[4][0]
            spread = raw_data[4][2:]
            o_u = raw_data[5][0]
            total = raw_data[5][2:]
            try:
                spread = float(spread)
                total = float(total)
            except ValueError:
                # 'PK' is a bookmaker abbreviation that means the spread is 0
                if spread == 'PK':
                    spread = 0
                # There are a few games where some or all data is unavailable
                else:
                    continue
            clean_data = [spread_outcome, spread, o_u, total]
            game_dict[datetime.strptime(raw_data[0], '%m/%d/%y')] =\
                clean_data
        all_game_dicts.append(game_dict)
    team_dict = dict(zip(header_listings, all_game_dicts))
    return team_dict


def build_game_list(season):
    team_dict = scrape_betting_lines(season)
    list_form = []
    # Have to do some preprocessing. Attach the franchise code and date to
    # each game listed in the inner dict of dates.  End result is a 2D list
    # that can be nicely converted to a datafame
    for franchise, games in team_dict.iteritems():
        for date, game in games.iteritems():
            list_form.append([date] + [franchise] + game)
    return list_form
    pass


def write_betting_lines(start_season, end_season):
    # Note that we refer to seasons by the year they start
    all_seasons = []
    for season in xrange(start_season, end_season + 1):
        all_seasons.extend(build_game_list(season))
    df = pd.DataFrame(all_seasons, columns=['Date', 'Franchise', 'Bet W/L',
                                            'Spread', 'Over/Under', 'Total'])
    writer = pd.ExcelWriter('BettingLines_' + str(start_season) + '_to_' +
                            str(end_season + 1) + '.xlsx')
    df.to_excel(writer, str(start_season) + '_to_' + str(end_season + 1))
    writer.save()


def collate_season_stats(start_season, end_season):
    # Call main of TeamSimulation module to establish globals
    TeamSimulation.main()
    all_seasons = []
    for season in xrange(start_season, end_season + 1):
        # Note that create_matrix refers to seasons by the year they end
        season_data, _ = create_matrix(datetime(season-1, 10, 25),
                                       datetime(season, 5, 6), season)
        all_seasons.extend(season_data)
        print 'Finished ' + str(season)
        print(len(all_seasons), len(all_seasons[0]))
    df = pd.DataFrame(all_seasons)
    writer = pd.ExcelWriter('Game_Stats_' + str(start_season-1) + '_to_' +
                            str(end_season) + '.xlsx')
    df.to_excel(writer, 'All_Franchises_All_Games')
    writer.save()
    print('Results Written')

