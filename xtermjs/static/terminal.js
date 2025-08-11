import { FitAddon } from 'https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.8.0/+esm';

const term = new Terminal();
const fitAddon = new FitAddon();
term.loadAddon(fitAddon);
term.open(document.getElementById('terminal'));

const socket = new WebSocket(`/ws`);

function resizeTerm() {
  fitAddon.fit();
  socket.send(JSON.stringify({cols:term.cols, rows:term.rows, HEADERS: {}}));
}
window.addEventListener('resize', () => resizeTerm());

socket.onopen = () => {
  resizeTerm();
  term.focus();
};
socket.onmessage = ev => term.write(ev.data);
term.onData(data => {socket.send(JSON.stringify({msg: data, HEADERS: {}}));});