from bs4 import BeautifulSoup, SoupStrainer
import requests
import numpy as np
from sklearn import decomposition
from sklearn import datasets
from sklearn import linear_model, naive_bayes, metrics
'''
Created on Apr 20, 2016

@author: Alex
'''


def create_player_matrix(player_id, season, wins):
    url = 'http://www.basketball-reference.com/play-index/pgl_finder.cgi?' +\
        'request=1&player_id=' + player_id + '&match=game&year_min=' + str(season) +\
        '&year_max=' + str(season) + '&age_min=0&age_max=99&team_id=&opp_id=&' +\
        'is_playoffs=N&round_id=&game_num_type=&game_num_min=&game_num_max=&' +\
        'game_month=&game_day=&game_location=&game_result=&is_starter=&' +\
        'is_active=&is_hof=&pos_is_G=&pos_is_GF=&pos_is_F=&pos_is_FG=&' +\
        'pos_is_FC=&pos_is_C=&pos_is_CF=&c1stat=&c1comp=gt&c1val=&c2stat=&' +\
        'c2comp=gt&c2val=&c3stat=&c3comp=gt&c3val=&c4stat=&c4comp=gt&c4val=&' +\
        'order_by=pts'
    print(url)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser",
                         parse_only=SoupStrainer('tbody'))
    list_of_games = []
    target = []
    games = soup.find_all('tr')
    for game in games:
        if game["class"] == [u'', u'thead']:
            continue
        raw_game_stats = game.findAll('td')
        win = 1. if raw_game_stats[6].get_text() == 'W' else 0.
        team1_id = 1
        team2_id = 2
        #  Filter out all percentage stats, since these sometimes have None vals
        raw_game_stats = raw_game_stats[7:11] + raw_game_stats[12:14] +\
            raw_game_stats[15:17] + raw_game_stats[18:20] + raw_game_stats[21:31]
        game_stats = [team1_id] + [team2_id] + \
            [float(raw_game_stats[i].get_text()) for i in range(0, 20)]
        list_of_games.append(game_stats[0:20])
        if wins:  #  Append the binary win value as the target data
            target.append(win)
        else:  #  Append points scored by plater as the target data
            target.append(game_stats[20])
    target = np.array(target)
    data = np.array(list_of_games)
    return data, target
    pass


def train_regression_model():
    #  Create and run a regression, not classifier, to predict points per game
    #  scored by a particular player
    #  This isn't that surprising that this works well, since our variables
    #  include FG, 2P, and 3P made in the game
    #  More interesting questions: is performance of one player predictive of
    #  team's score or opposition score?
    #  Is one player's performance predictive of another's?
    X, y = create_player_matrix('curryst01', 2015, False)
    model = linear_model.PassiveAggressiveRegressor()
    model.fit(X, y)
    return model
    """pca = decomposition.PCA(n_components=6)
    principal_components = pca.fit_transform(X)
    print(principal_components)"""
    pass


def train_classifier_model():
    X, y = create_player_matrix('curryst01', 2015, True)
    pca = decomposition.PCA(n_components=3)
    principal_components = pca.fit_transform(X)
    model = naive_bayes.GaussianNB()
    model.fit(principal_components, y)
    print(principal_components.shape)
    return model
    pass


def analyze_model(model, wins):
    model = model
    validation_data, expected = create_player_matrix('curryst01', 2016, wins)
    pca = decomposition.PCA(n_components=3)
    validation_data = pca.fit_transform(validation_data)
    predictions = model.predict(validation_data)
    print(zip(predictions[20:40], expected[20:40]))
    p, r, f1, _ = metrics.precision_recall_fscore_support(expected,
                                                          predictions,
                                                          average='binary')
    print(p, r, f1)
    pass

analyze_model(train_classifier_model(), True)
