function initializeDrawingArea() {
  var drawingArea = document.createElement('div');
  drawingArea.setAttribute('id', 'drawing-area');
  document.body.appendChild(drawingArea);
}

function clearDrawingArea() {
  var drawingArea = document.getElementById('drawing-area');
  drawingArea.innerHTML = '';
}
