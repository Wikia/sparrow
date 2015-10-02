(function (window) {
    var View = window.Sparrow.View,
        Api = window.Sparrow.Api,
        Metrics = window.Sparrow.Metrics,
        Actions = {},
        Data = {
            compareRequests: [],
            testResultsError: false,
            testResults: []
        };

    Actions.init = function () {
        Actions.render();
        setTimeout(Actions.loadCompareRequests, 0);
    };

    Actions.loadCompareRequests = function () {
        startLoading();
        Api.CompareRequest.list(100).allAtOnce(function (l) {
            Data.compareRequests = l;
            Actions.render();
        })
    };

    Actions.selectCompareRequest = function (id) {
        var compareRequest = false, i;
        for (i = 0; i < Data.compareRequests.length && Data.compareRequests[i].id != id; i++) {
        }
        if (i >= Data.compareRequests.length) {
            return;
        }
        compareRequest = Data.compareRequests[i];

        if (compareRequest) {
            $.when(compareRequest.base_test_run(), compareRequest.head_test_run())
                .done(function (base_test_run, head_test_run) {
                    var q = [base_test_run, head_test_run],
                        testRuns;
                    if (q[0].status < 2 || q[1].status < 2) {
                        var errorText = 'Ooops! Something went wrong!';
                        if (q[0].status == -1 || q[1].status == -1) {
                            errorText = 'One or more tests have failed.';
                        } else if (q[0].status != 2 || q[1].statis != -2) {
                            errorText = 'One or more tests have not yet finished.';
                        }
                        Data.testResultsError = errorText;
                        stopLoading();
                        Actions.render();
                        return;
                    }

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
                            Actions.render();
                        });
                });
        }
    };

    Actions.setServerName = function (server) {
        if (Data.serverName == server) {
            return;
        }
        Data.serverName = server;
        Api.setServer(server);
        storage.setItem(STORAGE_KEY_SERVER, server);
        Actions.loadCompareRequests();
    };

    Actions.render = function () {
        View.render(Data);
    };

    $.extend(window.Sparrow.Actions, {
        Data: Data
    }, Actions);
})(window);