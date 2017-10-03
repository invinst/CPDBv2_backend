const backgroundColorScheme = {
    '00': '#f5f4f4',
    '10': '#edf0fa',
    '01': '#f8eded',
    '20': '#d4e2f4',
    '11': '#ecdeef',
    '02': '#efdede',
    '30': '#c6d4ec',
    '21': '#d9d1ee',
    '12': '#eacbe0',
    '03': '#ebcfcf',
    '40': '#aec9e8',
    '31': '#c0c3e1',
    '22': '#cdbddd',
    '13': '#e4b8cf',
    '04': '#f0b8b8',
    '50': '#90b1f5',
    '41': '#aaace3',
    '32': '#b6a5de',
    '23': '#c99edc',
    '14': '#e498b6',
    '05': '#f89090',
    '51': '#748be4',
    '42': '#8e84e0',
    '33': '#af7fbd',
    '24': '#c873a2',
    '15': '#e1718a',
    '52': '#6660ae',
    '43': '#8458aa',
    '34': '#a34e99',
    '25': '#b5496a',
    '53': '#4c3d8f',
    '44': '#6b2e7e',
    '35': '#792f55',
    '54': '#391c6a',
    '45': '#520051',
    '55': '#131313',
};
const crScale = d3.scaleThreshold().domain([1, 5, 10, 25, 40]).range([0, 1, 2, 3, 4, 5, 6]);
const trrScale = d3.scaleThreshold().domain([1, 5, 10, 25, 40]).range([0, 1, 2, 3, 4, 5, 6]);
const state = {};

function calculateBackgroundColor(officer) {
  const crThres = crScale(officer.crs);
  const trrThres = trrScale(officer.trrs);
  return backgroundColorScheme[
    String(crThres) + String(trrThres)
  ];
}

function calculateEdgeColor(color) {
  const extracted = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(color);
  const value = Math.max(
    parseInt(extracted[1], 16),
    parseInt(extracted[2], 16),
    parseInt(extracted[3], 16)
  );
  const greyness = value >= 60 ? value - 60 : value + 60;
  const hex = greyness.toString(16);
  return '#' + hex + hex + hex;
}

function calculateFillColor(d) {
  if (d.id === state.focusedOfficer.id) {
    return '#231f20';
  }
  return calculateBackgroundColor(d);
}

function calculateStrokeColor(d) {
  if (d.id === state.focusedOfficer.id) {
    return 'white';
  }
  return calculateFillColor(d) === state.backgroundColor
    ? calculateEdgeColor(state.backgroundColor)
    : null;
}

function initializeDrawingArea() {
  clearDrawingArea();
  const svg = d3
    .select('div#drawing-area')
    .append('svg')
    .attr('id', 'social-graph')
    .attr('width', '1200')
    .attr('height', '630')
    .attr('viewBox', '-381 -200 762 400');
  svg.append('g').attr('class', 'link-group');
  svg.append('g').attr('class', 'node-group');
}

function getSVGString(nodes) {
  return [
    '<?xml version="1.0"?>',
    '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" \n',
    '         "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">',
    '<svg width="675" height="675" viewBox="-337.5 -337.5 675 675" xmlns="http://www.w3.org/2000/svg">',
    document.getElementById('social-graph').innerHTML,
    '</svg>'
  ].join('');
}

window.render = function (jsonString) {
  initializeDrawingArea();
  const data = JSON.parse(jsonString);
  const nodes = data.nodes;
  const links = data.links;
  state.focusedOfficer = nodes.find(function (node) {
    return node.id === data.focusedId;
  });

  const linearScale = d3
    .scaleLinear()
    .domain([
      1,
      d3.max(links, function (link) {
        return link.crs;
      })
    ])
    .range([40, 80]);

  const linkForce = d3.forceLink(links).id(function (d) {
    return d.id;
  });

  linkForce.distance(function (x) {
    return linearScale(x.crs);
  });

  const centerForce = d3.forceCenter();
  const chargeForce = d3.forceManyBody();
  chargeForce.strength(-100);

  this.simulation = d3
    .forceSimulation(nodes)
    .force('charge', chargeForce)
    .force('link', linkForce)
    .force('collision', d3.forceCollide(10))
    .force('center', centerForce);

  let link = d3
    .select('g.link-group')
    .selectAll('.link')
    .data(linkForce.links());

  let node = d3
    .select('g.node-group')
    .selectAll('.node')
    .data(nodes, function (d) {
      return d.id;
    });

  if (state.focusedOfficer === undefined) {
    throw new Error(jsonString)
  }
  state.backgroundColor = calculateBackgroundColor(state.focusedOfficer);
  d3.select('svg').attr('style', 'background-color: ' + state.backgroundColor);

  link.exit().remove();
  link = link
    .enter()
    .insert('line')
    .merge(link)
    .attr('class', 'link')
    .attr('shape-rendering', 'optimizeQuality')
    .style('stroke', calculateEdgeColor(state.backgroundColor));

  node.exit().remove();

  const enteredNode = node
    .enter()
    .insert('circle')
    .attr('class', 'node')
    .attr('r', 10);
  enteredNode.append('title').text(function (d) {
    return d.name;
  });

  node = enteredNode
    .merge(node)
    .attr('stroke-width', function (d) {
      return d.id === state.focusedOfficer.id ? 3 : 1;
    })
    .attr('stroke', calculateStrokeColor)
    .style('fill', calculateFillColor);
  node.selectAll('title').text(function (d) {
    return d.name;
  });

  this.simulation.stop();
  for (let i = 0; i < 300; i++) {
    this.simulation.tick();
  }
  link
    .attr('x1', function (d) {
      return d.source.x;
    })
    .attr('y1', function (d) {
      return d.source.y;
    })
    .attr('x2', function (d) {
      return d.target.x;
    })
    .attr('y2', function (d) {
      return d.target.y;
    });

  node
    .attr('cx', function (d) {
      return d.x;
    })
    .attr('cy', function (d) {
      return d.y;
    });

  return getSVGString(nodes);
};
