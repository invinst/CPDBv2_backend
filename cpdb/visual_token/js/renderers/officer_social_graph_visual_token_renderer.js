(function () {
  var backgroundColorScheme = {
    '000': '#f5f4f4',
    '001': '#cbd4db',
    '010': '#e7eee3',
    '100': '#f9efe3',
    '002': '#c3d7ed',
    '011': '#d3f3eb',
    '020': '#bae5b6',
    '101': '#e4dde6',
    '110': '#faf6c7',
    '200': '#f8c8bf',
    '012': '#78b8d3',
    '021': '#61b29d',
    '102': '#8a7c96',
    '111': '#8f8f8f',
    '120': '#9c9b84',
    '201': '#df7575',
    '210': '#f4765d',
    '022': '#308182',
    '112': '#485787',
    '121': '#4b704d',
    '202': '#6c4c83',
    '211': '#e44747',
    '220': '#ae4c12',
    '122': '#104045',
    '212': '#38314a',
    '221': '#472610',
    '222': '#231f20'
  };
  var crScale = d3.scaleThreshold().domain([6, 25]).range([0, 1, 2]);
  var trrScale = d3.scaleThreshold().domain([6, 25]).range([0, 1, 2]);
  var salaryScale = d3.scaleThreshold().domain([60000, 90000]).range([0, 1, 2]);

  function calculateBackgroundColor(officer) {
    var crThres = crScale(officer.crs);
    var trrThres = trrScale(officer.trrs);
    var salaryThres = salaryScale(officer.salary);
    return backgroundColorScheme[String(trrThres) + String(salaryThres) + String(crThres)];
  }

  function calculateEdgeColor(color) {
    var extracted = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(color);
    var value = Math.max(parseInt(extracted[1], 16), parseInt(extracted[2], 16), parseInt(extracted[3], 16));
    var greyness = value >= 60 ? value - 60 : value + 60;
    var hex = greyness.toString(16);
    return '#' + hex + hex + hex;
  }

  function calculateFillColor(d) {
    if (d.id === focusedOfficer.id) {
      return '#001733';
    }
    return calculateBackgroundColor(d);
  }

  function calculateStrokeColor(d) {
    var backgroundColor = calculateBackgroundColor(focusedOfficer);
    return calculateFillColor(d) === backgroundColor ? calculateEdgeColor(backgroundColor) : null;
  }

  function initializeDrawingArea() {
    clearDrawingArea();
    var svg = d3.select('div#drawing-area').append('svg')
      .attr('width', '1200')
      .attr('height', '630')
      .attr('viewport', '-381 -200 762 400');
    svg.append('g').attr('class', 'link-group');
    svg.append('g').attr('class', 'node-group');
  }

  window.render = function (jsonString) {
    initializeDrawingArea();
    var data = JSON.parse(jsonString);
    var nodes = data.nodes;
    var links = data.links;
    var focusedOfficer = nodes.find(function(node) { return node.id === data.focusedId; });

    var linearScale = d3.scaleLinear().domain([1, d3.max(links, function(link) {
      return link.crs;
    })]).range([40, 80]);

    var linkForce = d3.forceLink(links).id(function(d) {
      return d.id;
    });

    linkForce.distance(function(x) {
      return linearScale(x.crs)
    })

    var centerForce = d3.forceCenter()
    var chargeForce = d3.forceManyBody();
    chargeForce.strength(-100)

    this.simulation = d3
      .forceSimulation(nodes)
      .force("charge", chargeForce)
      .force("link", linkForce)
      .force('collision', d3.forceCollide(10))
      .force("center", centerForce);

    var link = d3
      .select('g.link-group')
      .selectAll(".link")
      .data(linkForce.links());

    var node = d3
      .select('g.node-group')
      .selectAll(".node")
      .data(nodes, function(d) { return d.id; });

    var backgroundColor = calculateBackgroundColor(focusedOfficer);

    link.exit().remove();
    link = link.enter().insert("line").merge(link)
      .attr("class", "link").style('stroke', calculateEdgeColor(backgroundColor));

    node.exit().remove();

    var enteredNode = node.enter()
      .insert('circle')
      .attr('class', 'node')
      .attr('r',10)
    enteredNode.append('title')
      .text(function(d) { return d.name; });

    node = enteredNode.merge(node)
      .attr('stroke-width', function(d) {
        return d.id === focusedOfficer.id ? 3 : 1;
      })
      .attr('stroke', calculateStrokeColor)
      .style('fill', calculateFillColor);
    node.selectAll('title').text(function(d) { return d.name; });

    this.simulation.on("tick", function () {
      link
        .attr("x1", function(d) {
          return d.source.x;
        })
        .attr("y1", function(d) {
          return d.source.y;
        })
        .attr("x2", function(d) {
          return d.target.x;
        })
        .attr("y2", function(d) {
          return d.target.y;
        });

      node
        .attr("cx", function(d) {
          return d.x;
        })
        .attr("cy", function(d) {
          return d.y;
        });
    });
  }
})();
