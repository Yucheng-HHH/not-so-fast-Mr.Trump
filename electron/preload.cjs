const { contextBridge, ipcRenderer } = require('electron');

// 暴露给渲染进程的 API
contextBridge.exposeInMainWorld('electron', {
  // 发送消息给主进程
  openExternal: (url) => ipcRenderer.send('open-external', url),
  // 连接钱包
  connectWallet: (url) => ipcRenderer.send('connect-wallet', url),
  // 获取钱包数据
  getWallets: () => ipcRenderer.invoke('get-wallets'),
  // 获取 API 端口
  getApiPort: () => ipcRenderer.invoke('get-api-port'),
  // 保存钱包数据
  saveWalletData: (walletData) => ipcRenderer.invoke('save-wallet-data', walletData),
  // 清除钱包数据
  clearWallets: () => ipcRenderer.invoke('clear-wallets')
});

// 通知渲染进程预加载脚本已完成执行
window.addEventListener('DOMContentLoaded', () => {
  console.log('Preload script loaded successfully');
});