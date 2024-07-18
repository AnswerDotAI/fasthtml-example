const canvas = document.getElementById('drawingCanvas');
const context = canvas.getContext('2d');
let drawing = false;

canvas.addEventListener('mousedown', startDrawing);
canvas.addEventListener('mouseup', stopDrawing);
canvas.addEventListener('mousemove', draw);

function startDrawing(e) {
  drawing = true;
  draw(e);
}

function stopDrawing() {
  drawing = false;
  context.beginPath();
  sendCanvasData();
}

function draw(e) {
  if (!drawing) return;
  context.lineWidth = 5;
  context.lineCap = 'round';
  context.strokeStyle = 'black';
  context.lineTo(e.clientX - canvas.offsetLeft, e.clientY - canvas.offsetTop);
  context.stroke();
  context.beginPath();
  context.moveTo(e.clientX - canvas.offsetLeft, e.clientY - canvas.offsetTop);
}

function sendCanvasData() {
  canvas.toBlob((blob) => {
    const formData = new FormData();
    formData.append('image', blob, 'canvas.png');

    fetch('/process-canvas', {
      method: 'POST',
      body: formData,
    }).then(response => response.json())
      .then(data => {
        document.getElementById('caption').innerHTML = data.caption;
        console.log(data);})
      .catch(error => console.error('Error:', error));
  });
}