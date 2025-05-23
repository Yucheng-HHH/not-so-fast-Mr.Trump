const express = require('express');
const path = require('path');
const { app } = require('electron');
const fs = require('fs');
const cors = require('cors');

// 默认存放在electron目录
const defaultDataPath = path.join(__dirname, 'wallet_data.json');

function startServer(customDataPath) {
  const server = express();
  server.use(cors());
  server.use(express.json());
  
  // 使用传入的路径或默认路径
  const dataPath = customDataPath || defaultDataPath;
  
  // 初始化内存数据存储
  let wallets = [];
  try {
    // 无论文件是否存在，都创建/覆盖为新的空数组文件
    wallets = [];
    fs.writeFileSync(dataPath, JSON.stringify(wallets), 'utf8');
    console.log(`初始化了数据文件: ${dataPath}`);
  } catch (err) {
    console.error('数据初始化失败:', err.message);
    throw err;
  }

  // API路由
  server.get('/api/wallets', (req, res) => {
    res.json(wallets);
  });

  server.post('/api/wallets', (req, res) => {
    const { address, balance } = req.body;
    try {
      const now = new Date().toISOString();
      const existingIndex = wallets.findIndex(w => w.address === address);
      
      if (existingIndex >= 0) {
        wallets[existingIndex] = {
          ...wallets[existingIndex],
          balance: balance || '0',
          last_updated: now
        };
      } else {
        wallets.push({
          address,
          balance: balance || '0',
          last_updated: now
        });
      }
      
      // 保存更新
      fs.writeFileSync(dataPath, JSON.stringify(wallets), 'utf8');
      
      const walletInfo = wallets.find(w => w.address === address);
      res.status(201).json(walletInfo);
    } catch (err) {
      res.status(400).json({ error: err.message });
    }
  });

  // 启动服务器
  const port = 3000;
  const serverInstance = server.listen(port, () => {
    console.log(`API服务器运行在: http://localhost:${port}`);
  });

  return {
    close: () => {
      // 保存数据
      try {
        fs.writeFileSync(dataPath, JSON.stringify(wallets), 'utf8');
      } catch (err) {
        console.error('关闭服务器时保存数据失败:', err.message);
      }
      serverInstance.close();
    }
  };
}

module.exports = { startServer };