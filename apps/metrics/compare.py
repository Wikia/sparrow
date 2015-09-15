from testrunner.metric_sets import StableMetricSet


def val_to_str(value, all_values):
    are_ints = all([abs(int(x) - x) < 1e-9 for x in all_values])
    if are_ints:
        format_str = '{:d}'
        value = int(value + 1e-9)
    else:
        x = min(all_values)
        if x > 100:
            format_str = '{:d}'
            value = int(value + 1e-9)
        else:
            format_str = '{:.3f}'
    return format_str.format(value)


class Compare(object):
    def __init__(self, test_runs):
        self.test_runs = test_runs
        self.stats_list = [StableMetricSet(test_run.get_metrics()).items for test_run in test_runs]

        if len(self.stats_list) != 2:
            raise ValueError("Currently only comparing two stats sets is supported!")

    def get_comparison(self):
        all_keys = set()
        for items in self.stats_list:
            all_keys.update(items.keys())

        compare_result_set = CompareResultSet(self.test_runs)
        for key in all_keys:
            stats = [items.get(key) for items in self.stats_list]
            compare_result_set[key] = CompareResult(key, stats)

        return compare_result_set


class CompareResultSet(dict):
    def __init__(self, test_runs, *args, **kwargs):
        super(CompareResultSet, self).__init__(*args, **kwargs)
        self.test_runs = test_runs

    def get_github_markdown(self):
        ICONS = {
            0:  ':heavy_minus_sign:',
            1:  ':chart:',
            -1: ':x:'
        }
        s = [
            'Metric | | {} | % | {}'.format(*[test_run.name for test_run in self.test_runs]),
            '--- |:---:| ---:| ---:|---:'
        ]
        for key, res in sorted(self.items(), key=lambda kv: kv[0]):
            s.append('{key} | {icon} | {a}{val1}{a} | {percent} | {b}{val2}{b}'.format(
                key=key,
                icon=ICONS[res.result],
                val1=res.str_values[0],
                percent=res.percentage_str,
                val2=res.str_values[1],
                a=res.markers[0],
                b=res.markers[1]
            ))
        # s.append('**SCORE** | | | | **{:+}**'.format(self.get_total_score()))
        return "\n".join(s)


    def get_total_score(self):
        return sum([x.result for x in self.values()])


class CompareResult(object):
    EPS = 1e-10

    def __init__(self, key, stats):
        self.key = key
        self.stats = stats

        self.values = [s.mean for s in stats]

        # calculate score for this comparison
        diff = self.values[0] - self.values[1]
        if abs(diff) < self.EPS:
            # first =~ second
            res = 0
        elif diff < 0:
            # first < second
            res = -1
        else:
            # first > second
            res = 1

        self.result = res

        # build string representations for values
        self.str_values = [val_to_str(v, self.values) for v in self.values]

        # calculate percentage difference
        if any([abs(x) < self.EPS for x in self.values]):
            self.percentage = None
            self.percentage_str = ''
        else:
            self.percentage = (self.values[1] - self.values[0]) / self.values[0]
            self.percentage_str = '{:+.1%}'.format(self.percentage)

        # set up markers
        self.markers = [
            '**' if self.result < 0 else '',
            '**' if self.result > 0 else ''
        ]