const { app, BrowserWindow } = require('electron');
const { execFile } = require('child_process');
const path = require('path');

let pyProc;
const pyPath = path.join(
    process.resourcesPath,
    'main.py'
);
const uvPath = path.join(
    process.resourcesPath,
    'uv'
);
app.whenReady().then(async () => {
  // Launch the FastHTML (Python) server
  pyProc = execFile(uvPath, ['run', pyPath], (error) => {
    if (error) console.error("Failed to start Python server:", error);
  });
  
  // Wait for server to start
  // Add retry logic for connecting to the server
  const maxRetries = 5;
  let retries = 0;
  const win = new BrowserWindow({ /* options */ });
  win.webContents.openDevTools()

  const tryConnect = () => {
    fetch('http://localhost:5001')
      .then(() => win.loadURL('http://localhost:5001'))
      .catch(err => {
        if (retries < maxRetries) {
          retries++;
          setTimeout(tryConnect, 1000);
        } else {
          console.error('Failed to connect to Python server');
        }
      });
  };

  tryConnect();

  
  // win.loadURL('http://localhost:5001');  // URL of FastHTML server
});
app.on('window-all-closed', () => {
  if (pyProc) pyProc.kill();  // ensure Python server quits when app closes
  app.quit();
});
