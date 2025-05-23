const path = require('path');
const { app } = require('electron');
const fs = require('fs');

// 默认存放在electron目录下
const dataPath = path.join(__dirname, 'wallet_data.json');
console.log('Data path:', dataPath);

// 使用内存存储数据
let wallets = [];

function initDatabase() {
  try {
    // 无论文件是否存在，都创建/覆盖为新的空数组文件
    wallets = [];
    fs.writeFileSync(dataPath, JSON.stringify(wallets), 'utf8');
    console.log('Initialized wallet_data.json with empty array');
    
    return true;
  } catch (err) {
    console.error('Data initialization failed:', err.message);
    return false;
  }
}

// 添加或更新钱包信息
function upsertWallet(walletData) {
  try {
    const { address, name, balance, icon, network = 'sui' } = walletData;
    
    // 检查钱包是否已存在
    const existingIndex = wallets.findIndex(w => w.address === address);
    const displayName = name || `Account ${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
    
    const walletInfo = {
      address,
      name: displayName,
      balance: balance || '0 SUI',
      icon: icon || null,
      network,
      last_updated: Date.now()
    };
    
    if (existingIndex >= 0) {
      wallets[existingIndex] = walletInfo;
    } else {
      wallets.push(walletInfo);
    }
    
    // 保存到文件
    fs.writeFileSync(dataPath, JSON.stringify(wallets), 'utf8');
    
    return { success: true, id: existingIndex >= 0 ? existingIndex : wallets.length - 1 };
  } catch (err) {
    console.error('Error saving wallet:', err.message);
    return { success: false, error: err.message };
  }
}

// 获取所有钱包
function getWallets() {
  try {
    // 按最后更新时间排序
    const sortedWallets = [...wallets].sort((a, b) => b.last_updated - a.last_updated);
    return { success: true, wallets: sortedWallets };
  } catch (err) {
    console.error('Error getting wallets:', err.message);
    return { success: false, error: err.message, wallets: [] };
  }
}

// 获取特定钱包
function getWallet(address) {
  try {
    const wallet = wallets.find(w => w.address === address);
    return { success: true, wallet };
  } catch (err) {
    console.error('Error getting wallet:', err.message);
    return { success: false, error: err.message };
  }
}

// 删除钱包
function deleteWallet(address) {
  try {
    const initialLength = wallets.length;
    wallets = wallets.filter(w => w.address !== address);
    const deleted = initialLength > wallets.length;
    
    // 保存到文件
    if (deleted) {
      fs.writeFileSync(dataPath, JSON.stringify(wallets), 'utf8');
    }
    
    return { success: true, deleted };
  } catch (err) {
    console.error('Error deleting wallet:', err.message);
    return { success: false, error: err.message };
  }
}

// 清理资源
function closeDatabase() {
  try {
    // 保存到文件
    fs.writeFileSync(dataPath, JSON.stringify(wallets), 'utf8');
    console.log('Data saved successfully');
  } catch (err) {
    console.error('Error saving data:', err.message);
  }
}

module.exports = {
  initDatabase,
  upsertWallet,
  getWallets,
  getWallet,
  deleteWallet,
  closeDatabase
};