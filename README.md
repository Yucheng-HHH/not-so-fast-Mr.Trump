# MemeVsTrump 🎮

一个多平台的区块链塔防游戏，融合了传统游戏体验与 Web3 技术。在这个游戏中，玩家使用各种Meme角色来阻止Trump到达白宫！

## 🌟 项目特色

- **多端支持**: Web DApp、桌面应用、独立Python游戏
- **区块链集成**: 基于 Sui 区块链，支持钱包连接和智能合约交互
- **塔防玩法**: 经典的塔防游戏机制，策略性强
- **现代技术栈**: React + TypeScript + Electron + Move智能合约

## 🛠️ 技术栈

### 前端 Web 应用
- **React 18** - 用户界面框架
- **TypeScript** - 类型安全的JavaScript
- **Vite** - 快速构建工具
- **Radix UI** - 现代化UI组件库

### 区块链集成
- **Sui 区块链** - 高性能Layer1区块链
- **Move语言** - 智能合约开发
- **@mysten/dapp-kit** - Sui DApp开发工具包

### 桌面应用
- **Electron** - 跨平台桌面应用框架
- **Express** - 内置API服务器
- **SQLite** - 本地数据存储

### 游戏客户端
- **Python** - 游戏逻辑开发
- **Pygame** - 2D游戏开发库

## 📁 项目结构

```
memeVsTrump/
├── src/                    # Web应用源码
│   ├── App.tsx            # 主应用组件
│   ├── Counter.tsx        # 计数器组件
│   ├── SaveWalletButton.tsx # 钱包功能
│   └── networkConfig.ts   # Sui网络配置
├── electron/              # Electron桌面应用
│   ├── main.cjs          # 主进程
│   ├── api-server.cjs    # API服务器
│   └── database.cjs      # 数据库操作
├── pyrun/                # Python游戏客户端
│   ├── game.py           # 游戏主逻辑
│   ├── player.py         # 玩家管理
│   ├── trump.py          # Trump角色
│   └── meme_card.py      # Meme卡片
├── move/                 # Move智能合约
│   └── counter/          # 计数器合约
├── public/               # 静态资源
│   ├── launcher.html     # 游戏启动器
│   └── assets/           # 游戏资源
└── package.json          # 项目配置
```

## 🚀 快速开始

### 环境要求

- **Node.js** 18+
- **Python** 3.8+
- **Git**
- **Sui CLI** (用于智能合约开发)

### 安装依赖

```bash
# 克隆项目
git clone <your-repo-url>
cd memeVsTrump

# 安装Node.js依赖
npm install

# 安装Python依赖
cd pyrun
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 运行项目

#### 🌐 Web DApp 开发模式
```bash
npm run dev
```
访问: http://localhost:5173

#### 🖥️ Electron 桌面应用
```bash
# 开发模式
npm run electron:dev

# 构建应用
npm run electron:build
```

#### 🐍 Python 游戏
```bash
cd pyrun
python main.py
```

#### 📝 智能合约开发
```bash
cd move/counter
sui move build
sui move test
```

## 🎮 游戏玩法

1. **选择Meme角色**: 使用游戏货币抽取不同的Meme卡片
2. **战略布局**: 在游戏板上策略性地放置Meme角色
3. **阻止Trump**: 防止Trump到达白宫
4. **升级装备**: 通过胜利获得更多资源和强力Meme

## 🔧 开发指南

### 添加新的Meme角色

1. 在 `pyrun/config.py` 的 `PREDEFINED_MEMES_POOL` 中添加新角色定义
2. 在 `public/assets/` 中添加角色图片
3. 更新 `pyrun/meme_card.py` 添加特殊能力（如需要）

### 修改游戏平衡

- **Trump属性**: 编辑 `pyrun/trump.py`
- **Meme属性**: 编辑 `pyrun/config.py` 中的数值
- **战斗配置**: 编辑 `pyrun/battle_config.py`

### 区块链功能开发

1. 在 `move/counter/sources/` 中编写Move合约
2. 在 `src/` 中添加前端交互逻辑
3. 更新 `src/networkConfig.ts` 配置网络参数

## 📦 构建部署

### Web应用构建
```bash
npm run build
```

### Electron应用打包
```bash
npm run electron:build
```

### 智能合约部署
```bash
cd move/counter
sui client publish --gas-budget 20000000
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 故障排除

### 常见问题

**Q: Python游戏无法启动?**
A: 确保已激活虚拟环境并安装了所有依赖：
```bash
cd pyrun
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Q: Web应用无法连接钱包?**
A: 确保已安装Sui钱包插件并已连接到正确的网络。

**Q: Electron应用打包失败?**
A: 确保已安装所有依赖并运行了 `npm run build`。

## 🔗 相关链接

- [Sui 开发文档](https://docs.sui.io/)
- [Pygame 文档](https://www.pygame.org/docs/)
- [Electron 文档](https://www.electronjs.org/docs)
- [React 文档](https://react.dev/)

## 📞 联系我们

如有问题或建议，请通过以下方式联系：

- 创建 [Issue](../../issues)
- 发送邮件至: [yucheng.huanggd@gmail.com]

---

**祝您游戏愉快！🎉**
