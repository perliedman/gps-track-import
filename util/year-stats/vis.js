/*
    Copied and lightly modified version from

    http://bl.ocks.org/tmcw/8153742

    By Tom MacWright (tmcw)
*/

d3.json('../../data/tracks/index.json', function(out) {

    out = out.filter(function(o) {
        var v = o.distance / o.duration * 3.6;
        return o.time && o.time.length &&
            v >= 5 && v < 17; // 5 <= v < 17 km/h -> probably running
    }).map(function(o) {
        o.totalseconds = +o.duration;
        o.date = new Date(o.time[0] * 1000);
        return o;
    }).filter(function(o) {
        return o.date.getFullYear() >= 2009;
    });

    var margin = {top: 20, right: 10, bottom: 20, left: 10},
        width = 640 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;

    var formatNumber = d3.format("d");

    var y = d3.scale.linear()
        .domain([0, 400])
        .range([height, 0]);

    var x = d3.time.scale()
        .domain([new Date(2010, 0, 1), new Date(2011, 0, 1)])
        .range([0, width]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .ticks(d3.time.months)
        .tickFormat(d3.time.format("%b"))
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .tickSize(width)
        .ticks(4)
        .tickFormat(formatMiles)
        .orient("right");

    var years = d3.nest()
        .key(function(d) {
            return d.date.getFullYear();
        })
        .entries(out);

    for (var yr in years) {
        var total = 0;
        years[yr].values = years[yr].values.sort(function(a, b) {
            return a.date - b.date;
        }).map(function(k) {
            total += (k.distance / 1000.0);
            k.total = total;
            return k;
        });
    }

    var color = d3.scale.category10();

    var svg = d3.select("body").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    var gy = svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);

    gy.selectAll("g").filter(function(d) { return d; })
        .classed("minor", true);

    gy.selectAll("text")
        .attr("x", 4)
        .attr("dy", -4);

    var line = d3.svg.line()
        .x(function(d) {
            var year_normal = d.date.setYear(2010);
            return x(year_normal);
        })
        .y(function(d) {
            return y(d.total);
        });
    var area = d3.svg.area()
        .x(function(d) {
            var year_normal = d.date.setYear(2010);
            return x(year_normal);
        })
        .y0(height)
        .y1(function(d) {
            return y(d.total);
        });

    svg.selectAll('path.line')
        .data(years)
        .enter()
        .append("path")
        .style("stroke", function(d) { return color(d.key); })
        .attr("class", "line")
        .attr("d", function(d) {
            return line(d.values);
        });
    svg.selectAll('path.area')
        .data(years)
        .enter()
        .append("path")
        .style("fill", function(d) { return color(d.key); })
        .attr("class", "area")
        .attr("d", function(d) {
            return area(d.values);
        });

    svg.selectAll('text.year')
        .data(years)
        .enter()
        .append("text")
        .style("fill", function(d) { return color(d.key); })
        .attr("class", "year")
        .attr('dx', -5)
        .attr('dy', -5)
        .attr("transform", function(d) {
            var last = d.values[d.values.length - 1];
            var year_normal = last.date.setYear(2010);
            return 'translate(' + x(year_normal) + ',' +
                y(last.total) + ')';
        })
        .text(function(d) {
            return d.key;
        });
    function formatMiles(d) {
      return formatNumber(d) + ' km';
    }
});
