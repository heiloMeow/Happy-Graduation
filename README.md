# NudgeeQ Web App

共享空间社交协作应用，支持实时座位管理、状态信号展示和跨桌消息通信。

## 技术栈

- 后端: FastAPI + SQLAlchemy + SQLite + WebSocket
- 前端: Vue 3 (Composition API) + Vite
- 实时通信: WebSocket

## 快速开始

### 方法 1: 使用启动脚本（Windows）

双击运行：
- `start_backend.bat` - 启动后端服务
- `start_frontend.bat` - 启动前端服务

### 方法 2: 手动启动

#### 后端

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境（Windows）
.venv\Scripts\activate

# 安装依赖
pip install -r backend/requirements.txt

# 创建 .env 配置文件
copy backend\env.sample backend\.env

# 启动后端服务
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端

```bash
cd frontend
npm install
npm run dev
```

## 访问应用

- 前端应用: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

## 功能特性

### 核心流程
1. **欢迎页** - 品牌展示与加入入口
2. **座位选择** - 4 个座位的互斥选择（Step 1）
3. **状态配置** - 选择头像颜色与状态（Step 2）
4. **信号设置** - 拖拽创建左右两侧的 Signal 气泡（Step 3）
5. **桌位主页** - 单人/多人态实时展示，支持编辑信号
6. **附近搜索** - 按关键词筛选其他桌位
7. **消息发送** - 向目标桌位发送快捷或自定义消息
8. **消息接收** - 弹窗选择 SORRY/IGNORE/SURE 三种回复
9. **回执确认** - 发送端收到对方的处理结果

### 技术亮点
- ✅ 匿名用户系统（基于 session_id）
- ✅ 座位互斥锁定
- ✅ WebSocket 实时推送（桌位变更、消息通知）
- ✅ 拖拽交互（Signal 设置）
- ✅ 响应式设计（渐变背景、动画效果）
- ✅ Ruff 代码质量检查通过

## 项目结构

```
fe/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── main.py      # 应用入口
│   │   ├── models.py    # 数据模型
│   │   ├── schemas.py   # Pydantic schemas
│   │   ├── database.py  # 数据库配置
│   │   └── routers/     # API 路由
│   ├── requirements.txt
│   └── env.sample
├── frontend/             # Vue3 前端
│   ├── src/
│   │   ├── views/       # 页面组件
│   │   ├── components/  # 复用组件
│   │   ├── composables/ # WebSocket hook
│   │   ├── api.js       # API 调用封装
│   │   ├── router.js    # 路由配置
│   │   └── store.js     # 状态管理
│   ├── public/avatars/  # 头像资源
│   └── package.json
├── config.yaml          # 应用配置
└── README.md

## 配置说明

### backend/.env
```
DATABASE_URL=sqlite:///./nudgeeq.db
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### config.yaml
- 座位数量配置
- Signal 短语库
- 消息超时设置
- 桌号自动分配规则

## 数据模型

- **User**: 匿名用户（session_id, avatar_color, avatar_status）
- **Seat**: 座位状态（number, occupied, current_user_id）
- **Table**: 桌位（number, created_at）
- **TableMember**: 成员关联
- **Signal**: 用户信号（text, position: left/right）
- **Message**: 跨桌消息（content, reply: SORRY/IGNORE/SURE）

## 开发说明

### 后端开发
```bash
# 代码检查
ruff check backend/app

# 自动修复
ruff check backend/app --fix

# 运行测试
cd backend
pytest
```

### 前端开发
```bash
cd frontend
npm run dev    # 开发服务器
npm run build  # 生产构建
npm run preview # 预览构建
```

## 故障排查

### 座位无法占用
- 检查后端服务是否运行
- 确认用户已正确创建（检查 localStorage 中的 session_id）

### WebSocket 无法连接
- 确认后端运行在 8000 端口
- 检查浏览器控制台的 WebSocket 连接状态
- 确认用户 ID 存在

### 头像图片无法显示
- 确认 `frontend/public/avatars/` 目录包含所有图片
- 检查图片命名格式：`{颜色}-{状态}.png`

## 许可证

MIT License

