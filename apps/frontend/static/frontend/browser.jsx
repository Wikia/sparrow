window.Sparrow.Api.CompareRequest.get(29);

(function(){
    var Actions = window.Sparrow.Actions,
        isNumericType = window.Sparrow.Metrics.isNumericType;

    var Browser = React.createClass({
        render: function() {
            var data = this.props.data;
            return <div>
                    <div>
                        <CompareRequestSelect compareRequests={data.compareRequests} />
                        @
                        <ServerSelect serverName={data.serverName}/>
                    </div>
                    <ResultComparison errorText={data.testResultsError} results={data.testResults} />
                    <LoadingIndicator loading={data.loading}/>
                </div>;
        }
    });

    var ResultComparison = React.createClass({
        render: function() {
            var errorText = this.props.errorText;
            if (!errorText && this.props.results.length == 0){
                errorText = 'No results available for the selected comparison';
            }
            //console.log(this.props);
            if (errorText) {
                return <span className="error">{errorText}</span>;
            } else {
                return <ComparisonTable comparison={this.props.results} />;
            }
        }
    });

    var ComparisonTable = React.createClass({
        headers: function() {
            var ths = [<th key="metric">Metric</th>].concat(this.props.comparison.names().map(function(text, i){
                var res = [];
                if (i > 0) {
                    res.push(<th></th>);
                }
                res.push(<th>{text}</th>);
                return res;
            }));
            return <tr key="::header">{ths}</tr>;
        },
        rows: function() {
            if (this.props.comparison.length == 0) {
                return false;
            }
            var data = this.props.comparison.data,
                ord = this.props.comparison.ids(),
                byId, byResult, rowResults,
                id1, id2, id3,
                colspan = 2 * this.props.comparison.length,
                out = [];

            Object.keys(data).forEach(function(url){
                id1 = url;
                out.push(<ComparisonHeader key={id1} colspan={colspan} level="1" text={url} />);
                byId = data[url];
                console.log(byId);
                Object.keys(byId).forEach(function(id){
                    id2 = id1 + '___' + id;
                    //console.log(id2);
                    //out.push(<ComparisonHeader key={id2} colspan={colspan} level="2" text={id} />);
                    byResult = byId[id];
                    rowResults = [];
                    ord.map(function(rId){
                        rowResults.push(byResult[rId]);
                    });
                    out.push(<ComparisonRow key={id2} name={id} results={rowResults} />);
                });
            });

            return out;
        },
        render: function() {
            var rows = [this.headers()].concat(this.rows());
            return <table className="cmp-table">
                    <tbody>
                    {rows}
                    </tbody>
                </table>
        }
    });

    var ComparisonHeader = React.createClass({
        render: function() {
            return <tr className={"cmp-header cmp-header-" + this.props.level}><td colSpan={this.props.colspan}>{this.props.text}</td></tr>;
        }
    });

    var ComparisonRow = React.createClass({
        getInitialState: function() {
            return {
                expanded: false
            };
        },
        getPercentageDiffText: function(stats1, stats2, extraCls) {
            var scaledDiff = stats1.mean.scaledDiffTo(stats2.mean),
                diffCls = (scaledDiff > 0 ? 'cmp-diff-plus' : (scaledDiff < 0 ? 'cmp-diff-minus' : ''))
                    + (extraCls ? ' ' + extraCls : ''),
                perc;
            if (isNaN(scaledDiff)) {
                return <span className={diffCls} />;
            }
            perc = scaledDiff * 100;
            perc = Math.round(perc * 100) / 100;
            return <span className={diffCls}>{(perc > 0 ? '+' : '') + perc + '%'}</span>;
        },
        renderCell: function(result, baseResult) {
            if (!result || !result.length) {
                return <td></td>;
            }
            result = result[0];
            var stats = result.stats,
                valType = result.type,
                statsText = Object.keys(stats).map(function(stat){
                    return stat + ': ' + stats[stat];
                }).join(', '),
                tooltip = statsText,
                text = stats.mean.format(),
                cls = isNumericType(valType) ? 'cmp-value-number' : '',
                res = [];
            if (this.state.expanded) {
                var els = [];
                result.values.forEach(function(v){
                    console.log(v.format());
                    var lines = v.format().split("\n");
                    lines.forEach(function(c){
                        els.push(<br />);
                        els.push(<span>{c}</span>);
                    });
                    if (v.length > 1) {
                        els.push(<br />);
                    }
                });
                text = <span><b>{text}</b>{els}</span>;
            }
            if (baseResult[0] != result) {
                baseResult = baseResult[0];
                res.push(<td className="cmp-diff">
                    {this.getPercentageDiffText(baseResult.stats, result.stats)}
                    <br />
                    {this.getPercentageDiffText(baseResult.statsMargin2, result.statsMargin2, 'cmp-diff-secondary')}
                    </td>);
            }
            res.push(<td className={cls} title={tooltip}>{text}</td>);
            return res;
        },
        render: function() {
            var name = this.props.name + ' [' + this.props.results[0][0].type + ']',
                results = this.props.results,
                first = results[0],
                self = this,
                tds = results.map(function(r) {
                    return self.renderCell(r, first);
                });
            return <tr onClick={this.onClick}>
                <td>{name}</td>
                {tds}
                </tr>;
        },
        onClick: function() {
            this.setState({expanded: !this.state.expanded});
        }
    });


    var CompareRequestSelect = React.createClass({
        render: function() {
            var options = this.props.compareRequests.map(function(c){
                var text = c.repo + '#' + c.pull_request_num + ' ' + c.head_ref + ' (' + c.head_sha + ') [' + c.id + ']';
                return <option key={c.id} value={c.id}>{text}</option>;
            });
            return <div className="request-select">
                    <select onChange={this.onChange}>
                        {options}
                    </select>
                </div>;
        },

        onChange: function(ev) {
            Actions.selectCompareRequest($(ev.target).val());
            console.log('request-select onchange', $.extend({},arguments[0]));
        }
    });

    var ServerSelect = React.createClass({
        render: function() {
            return <input type="text" defaultValue={this.props.serverName} onKeyDown={this.onKeyDown} onBlur={this.onBlur} />
        },

        onKeyDown: function(ev) {
            if (ev.keyCode == 13 && !ev.shiftKey && !ev.ctrlKey && !ev.altKey) {
                Actions.setServerName($(ev.target).val());
                console.log('server-select onkeydown', $.extend({},arguments[0]));
            }
        },

        onBlur: function(ev) {
            Actions.setServerName($(ev.target).val());
            console.log('server-select onblur', $.extend({},arguments[0]));
        }
    });

    var LoadingIndicator = React.createClass({
        render: function() {
            console.log(this.props);
            var cls = 'loading-indicator' + (this.props.loading ? ' active' : '');
            return <div className={cls}>Loading...</div>
        }
    });

    $.extend(window.Sparrow.View, {
        render: function(Data) {
            React.render(
                <Browser data={Data} />,
                document.body
            );
        },
        setLoading: function(loading) {
            $('.loading-indicator')[loading?'addClass':'removeClass']('active');
        }
    });

    window.Sparrow.Actions.init();
})();