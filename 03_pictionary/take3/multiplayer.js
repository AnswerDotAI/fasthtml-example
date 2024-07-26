let drawing = false;
let context = null;
let canvas = null;
let lastSendTime = 0;
const throttleInterval = 1000; // 1 second in milliseconds
let throttleTimeout = null;
let pendingData = false;


htmx.onLoad(elt => {

    // Find and process the canvas element
    const elements = htmx.findAll(elt, '#drawingCanvas');
    if (elt.matches('#drawingCanvas')) elements.unshift(elt)
    elements.forEach(c => {
        console.log(c);
        canvas = c;
        console.log(canvas);
        context = canvas.getContext('2d'); 
        context.fillStyle = 'white'; 
        context.fillRect(0, 0, canvas.width, canvas.height);

        // // Countdown 3...2...1... on the canvas
        // context.font = '30px Arial';
        // context.fillStyle = 'black';
        // context.textAlign = 'center';
        // for (let i = 0; i < 4; i++) {
        //     setTimeout(() => {
        //         context.fillStyle = 'white'; 
        //         context.fillRect(0, 0, canvas.width, canvas.height);
        //         context.fillStyle = 'black';
        //         let text = i == 3 ? "Go!" : 3 - i;
        //         context.fillText(text, canvas.width / 2, canvas.height / 2);
        //     }, i * 1000);
        // }
        // setTimeout(() => {
        //     context.fillStyle = 'white'; 
        //     context.fillRect(0, 0, canvas.width, canvas.height);
        // }, 4000);

        // Mouse events
        canvas.addEventListener('mousedown', startDrawing);
        canvas.addEventListener('mouseup', stopDrawing);
        canvas.addEventListener('mousemove', draw);

        // Touch events (no {passive: true} since we want to stop scroll)
        canvas.addEventListener('touchstart', handleStart);
        canvas.addEventListener('touchend', handleEnd);
        canvas.addEventListener('touchmove', handleMove);
        
    });

    // If elt is a guess, log it and update latest-guess
    if (elt.matches('.guess')) {
        console.log("Got guess:", elt);
        const latestGuess = document.getElementById('latest-guess');

        let correct = elt.innerText.includes(" (correct!)");
        let guess = elt.innerText.split(": ")[1].split(" ")[0];
        let guesser = elt.innerText.split(": ")[0];
        let text = elt.innerText.split(" (")[0];
        if (latestGuess) {
            latestGuess.innerText = text; //correct ? text + " (correct!)" : text;
            latestGuess.classList.add('guess-animation');
            
            if (correct) {
                latestGuess.classList.add('correct-guess');
                // End game means 3 seconds before the game ends and moves to new screen
                // TODO pause and animate fireworks
                let tl = document.getElementById("time-left")
                if (tl){
                    console.log("Stopping countdown");
                    document.getElementById("active-header").innerText = "Game Over!";
                    document.getElementById("active-subheader").innerText =  guesser + " correctly guessed the word "+ guess + "!";
                    window.confetti(ticks=100);
                    tl.remove();// Stops the countdown
                } 
                

            } else {
                latestGuess.classList.remove('correct-guess');
            }

            // Remove animation class after it's done
            setTimeout(() => {
                latestGuess.classList.remove('guess-animation');
            }, 500);
        }
    }

    // If > max_guesses guesses, remove the oldest ones
    const guessList = document.getElementById('guess-area');
    const max_guesses = 8;
    if (guessList && guessList.children.length > max_guesses) {
        console.log("Removing old guesses");
        for (let i = guessList.children.length - 1; i >= max_guesses; i--) {
            guessList.removeChild(guessList.children[i]);
        }
    }
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

// Sends all events, one per second
// function throttledSendCanvasData() {
//     const now = Date.now();
//     if (now - lastSendTime >= throttleInterval) {
//         sendCanvasData();
//         lastSendTime = now;
//     }
//     else {
//         setTimeout(throttledSendCanvasData, throttleInterval);
//     }
// }

// Sends first event then again after 1 second
function throttledSendCanvasData() {
    const now = Date.now();
    
    if (now - lastSendTime >= throttleInterval) {
        sendCanvasData();
        lastSendTime = now;
        
        if (throttleTimeout) {
            clearTimeout(throttleTimeout);
            throttleTimeout = null;
        }
        
        if (pendingData) {
            throttleTimeout = setTimeout(() => {
                sendCanvasData();
                lastSendTime = Date.now();
                pendingData = false;
            }, throttleInterval);
        }
    } else {
        pendingData = true; 
        
        if (!throttleTimeout) {
            throttleTimeout = setTimeout(() => {
                sendCanvasData();
                lastSendTime = Date.now();
                pendingData = false;
                throttleTimeout = null;
            }, throttleInterval - (now - lastSendTime));
        }
    }
}


function sendCanvasData() {
    canvas.toBlob((blob) => {
    const formData = new FormData();
    formData.append('image', blob, 'canvas.png');
    console.log("Sending canvas data");
    fetch('/process-canvas', {
        method: 'POST',
        body: formData,
    }).then(response => response.json())
        .then(data => {
        console.log("Received data");
        if (data['active_game'] == "no") {
            // if the canvas exists, update the active area to remove it
            setTimeout(() => {
                if (document.getElementById('drawingCanvas')) {
                    htmx.ajax('GET', '/active_area', {target:'#active-area', swap:'outerHTML'});
                }
            }, 4000);
            
        }
        console.log(data);})
        .catch(error => console.error('Error:', error));
    });
}

// COUNTDOWN TIMER
// function updateCountdown() {
//     let timeLeftElement = document.getElementById("time-left");
//     let progressElement = document.getElementById("progress");
//     let containerElement = document.getElementById("countdown-container");

//     if (!timeLeftElement || !progressElement) return;

//     let start = parseFloat(document.getElementById("start-time").value);
//     let elapsed = Math.floor(Date.now() / 1000) - start;
//     let max_duration = parseFloat(document.getElementById("game-max-duration").value);
//     let time = Math.max(0, max_duration - elapsed);
//     let percentage = (time / max_duration) * 100;

//     timeLeftElement.innerText = `Time left: ${Math.floor(time)} seconds`;
//     progressElement.style.width = `${percentage}%`;

//     // Add urgency effects
//     if (percentage <= 25) {
//         progressElement.classList.add('urgent');
//         containerElement.classList.add('urgency');
//     } else {
//         progressElement.classList.remove('urgent');
//         containerElement.classList.remove('urgency');
//     }

//     if (time <= 0) {
//         console.log("Time's up!");
//         htmx.ajax('GET', '/endgame', {target:'#active-area', swap:'outerHTML'});
//         clearInterval(countdownInterval);
//     }
// }

// Initialize the countdown
// let countdownInterval = setInterval(updateCountdown, 100); // Update every 100ms for smoother animation

// Countdonw timer
setInterval(() => {
    let timeLeftElement = document.getElementById("time-left");
    let progressElement = document.getElementById("progress");
    let containerElement = document.getElementById("countdown-container");
    // do nothing if it doesn't exist
    if (!timeLeftElement || !progressElement) return;
    let start = parseFloat(document.getElementById("start-time").value);
    let elapsed = (Date.now() / 1000) - start;
    let max_duration = parseFloat(document.getElementById("game-max-duration").value);
    let time = Math.max(0, max_duration - elapsed);
    let percentage = (time / max_duration) * 100;
    // console.log(start, elapsed, max_duration, time, percentage);
    timeLeftElement.innerText = `Time left: ${time} seconds`;
    progressElement.style.width = `${percentage}%`;
    // Add urgency effects
    if (percentage <= 25) {
        progressElement.classList.add('urgent');
        containerElement.classList.add('urgency');
    } else {
        progressElement.classList.remove('urgent');
        containerElement.classList.remove('urgency');
    }
    if (time <= 0) {
        // Check the game hasn't already been ended
        let timeLeftElement = document.getElementById("time-left");
        if (timeLeftElement){
            console.log("Time's up!");
            // remove the time-left element
            timeLeftElement.remove();
            // trigger HTMX to end the game and replace the active area
            htmx.ajax('GET', '/endgame', {target:'#active-area', swap:'outerHTML'});
        }
        
    }
}, 100); // every 100ms 