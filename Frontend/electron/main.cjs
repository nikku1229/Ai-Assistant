const { app, BrowserWindow, session } = require("electron");

app.commandLine.appendSwitch("enable-speech-dispatcher");
app.commandLine.appendSwitch("use-fake-ui-for-media-stream");

function createWindow() {
  const win = new BrowserWindow({
    width: 1000,
    height: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  session.defaultSession.setPermissionRequestHandler(
    (_webContents, permission, callback) => {
      const allowed = new Set(["media"]);
      callback(allowed.has(permission));
    },
  );

  // Permission check karne se pehle set karo
  session.defaultSession.setPermissionCheckHandler(
    (_webContents, permission) => {
      const allowed = new Set(["media"]);
      return allowed.has(permission);
    },
  );

  win.loadURL("http://localhost:5173");
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
