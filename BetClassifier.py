'''
Created on Jul 26, 2016

@author: Alex
'''

import pandas as pd
import numpy as np
from sklearn import neighbors, metrics, feature_selection, linear_model, svm


def build_dataset(in_file):
    all_stats_df = pd.read_excel(in_file, sheetname=0)
    lopsided_lines_df = pd.read_excel(in_file, sheetname=1)
    # Get the list of feautures that will form the untransformed training set
    column_features = [str(i) for i in all_stats_df.axes[1].tolist()]
    line_dict = dict()
    for line in lopsided_lines_df.as_matrix():
        # Identify every game as the date and team id concatenated
        game_id = str(line[0]) + str(line[1])
        line_dict[game_id] = line[1:]
    training_set, target = [], []
    # Iterate through all games and look for a key in the lopsided lines
    # If key is found, add spread to game and add game to training set
    for game in all_stats_df.as_matrix():
        game_id = str(game[0]) + str(game[1])
        if game_id in line_dict:
            betting_line = line_dict.get(game_id).tolist()
            game = game.tolist()[1:]
            # Append the spread as a new game statistic
            game.append(betting_line[2])
            training_set.append(game)
            target.append(betting_line[1])
    column_features.append('Spread')
    training_set, target = np.array(training_set), np.array(target)
    return training_set, target, column_features
    pass


def run_model(X, y, validation_set):
    model = neighbors.KNeighborsClassifier()
    model.fit(X, y)
    predictions = []
    for game in validation_set:
        bet_prediction = model.predict(np.reshape(game, (1, -1)))
        predictions.append(bet_prediction)
    predictions = np.array(predictions)
    return predictions
    pass


def pick_features(X, y, features):
    estimator = svm.SVC(kernel='linear')
    selector = feature_selection.SelectFromModel(estimator,
                                                 threshold='0.25*mean')
    print 'Fitting'
    selector.fit(X, y)
    print 'Fitting Finished'
    selected_features = selector.get_support(indices=True)
    print('Features picked by Meta-transformer: {}'.format
          (len(selected_features)))
    print([features[i] for i in selected_features])
    return selector.transform(X), selector
    pass


def run_and_analyze(X_cache, y_cache, val_cache, tru_cache, features):
    X, selector = pick_features(X_cache, y_cache, features)
    # build_validation_set will go here
    val_set = selector.transform(val_cache)
    predictions = run_model(X, y_cache, val_set)
    p, r, f1, _ = metrics.precision_recall_fscore_support(tru_cache,
                                                          predictions,
                                                          average='binary')
    print 'p, r, f1 = {}'.format((p, r, f1))

if __name__ == '__main__':
    pass
