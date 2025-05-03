var term = new Terminal();
term.open(document.getElementById('terminal'));
term.write('Hello from \x1B[1;3;31mxterm.js\x1B[0m $ ')
term.writeln('')
term.prompt = () => {
  term.write('\r\n$ ');
};

const socket = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws`);
socket.onopen  = () => term.focus();
socket.onmessage = ev => term.write(ev.data);

term.onKey(e =>{
  const ev = e.domEvent;
  const printable = !ev.altKey && !ev.ctrlKey && !ev.metaKey;

  if (ev.keyCode === 13) {
    term.prompt();
  } else if (ev.keyCode === 8) {
    // Do not delete the prompt
    if (term._core.buffer.x > 2) {
      term.write('\b \b');
    }
  } else if (printable) {
    term.write(e.key);
  }
});
// term.onData(data => socket.send('ls'));
term.onData(data => {
  console.log('data', data);
    socket.send(JSON.stringify({msg: data, HEADERS: {}}));
});
// term.onData(d => socket.send(JSON.stringify({msg: d, HEADERS: {}})));

// window.addEventListener('resize', () => fitAddon.fit());