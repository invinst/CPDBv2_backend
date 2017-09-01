(function () {
  function initializeDrawingArea() {
    var drawingArea = document.createElement('div');
    drawingArea.setAttribute('id', 'drawing-area');
    body.appendChild(drawingArea);
  }

  window.clearDrawingArea = function() {
    var drawingArea = document.getElementById('drawing-area');
    drawingArea.innerHTML = '';
  }
})();
