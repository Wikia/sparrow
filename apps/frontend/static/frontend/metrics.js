(function(){
    var Metrics = {},
        Collection, CollectionComparison, Value, ValueList;

    Collection = function(result, testRun) {
        this.result = result;
        this.testRun = testRun;

        this.id = this.result.id;
        this.name = this.testRun ? this.testRun.name : this.id;

        this.raw = result.results;
        this.data = this.init();
    };

    Collection.prototype.init = function () {
        var res = {}, values;
        this.raw.forEach(function (e) {
            var ctx = $.extend({}, e.context),
                vtype = ctx.type,
                o = res,
                id, item;

            // split by url
            id = ctx.url;
            o = o[id] = o[id] || {};
            delete ctx.url;

            // split by metric id
            id = ctx.origin + ':' + ctx.id;
            o = o[id] = o[id] || [];
            delete ctx.origin;
            delete ctx.id;

            // append results
            values = new ValueList(vtype, e.values);
            item = {
                type: vtype,
                context: ctx,
                info: e.info,
                values: values.items,
                stats: values.stats()
            };

            o.push(item);
        });

        this.__cachePlain = res;

        return res;
    };


    Collection.compare = Collection.prototype.compare = function(collections) {
        return new CollectionComparison(collections);
    };


    CollectionComparison = function(collections) {
        this.sources = collections;
        this.length = this.sources.length;
        this.data = this.init();
    };

    function Object_values(o) {
        return Object.keys(o).map(function (k) {
            return o[k];
        });
    }

    function mergeAndSortLists(lists) {
        var o = {};
        lists.forEach(function (d) {
            if (!d.push || !d.length) {
                return;
            }
            d.forEach(function (k) {
                o[k] = 1;
            });
        });
        return Object.keys(o).sort();
    }

    CollectionComparison.prototype.init = function () {
        var plains = {}, rIds = [],
            u, v,
            urls, ids,
            out = {};
        this.sources.forEach(function (c) {
            plains[c.result.id] = c.data;
            rIds.push(c.result.id);
        });
        urls = mergeAndSortLists(Object_values(plains).map(function (data) {
            return Object.keys(data);
        }));
        urls.forEach(function(url){
            out[url] = {};
            u = {};
            rIds.forEach(function (rId) {
                u[rId] = plains[rId][url] ? plains[rId][url] : {};
            });
            ids = mergeAndSortLists(Object_values(u).map(function (data) {
                return Object.keys(data);
            }));
            ids.forEach(function(id){
                v = {};
                rIds.forEach(function (rId) {
                    v[rId] = u[rId][id] ? u[rId][id] : null;
                });
                out[url][id] = v;
            });
        });
        return out;
    };

    CollectionComparison.prototype.ids = function() {
        return this.sources.map(function(coll){
            return coll.id;
        });
    };

    CollectionComparison.prototype.names = function() {
        return this.sources.map(function(coll){
            return coll.name;
        });
    };

    function strcmp( str1, str2 ) {
        return ( ( str1 == str2 ) ? 0 : ( ( str1 > str2 ) ? 1 : -1 ) );
    }


    var ROUND_PRECISION = 6,
        ROUND_MOD = Math.pow(10, ROUND_PRECISION),
        RE_NUMBER = /^[0-9.]+$/;

    function looksLikeNumber(s) {
        if (typeof s == 'number') {
            return true;
        } else if (typeof s == 'string') {
            if (RE_NUMBER.test(s)) {
                return true;
            }
        }
        return false;
    }

    Value = function(raw_value, type, info, index) {
        this.input_value = raw_value;
        if (type == 'unknown' && looksLikeNumber(raw_value)) {
            raw_value = parseFloat(raw_value);
            type = 'number';
        }
        this.raw_value = raw_value;
        this.type = type;
        this.info = info || null;
        this.index = index || null;
    };

    Value.prototype.format = function() {
        var value;
        if (typeof this.raw_value == 'number') {
            value = Math.round(this.raw_value * ROUND_MOD) / ROUND_MOD;
        } else if (this.type == 'query_list') {
            value = ([].concat(this.raw_value)).sort(function (q1, q2) {
                return strcmp(q1.statement, q2.statement);
            });
            value = value.map(function (qinfo) {
                return '[' + qinfo.time + '] ' + qinfo.count + ' x ' + qinfo.statement;
            }).join("\n")
        } else {
            value = this.raw_value;
        }

        return '' + value;
    };
    Value.prototype.toString = Value.prototype.format;

    Value.compare = function(a, b) {
        if (!isNumericType(this.type)) {
            return a.index - b.index;
        } else {
            return a.raw_value - b.raw_value;
        }
    };

    Value.scaledDiff = function(a, b) {
        if (!isNumericType(this.type)) {
            return null;
        }
        if (a.raw_value == 0 && b.raw_value == 0) {
            return 0;
        }
        if (a.raw_value == 0 || b.raw_value == 0) {
            return null;
        }
        return (b.raw_value - a.raw_value) / a.raw_value;
    };
    Value.prototype.scaledDiffTo = function( other ) {
        return Value.scaledDiff(this, other);
    };


    function NaNValue() {
        return new Value(NaN, 'null');
    }


    ValueList = function(type, valuesAndInfos) {
        this.type = type;
        this.items = valuesAndInfos.map(function(vi, i) {
            return new Value(vi.value, type, vi.info, i);
        });
        this.__sorted = false;
    };

    ValueList.prototype.sorted = function() {
        if (!this.__sorted) {
            this.__sorted = ([].concat(this.items)).sort(Value.compare);
        }
        return this.__sorted;
    };

    ValueList.prototype.stats = function() {
        if (!isNumericType(this.type)) {
            return {
                count: this.items.length,
                median: NaNValue(),
                mean: NaNValue(),
                min: NaNValue(),
                max: NaNValue()
            }
        }
        var sorted = this.sorted(),
            sum = 0, cnt = sorted.length;
        sorted.forEach(function (v) {
            sum += v.raw_value;
        });

        return {
            count: new Value(cnt, 'number'),
            median: new Value(sorted[parseInt(cnt / 2)], this.type),
            mean: new Value(sum / cnt, this.type),
            min: new Value(sorted[0], this.type),
            max: new Value(sorted[cnt - 1], this.type)
        };
    };

    function isNumericType(type) {
        return !(type == 'query_list' || type == 'string');
    }


    $.extend(Metrics, {
        Collection: Collection,
        CollectionComparison: CollectionComparison,
        Value: Value,
        ValueList: ValueList,
        isNumericType: isNumericType
    });

    $.extend(window.Sparrow.Metrics, Metrics);
})();