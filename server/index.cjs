const express = require('express');
const fs = require('fs');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3001;

// 数据存储路径
const WALLETS_DATA_PATH = path.join(__dirname, 'wallets.json');

// 中间件
app.use(cors({ origin: 'http://localhost:5173' })); // 允许来自Vite开发服务器的请求
app.use(express.json()); // 解析JSON请求体

// 初始化数据文件（如果不存在）
const initializeWalletsFile = () => {
  if (!fs.existsSync(WALLETS_DATA_PATH)) {
    try {
      fs.writeFileSync(WALLETS_DATA_PATH, JSON.stringify([], null, 2), 'utf8');
      console.log(`Wallets data file created at ${WALLETS_DATA_PATH}`);
    } catch (err) {
      console.error('Error creating wallets data file:', err);
    }
  }
};

initializeWalletsFile();

// API端点：保存钱包数据
app.post('/api/wallets', (req, res) => {
  const newWalletData = req.body;

  if (!newWalletData || !newWalletData.address) {
    return res.status(400).json({ success: false, message: 'Invalid wallet data. Address is required.' });
  }

  try {
    let wallets = [];
    // 读取现有数据
    if (fs.existsSync(WALLETS_DATA_PATH)) {
      const fileData = fs.readFileSync(WALLETS_DATA_PATH, 'utf8');
      wallets = JSON.parse(fileData);
      if (!Array.isArray(wallets)) {
        wallets = []; // 如果内容不是数组，则重置
      }
    }

    // 检查钱包是否已存在，如果存在则更新，否则添加
    const existingWalletIndex = wallets.findIndex(
      (wallet) => wallet.address === newWalletData.address
    );

    if (existingWalletIndex > -1) {
      wallets[existingWalletIndex] = {
        ...wallets[existingWalletIndex], // 保留旧数据（如果有其他字段）
        ...newWalletData, // 用新数据覆盖/添加字段
        last_updated: new Date().toISOString() // 总是更新时间戳
      };
      console.log(`Wallet updated: ${newWalletData.address}`);
    } else {
      wallets.push({...newWalletData, last_updated: new Date().toISOString()});
      console.log(`New wallet added: ${newWalletData.address}`);
    }

    // 将更新后的列表存回文件
    fs.writeFileSync(WALLETS_DATA_PATH, JSON.stringify(wallets, null, 2), 'utf8');
    res.status(200).json({ success: true, message: 'Wallet data saved successfully.', wallet: newWalletData });

  } catch (error) {
    console.error('Error saving wallet data:', error);
    res.status(500).json({ success: false, message: 'Failed to save wallet data.', error: error.message });
  }
});

// API端点：获取所有钱包数据（可选，用于测试或未来功能）
app.get('/api/wallets', (req, res) => {
  try {
    if (fs.existsSync(WALLETS_DATA_PATH)) {
      const fileData = fs.readFileSync(WALLETS_DATA_PATH, 'utf8');
      const wallets = JSON.parse(fileData);
      res.status(200).json({ success: true, wallets });
    } else {
      res.status(200).json({ success: true, wallets: [] });
    }
  } catch (error) {
    console.error('Error fetching wallets data:', error);
    res.status(500).json({ success: false, message: 'Failed to fetch wallets data.', error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Backend server is running on http://localhost:${PORT}`);
}); 