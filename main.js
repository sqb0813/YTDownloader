const { app, BrowserWindow } = require('electron')
const path = require('path')
const isDev = require('electron-is-dev')
const { spawn } = require('child_process')

let mainWindow
let pythonProcess

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  })

  // 启动Python后端
  startPythonBackend()

  // 等待后端启动
  setTimeout(() => {
    mainWindow.loadURL('http://localhost:8000')
  }, 2000)

  if (isDev) {
    mainWindow.webContents.openDevTools()
  }
}

function startPythonBackend() {
  let scriptPath
  if (isDev) {
    // 开发环境
    scriptPath = path.join(__dirname, 'backend', 'main.py')
    pythonProcess = spawn('python', [scriptPath])
  } else {
    // 生产环境
    scriptPath = path.join(process.resourcesPath, 'backend', 'youtube_downloader.exe')
    pythonProcess = spawn(scriptPath)
  }

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python输出: ${data}`)
  })

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python错��: ${data}`)
  })
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
  // 关闭Python进程
  if (pythonProcess) {
    pythonProcess.kill()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
}) 