const { app, BrowserWindow, session } = require("electron");

app.commandLine.appendSwitch("enable-speech-dispatcher");
app.commandLine.appendSwitch("use-fake-ui-for-media-stream");

function createWindow() {
  const win = new BrowserWindow({
    width: 1000,
    height: 700,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  session.defaultSession.setPermissionRequestHandler(
    (webContents, permission, callback) => {
      callback(true);
    },
  );

  // Permission check karne se pehle set karo
  session.defaultSession.setPermissionCheckHandler(
    (webContents, permission) => {
      return true;
    },
  );

  win.loadURL("http://localhost:5173");
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
