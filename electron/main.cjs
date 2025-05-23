const { app, BrowserWindow, shell, ipcMain } = require('electron');
const path = require('path');
const isDev = !app.isPackaged;
const { initDatabase, getWallets, closeDatabase } = require('./database.cjs');
const { startServer } = require('./api-server.cjs');
const fs = require('fs');

// 存储 API 服务器端口
let apiPort = 3000;
let mainWindow;

function createWindow() {
  // 创建浏览器窗口
  mainWindow = new BrowserWindow({
    width: 800,  // 临时调大尺寸
    height: 600,
    frame: true,  // 暂时显示窗口边框
    transparent: false,  // 禁用透明
    skipTaskbar: false,
    resizable: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: true,
      webSecurity: false,
      preload: path.join(__dirname, 'preload.cjs')
    }
  });

  // 加载应用
  if (isDev) {
    console.log('Loading development URL: http://localhost:5173/launcher.html');
    mainWindow.loadURL('http://localhost:5173/launcher.html');
  } else {
    const prodPath = path.join(__dirname, '../dist/launcher.html');
    console.log('Loading production URL:', prodPath);
    mainWindow.loadFile(prodPath);
  }

  // 开发者工具
  if (isDev) {
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  }

  // 设置窗口始终在顶部
  mainWindow.setAlwaysOnTop(true, 'floating');

  // 允许链接在默认浏览器中打开
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    // 注入 API 端口信息
    if (url.startsWith('http://localhost:5173')) {
      const separator = url.includes('?') ? '&' : '?';
      shell.openExternal(`${url}${separator}apiPort=${apiPort}`);
    } else {
      shell.openExternal(url);
    }
    return { action: 'deny' };
  });

  // 当点击关闭按钮时隐藏窗口而不是退出应用
  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
      return false;
    }
    return true;
  });
}

// 应用准备就绪时初始化
app.whenReady().then(async () => {
  // 初始化数据库
  initDatabase();
  
  // 启动 API 服务器，不需要传参数，因为我们在api-server.cjs中设置了默认路径
  try {
    const server = startServer();
    apiPort = 3000; // 如果startServer返回的不是端口号，手动设置为3000
    console.log(`API server started on port: ${apiPort}`);
  } catch (err) {
    console.error('Failed to start API server:', err);
  }
  
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// IPC 处理程序：获取钱包数据
ipcMain.handle('get-wallets', async () => {
  return getWallets();
});

// IPC 处理程序：获取 API 端口
ipcMain.handle('get-api-port', () => {
  return apiPort;
});

// 监听来自渲染进程的"打开外部链接"事件
ipcMain.on('open-external', (event, url) => {
  shell.openExternal(url);
});

// 监听连接钱包请求
ipcMain.on('connect-wallet', (event, url) => {
  const separator = url.includes('?') ? '&' : '?';
  shell.openExternal(`${url}${separator}apiPort=${apiPort}`);
});

// 在所有窗口关闭时退出应用
app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

// 添加退出应用的逻辑
app.on('before-quit', async () => {
  app.isQuitting = true;
  
  // 关闭数据库连接
  closeDatabase();
  
  // 停止 API 服务器
  await stopServer();
});

// 在现有代码中添加这个IPC监听器
ipcMain.handle('save-wallet-data', async (event, walletData) => {
  try {
    // 数据文件路径
    const dataPath = path.join(__dirname, 'wallet_data.json');
    
    // 读取现有数据
    let wallets = [];
    if (fs.existsSync(dataPath)) {
      try {
        const data = fs.readFileSync(dataPath, 'utf8');
        wallets = JSON.parse(data);
      } catch (err) {
        console.error('解析wallet_data.json失败:', err);
      }
    }
    
    // 准备钱包数据
    const wallet = {
      address: walletData.address,
      name: walletData.name || `Account ${walletData.address.substring(0, 6)}...`,
      balance: walletData.balance || '0 SUI',
      icon: walletData.icon || null,
      network: walletData.network || 'sui',
      last_updated: new Date().toISOString()
    };
    
    // 检查是否已存在该钱包
    const existingIndex = wallets.findIndex(w => w.address === wallet.address);
    
    if (existingIndex >= 0) {
      // 更新现有钱包
      wallets[existingIndex] = {
        ...wallets[existingIndex],
        ...wallet
      };
      console.log(`更新钱包信息: ${wallet.address}`);
    } else {
      // 添加新钱包
      wallets.push(wallet);
      console.log(`添加新钱包: ${wallet.address}`);
    }
    
    // 保存到文件
    fs.writeFileSync(dataPath, JSON.stringify(wallets, null, 2), 'utf8');
    
    return { success: true, wallet };
  } catch (err) {
    console.error('保存钱包数据失败:', err);
    return { success: false, error: err.message };
  }
});

// 添加清除钱包数据的处理函数
ipcMain.handle('clear-wallets', async () => {
  try {
    const dataPath = path.join(__dirname, 'wallet_data.json');
    fs.writeFileSync(dataPath, JSON.stringify([]), 'utf8');
    console.log('钱包数据已清除');
    return { success: true };
  } catch (err) {
    console.error('清除钱包数据失败:', err);
    return { success: false, error: err.message };
  }
});