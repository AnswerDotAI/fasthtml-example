const sel = '#drawingCanvas';
let drawing = false;
let context = null;
let canvas = null;
let lastSendTime = 0;
const throttleInterval = 1000; // 1 second in milliseconds

htmx.onLoad(elt => {
    const elements = htmx.findAll(elt, sel);
    if (elt.matches(sel)) elements.unshift(elt)
    elements.forEach(c => {
        canvas = c;
        console.log(canvas);
        context = canvas.getContext('2d'); 
        // Mouse events
        canvas.addEventListener('mousedown', startDrawing);
        canvas.addEventListener('mouseup', stopDrawing);
        canvas.addEventListener('mousemove', draw);
        // Touch events
        canvas.addEventListener('touchstart', handleStart);
        canvas.addEventListener('touchend', handleEnd);
        canvas.addEventListener('touchmove', handleMove);
        // set background color
        context.fillStyle = 'white'; 
        context.fillRect(0, 0, canvas.width, canvas.height);
    });
});

function startDrawing(e) {
    drawing = true;
    draw(e);
}

function stopDrawing() {
    drawing = false;
    context.beginPath();
    throttledSendCanvasData();
}

function draw(e) {
    if (!drawing) return;
    context.lineWidth = 5;
    context.lineCap = 'round';
    context.strokeStyle = 'black';

    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX || e.touches[0].clientX) - rect.left;
    const y = (e.clientY || e.touches[0].clientY) - rect.top;

    context.lineTo(x, y);
    context.stroke();
    context.beginPath();
    context.moveTo(x, y);
}

// Touch event handlers
function handleStart(e) {
    e.preventDefault();
    startDrawing(e.touches[0]);
}

function handleEnd(e) {
    e.preventDefault();
    stopDrawing();
}

function handleMove(e) {
    e.preventDefault();
    draw(e.touches[0]);
}

function throttledSendCanvasData() {
    const now = Date.now();
    if (now - lastSendTime >= throttleInterval) {
        sendCanvasData();
        lastSendTime = now;
    }
    else {
        setTimeout(throttledSendCanvasData, throttleInterval);
    }
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
        if (data['active_game'] == "no") {htmx.ajax('GET', '/active_area', {target:'#active-area', swap:'outerHTML'});}
        console.log(data);})
        .catch(error => console.error('Error:', error));
    });
}