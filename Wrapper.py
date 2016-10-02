import TeamSimulation
import sys
import cProfile
import pstats
import StringIO
import pandas as pd

training_set_cache = None
writer = None
if __name__ == '__main__':
    while True:
        if training_set_cache is None:
            num_cache, code_cache, num_to_code_cache = TeamSimulation.main()
            training_set_cache, target_cache = TeamSimulation.initialize()
            writer = pd.ExcelWriter('Predictions_Lines_Comparison.xlsx')
        print('Cache Established')
        pr = cProfile.Profile()
        pr.enable()
        TeamSimulation.run_and_analyze(training_set_cache, target_cache, num_cache, code_cache, num_to_code_cache, writer)
        pr.disable()
        s = StringIO.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats()
        print s.getvalue()
        print "Press enter to re-run the script, CTRL-C to exit"
        sys.stdin.readline()
        reload(TeamSimulation)
    pass

