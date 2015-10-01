(function (window) {
    var View = window.Sparrow.View,
        Api = window.Sparrow.Api,
        Metrics = window.Sparrow.Metrics,
        Actions = {},
        Data = {
            loading: 0,
            compareRequests: [],
            testResultsError: false,
            testResults: []
        };

    Actions.init = function () {
        startLoading();
        Api.CompareRequest.list().allAtOnce(function (l) {
            Data.compareRequests = l;
            stopLoading();
            Actions.render();
        })
    };

    function startLoading() {
        Data.loading++;
        View.setLoading(Data.loading);
    }
    function stopLoading() {
        Data.loading--;
        View.setLoading(Data.loading);
    }

    Actions.selectCompareRequest = function (id) {
        var compareRequest = false, i;
        for (i = 0; i < Data.compareRequests.length && Data.compareRequests[i].id != id; i++) {
        }
        if (i >= Data.compareRequests.length) {
            return;
        }
        compareRequest = Data.compareRequests[i];

        if (compareRequest) {
            startLoading();
            $.when(compareRequest.base_test_run(), compareRequest.head_test_run())
                .done(function (base_test_run, head_test_run) {
                    var q = [base_test_run, head_test_run],
                        testRuns;
                    q = q.filter(function (e) {
                        return e.results.length > 0;
                    });
                    testRuns = [].concat(q);
                    q = q.map(function (e) {
                        return e.results[0]();
                    });
                    if (q.length == 0) {
                        Data.testResultsError = 'No results available for the selected comparison';
                        Actions.render();
                        return;
                    }
                    $.when.apply($, q)
                        .done(function () {
                            var results = Array.prototype.slice.call(arguments, 0);
                            Data.testResultsError = false;
                            Data.testResults = new Metrics.CollectionComparison(
                                results.map(function(result,i){
                                    return new Metrics.Collection(result, testRuns[i]);
                                })
                            );
                            stopLoading();
                            Actions.render();
                        })
                        .fail(stopLoading);
                })
                .fail(stopLoading);
        }
    };

    Actions.render = function () {
        View.render(Data);
    };

    $.extend(window.Sparrow.Actions, {
        Data: Data
    }, Actions);
})(window);