(function () {
    var Config = {
            apiUrl: '/api/v1/'
        },
        Api = {},
        CompareRequest, TestRun, Result, Task,
        allClasses;

    function Object_values(o) {
        return Object.keys(o).map(function (k) {
            return o[k];
        });
    }

    Api.init = function (options) {
        Config = $.extend({}, Config, options);
    };

    Api.call = function (url, method) {
        var deferred = $.Deferred();
        method = method || 'GET';
        $.ajax({
            url: url,
            method: method,
            dataType: 'json',
            success: function (r) {
                deferred.resolve(r);
            },
            error: function (r) {
                deferred.reject.apply(deferred, arguments);
            }
        });
        return deferred.promise();
    };

    Api.setServer = function(server) {
        var url = server ? ('http://' + server) : '';
        url += '/api/v1/';
        Config.apiUrl = url;
    };

    function getEntity(cls, id) {
        var url = (typeof id == 'string' && id.substr(0, 4) == 'http') ? id
            : Config.apiUrl + cls.API_NAME + '/' + id + '/';

        return Api.call(url).then(function (r) {
            var o = new cls(r);
            console.log(o);
            window.Sparrow.__last_loaded = o;
            return o;
        });
    }

    function getEntityBuilder(cls) {
        return function (id) {
            return getEntity(cls, id);
        }
    }

    function getEntityFetcher(cls, id) {
        return function () {
            return getEntity(cls, id);
        }
    }

    function createEntityClass() {
        return function (data) {
            this.__data = data;
            this.init();
        }
    }

    var PagedList;

    PagedList = function (cls) {
        this.childCls = cls;
        this.nextUrl = Config.apiUrl + cls.API_NAME + '/';
        this.currentPage = [];
        this.currentIndex = 0;

    };
    PagedList.prototype.next = function () {
        var deferred = $.Deferred(),
            cls = this.childCls;
        if (this.currentIndex < this.currentPage.length) {
            deferred.resolve(new cls(this.currentPage[this.currentIndex++]));
        } else if (this.nextUrl) {
            Api.call(this.nextUrl)
                .done(function (r) {
                    this.nextUrl = r.next;
                    this.currentPage = r.results;
                    this.currentIndex = 0;
                    if (this.currentPage.length > 0) {
                        deferred.resolve(new cls(this.currentPage[this.currentIndex++]));
                    } else {
                        deferred.reject();
                    }
                }.bind(this))
                .fail(function (r) {
                    deferred.reject.apply(deferred, arguments);
                }.bind(this))
        } else {
            deferred.reject();
        }
        return deferred.promise();
    };
    PagedList.prototype.all = function (entryCb, endCb) {
        var self = this;

        function getNext() {
            self.next()
                .done(function (o) {
                    entryCb && entryCb(o);
                    getNext();
                })
                .fail(function () {
                    endCb && endCb()
                });
        }

        getNext();
    };
    PagedList.prototype.allAtOnce = function (allCb) {
        var all = [];
        this.all(function (r) {
            all.push(r);
        }, function () {
            allCb && allCb(all);
        });
    };

    function getPagedListBuilder(cls) {
        return function () {
            return new PagedList(cls);
        }
    }


    CompareRequest = createEntityClass();
    TestRun = createEntityClass();
    Result = createEntityClass();
    Task = createEntityClass();

    CompareRequest.API_NAME = 'compare_requests';
    TestRun.API_NAME = 'test_runs';
    Result.API_NAME = 'results';
    Task.API_NAME = 'tasks';

    CompareRequest.RELATED_FIELDS = {
        base_test_run: TestRun,
        head_test_run: TestRun
    };
    TestRun.RELATED_ARRAYS = {
        results: Result,
        tasks: Task
    };


    allClassess = [CompareRequest, TestRun, Result, Task];
    allClassess.forEach(function (cls) {
        cls.get = getEntityBuilder(cls);
        cls.list = getPagedListBuilder(cls);

        cls.prototype.init = function () {
            var RELATED_FIELDS = cls.RELATED_FIELDS || {},
                RELATED_ARRAYS = cls.RELATED_ARRAYS || {};
            for (var k in this.__data) {
                if (k in RELATED_FIELDS) {
                    this[k] = getEntityFetcher(RELATED_FIELDS[k], this.__data[k]);
                } else if (k in RELATED_ARRAYS) {
                    this[k] = this.__data[k].map(function (e) {
                        return getEntityFetcher(RELATED_ARRAYS[k], e);
                    });
                } else {
                    this[k] = this.__data[k];
                }
            }
        }
    });


    $.extend(Api, {
        CompareRequest: CompareRequest,
        TestRun: TestRun,
        Result: Result,
        Task: Task
    });


    $.extend(window.Sparrow.Api, Api);
})();