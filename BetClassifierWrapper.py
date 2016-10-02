
import pandas as pd
import StringIO
import sys
import BetClassifier
# =============================================================================
# This module wraps BetClassifier and caches the intial files to allow for
# quicker testing. Note that any change to the underlying Excel files means
# this module must be terminated and reloaded to reflect these changes
# =============================================================================
if __name__ == '__main__':
    X_cache, y_cache, val_cache, tru_cache, features = None, None, None,\
        None, None
    while True:
        # Handle the caching
        if X_cache is None:
                training_file = pd.ExcelFile('/Users/Alex/Documents/CIS192/FinalProject/Excel_Archive/Game_Stats_1990_to_2015_28JUL16.xlsx')
                validation_file = pd.ExcelFile('/Users/Alex/Documents/CIS192/FinalProject/Excel_Archive/Game_Stats_2015_to_2016_28JUL16.xlsx')
                X_cache, y_cache, features = BetClassifier.build_dataset(training_file)
                val_cache, tru_cache, _ = BetClassifier.build_dataset(validation_file)
        print("Shape of training set is {}".format(X_cache.shape))
        print("Shape of validation set is {}".format(val_cache.shape))

        # run_and_analyze handles feature selection, parameter estimation,
        # predictions, and performance eval given the raw sets from excel files
        BetClassifier.run_and_analyze(X_cache, y_cache, val_cache, tru_cache,
                                      features)

        # Reload BetClassifier and make new predictions with diff models
        s = StringIO.StringIO()
        print s.getvalue()
        print "Press enter to re-run the script"
        sys.stdin.readline()
        reload(BetClassifier)
    pass
