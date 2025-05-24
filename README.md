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

### 桌面应用 (已移除)
- ~~Electron - 跨平台桌面应用框架~~

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
│   └── counter/          # 计数器合约
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
4. **(未来)**: 可以将Web端保存的钱包数据或游戏状态与Python游戏进行某种形式的交互。

## 🔧 开发指南

### 前端 (React - `src/`)
- 修改UI组件、与Sui区块链交互、调用后端API。

### 后端 (Node.js/Express - `server/index.cjs`)
- 修改API逻辑，例如数据验证、不同的数据存储方式等。
- 当前钱包数据保存在 `server/wallets.json`。

### Python游戏 (Pygame - `pyrun/`)
- 修改游戏逻辑、角色、关卡等。
- 资源文件位于 `pyrun/assets/`，路径已在 `pyrun/config.py` 中配置为相对脚本位置加载。

### 数据同步到 `public` 目录 (可选)
如果您希望将后端动态保存的 `server/wallets.json` 的内容在**下一次构建时**包含到静态资源中 (即复制到 `public/wallets.json` 以便通过 `dist/wallets.json` 访问)，您需要在 `npm run build` 之前手动或通过脚本完成复制。例如，修改 `package.json` 的 `build` 脚本：
```json
"scripts": {
  // ...
  "copy-wallets-to-public": "node -e \"require('fs').copyFileSync('server/wallets.json', 'public/wallets.json', (err) => { if (err) throw err; console.log('wallets.json copied to public'); });\"", // 跨平台Node.js复制
  "build": "npm run copy-wallets-to-public && tsc && vite build"
}
```
*注意: 上述 `copy-wallets-to-public` 脚本是一个简单的Node.js内联命令，用于跨平台复制。如果 `public/wallets.json` 不存在，它会创建。如果目标文件已存在，它会被覆盖。*

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

本项目采用 MIT 许可证 - 查看 `LICENSE` 文件了解详情 (如果项目中没有，建议添加一个)。

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

## 🔗 相关链接

- [Sui 开发文档](https://docs.sui.io/)
- [Pygame 文档](https://www.pygame.org/docs/)
- [Express.js 文档](https://expressjs.com/)
- [Node.js 文档](https://nodejs.org/)
- [React 文档](https://react.dev/)

## 📞 联系我们

如有问题或建议，请通过以下方式联系：

- 创建 [Issue](../../issues) (如果您的仓库在GitHub等平台)
- 发送邮件至: [yucheng.huanggd@gmail.com]

---

**祝您开发愉快！🎉**
