# MemeVsTrump 🎮

一个多平台的区块链塔防游戏，融合了传统游戏体验与 Web3 技术。在这个游戏中，玩家使用各种Meme角色来阻止Trump到达白宫！

## 🌟 项目特色

- **多端支持**: Web DApp、Node.js 后端服务、独立Python游戏
- **区块链集成**: 基于 Sui 区块链，支持钱包连接和智能合约交互
- **塔防玩法**: 经典的塔防游戏机制，策略性强
- **现代技术栈**: React + TypeScript + Vite + Node.js/Express + Pygame + Move智能合约

## 🛠️ 技术栈

### 前端 Web 应用
- **React 18** - 用户界面框架
- **TypeScript** - 类型安全的JavaScript
- **Vite** - 快速构建工具
- **Radix UI** - 现代化UI组件库

### 后端服务
- **Node.js** - JavaScript 运行时
- **Express.js** - Web应用框架 (用于API服务)
- **CORS** - 处理跨域资源共享

### 区块链集成
- **Sui 区块链** - 高性能Layer1区块链
- **Move语言** - 智能合约开发
- **@mysten/dapp-kit** - Sui DApp开发工具包


### 游戏客户端
- **Python** - 游戏逻辑开发
- **Pygame** - 2D游戏开发库

## 📁 项目结构

```
memeVsTrump/
├── src/                    # Web应用源码 (前端)
├── public/               # 静态资源 (前端使用, 构建时复制)
├── pyrun/                # Python游戏客户端
│   ├── main.py           # Python游戏入口
│   ├── game.py           # 游戏主逻辑
│   ├── config.py         # Python游戏配置 (包含资源路径修正)
│   └── assets/           # Python游戏资源
├── server/               # Node.js 后端服务器
│   ├── index.cjs         # 后端服务器主文件 (CommonJS模块)
│   └── wallets.json      # 后端保存的钱包数据
├── move/                 # Move智能合约
│   └── meme_game/        # 游戏智能合约
│       ├── sources/      # 合约源代码
│       ├── tests/        # 合约测试
│       └── Move.toml     # 合约配置文件
├── package.json          # 项目配置和脚本
└── README.md             # 项目说明文档
```

## 🚀 快速开始

### 环境要求

- **Node.js** 18+ (包含 npm)
- **Python** 3.8+
- **Git**
- **Sui CLI** (用于智能合约开发)

### 安装依赖

```bash
# 克隆项目
git clone <your-repo-url>
cd memeVsTrump

# 安装Node.js依赖 (包括前端和后端)
npm install express cors concurrently nodemon --save-dev # 开发依赖
npm install # 安装其他在package.json中定义的依赖

# 设置Python虚拟环境并安装依赖
cd pyrun
python -m venv venv
# Windows激活:
# .\venv\Scripts\activate
# macOS/Linux激活:
# source venv/bin/activate
pip install -r requirements.txt # 确保pygame等已在requirements.txt中
cd ..
```

### 运行项目 (开发模式)

```bash
npm run dev
```
这将同时启动：
- **前端开发服务器**: 访问 `http://localhost:5173`
- **后端API服务器**: 监听 `http://localhost:3001` (前端会调用此API保存钱包数据)
- **Python Pygame游戏**: 游戏窗口会自动弹出

Python游戏的资源（图片等）现在会从 `pyrun/assets/` 目录正确加载，不受启动工作目录影响。
钱包数据会由前端发送到后端API，并保存在项目根目录下的 `server/wallets.json` 文件中。

### 其他脚本

- **仅启动前端**: `npm run dev:frontend`
- **仅启动后端**: `npm run dev:backend`
- **仅启动Python游戏**: `npm run dev:python` (确保Python虚拟环境已配置)

## 🎮 游戏玩法

1. **连接钱包**: 在Web应用 (`http://localhost:5173`) 中连接您的Sui钱包。
2. **保存钱包信息**: 点击"保存钱包信息"按钮，数据将通过后端API保存到 `server/wallets.json`。
3. **运行Python游戏**: Python游戏独立运行，展示Meme对战Trump的塔防场景。
4. **抽取NFT卡牌**: 使用钱包中的SUI代币抽取Meme NFT卡牌，用于游戏中部署防御单位。
5. **参与战斗**: 使用您的Meme NFT卡牌在游戏中部署防御单位，阻止Trump到达终点。

## 🔧 开发指南

### 前端 (React - `src/`)
- 修改UI组件、与Sui区块链交互、调用后端API。

### 后端 (Node.js/Express - `server/index.cjs`)
- 修改API逻辑，例如数据验证、不同的数据存储方式等。
- 当前钱包数据保存在 `server/wallets.json`。

### Python游戏 (Pygame - `pyrun/`)
- 修改游戏逻辑、角色、关卡等。
- 资源文件位于 `pyrun/assets/`，路径已在 `pyrun/config.py` 中配置为相对脚本位置加载。

### 智能合约 (Move - `move/meme_game/`)
- 修改智能合约逻辑、添加新功能、优化现有功能。
- 合约源代码位于 `move/meme_game/sources/`。
- 测试文件位于 `move/meme_game/tests/`。

## 🔗 智能合约功能

项目使用Sui Move语言开发了三个核心智能合约模块，实现了游戏的链上功能：

### 1. MemeNFT模块 (`meme_nft.move`)

这个模块负责NFT的基本功能：

- **NFT创建与管理**: 定义了MemeNFT结构，包含名称、描述、图片URL和稀有度等属性
- **NFT铸造**: 支持管理员铸造和抽卡系统铸造两种方式
- **NFT转移**: 允许用户之间转移NFT所有权
- **稀有度系统**: 实现了1-5级的稀有度系统，影响NFT的属性和价值
- **元数据展示**: 使用Sui的Display功能，使NFT在钱包和市场中能够正确显示

### 2. 抽卡系统模块 (`card_system.move`)

这个模块实现了游戏的抽卡机制：

- **卡片类型管理**: 定义了不同稀有度和类型的卡片，包括普通、稀有、史诗和传奇等
- **随机抽卡**: 基于概率分布的随机抽卡系统，稀有卡片的获取概率较低
- **单抽与十连抽**: 支持单次抽卡和十连抽，十连抽有优惠
- **费用管理**: 抽卡需要支付SUI代币，费用可由管理员设置
- **自动铸造NFT**: 抽卡成功后自动调用NFT模块铸造对应的NFT
- **抽卡记录**: 记录用户的抽卡历史，包括时间、卡片类型和NFT ID

### 3. 惩罚系统模块 (`penalty_system.move`)

这个模块负责游戏中的惩罚机制：

- **惩罚类型**: 支持多种惩罚类型，包括警告、禁止抽卡、禁止战斗和全面禁止等
- **时限惩罚**: 支持临时惩罚（有时间限制）和永久惩罚
- **惩罚管理**: 管理员可以应用和解除惩罚
- **自动过期**: 临时惩罚会自动过期，系统提供清理过期惩罚的功能
- **状态查询**: 提供接口查询用户是否有活跃惩罚，用于前端和游戏逻辑判断

## 📦 构建部署

### Web应用构建 (前端 + public资源)
```bash
npm run build
```
构建产物将位于 `dist/` 目录。

### 后端服务部署
- 后端服务 (`server/index.cjs` 和 `server/wallets.json`) 需要部署在一个Node.js运行环境中。
- 确保 `wallets.json` 文件有写入权限。

### Python游戏分发
- 可以使用如 PyInstaller 之类的工具将Python游戏打包成可执行文件。

### 智能合约部署
```bash
cd move/meme_game
sui client publish --gas-budget 20000000
```

部署后，需要：
1. 记录部署生成的Package ID
2. 更新前端代码中的合约地址（在`src/constants.ts`中）
3. 初始化必要的合约对象（如创建卡片配置和惩罚系统）

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 `LICENSE` 文件了解详情。

## 🆘 故障排除

### 常见问题

**Q: 后端服务器无法启动或API调用失败?**
A: 
  - 确保已安装 `express` 和 `cors` (`npm install express cors`)。
  - 检查 `server/index.cjs` 中的端口是否被占用 (默认为3001)。
  - 查看后端服务器的控制台日志获取错误信息。
  - 确认前端API调用地址 (`http://localhost:3001/api/wallets`) 正确。

**Q: Python游戏无法启动或资源加载失败?**
A: 
  - 确保已在 `pyrun/` 目录下正确设置Python虚拟环境 (`venv`) 并已安装 `pygame` 等依赖 (通过 `pip install -r pyrun/requirements.txt`)。
  - `pyrun/config.py` 已被修改为从脚本自身相对路径加载 `pyrun/assets/` 中的资源，通常能解决路径问题。
  - 检查Python控制台的错误输出。

**Q: Web应用无法连接钱包?**
A: 确保已安装Sui钱包浏览器插件并已连接到正确的网络。

**Q: 智能合约部署失败?**
A:
  - 确保已安装Sui CLI并配置了钱包。
  - 检查钱包中是否有足够的SUI代币支付Gas费用。
  - 检查Move.toml文件中的依赖配置是否正确。
  - 查看部署时的错误信息，可能是合约代码中有语法或逻辑错误。

## 🔗 相关链接

- [Sui 开发文档](https://docs.sui.io/)
- [Sui Move 语言文档](https://docs.sui.io/guides/developer/sui-move-concepts)
- [Pygame 文档](https://www.pygame.org/docs/)
- [Express.js 文档](https://expressjs.com/)
- [Node.js 文档](https://nodejs.org/)
- [React 文档](https://react.dev/)


