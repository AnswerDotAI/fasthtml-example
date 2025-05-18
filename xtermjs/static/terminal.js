var term = new Terminal();
term.open(document.getElementById('terminal'));

const socket = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws`);
socket.onopen  = () => term.focus();
socket.onmessage = ev => term.write(ev.data);

term.onKey(e =>{
  const ev = e.domEvent;
  const printable = !ev.altKey && !ev.ctrlKey && !ev.metaKey;
  if (printable) {
    socket.send(JSON.stringify({msg: e.key, HEADERS: {}}));
  }
});