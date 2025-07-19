var term = new Terminal();
term.open(document.getElementById('terminal'));

const socket = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws`);
socket.onopen  = () => term.focus();
socket.onmessage = ev => term.write(ev.data);

term.onData(data => {
  // Send all data including control characters
  socket.send(JSON.stringify({msg: data, HEADERS: {}}));
});