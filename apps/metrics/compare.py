from testrunner.metric_sets import BasicMetricSet


class Compare(object):
    def __init__(self, test_runs):
        self.test_runs = test_runs
        self.stats_list = [BasicMetricSet(test_run.get_metrics()).items for test_run in test_runs]

        if len(self.stats_list) != 2:
            raise ValueError("Currently only comparing two stats sets is supported!")

    def get_comparison(self):
        all_keys = set()
        for items in self.stats_list:
            all_keys.update(items.keys())

        compare_result_set = CompareResultSet(self.test_runs)
        for key in all_keys:
            stats = [items.get(key) for items in self.stats_list]
            compare_result_set[key] = CompareResult(key,stats)

        return compare_result_set


class CompareResultSet(dict):
    def __init__(self, test_runs, *args, **kwargs):
        super(CompareResultSet, self).__init__(*args, **kwargs)
        self.test_runs = test_runs

    def get_text(self):
        CMPS = {
            0: '   ',
            1: '+++',
            -1:'---'
        }
        s = []
        s.append('{:30s} {:^19s}   {:^19s}'.format('',*[test_run.main_revision for test_run in self.test_runs]))
        for key, res in self.items():
            s.append('{key:30s}:   {val1:>13.4f}   {cmp}   {val2:>13.4f}'.format(
                key=key,
                val1=res.stats[0].mean,
                val2=res.stats[1].mean,
                cmp=CMPS[res.result]
            ))
        return "\n".join(s)

    def get_total_score(self):
        return sum([x.result for x in self.values()])

class CompareResult(object):
    def __init__(self, key, stats):
        self.key = key
        self.stats = stats

        val1 = self.stats[0].mean
        val2 = self.stats[1].mean
        if abs(val1-val2) < 1e-6:
            res = 0
        elif val1 < val2:
            res = -1
        else:
            res = 1

        self.result = res
