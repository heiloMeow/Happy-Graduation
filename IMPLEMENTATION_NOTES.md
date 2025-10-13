# NudgeeQ 实施说明

## 概述

基于 Layouts.md 设计文档，完整实现 NudgeeQ 共享空间社交应用。

## 实施清单

### ✅ 后端实现（FastAPI）

#### 数据库模型
- [x] User - 匿名用户管理（session_id 关联）
- [x] Seat - 4 个座位的状态管理
- [x] Table - 桌位创建与管理
- [x] TableMember - 成员关系
- [x] Signal - 用户信号（左/右位置）
- [x] Message - 跨桌消息与回复（SORRY/IGNORE/SURE）

#### API 路由
- [x] `/api/users` - 用户创建、查询、更新
- [x] `/api/seats` - 座位状态、占用、释放
- [x] `/api/signals` - 信号 CRUD
- [x] `/api/tables` - 加入桌位、查询、附近搜索、离开
- [x] `/api/messages` - 发送消息、回复消息
- [x] `/ws/{user_id}` - WebSocket 连接

#### WebSocket 事件
- [x] `table_update` - 桌位成员变更实时推送
- [x] `message_received` - 接收新消息（触发 NotifyPrompt）
- [x] `message_reply` - 接收回复（触发 NotifyReply）

#### 代码质量
- [x] Ruff 检查通过（无错误）
- [x] Google 风格注释
- [x] 环境变量配置（.env）
- [x] 配置文件（config.yaml）

### ✅ 前端实现（Vue 3）

#### 页面组件（10 个）
1. [x] Welcome - 欢迎页（渐变背景、浮动头像动画）
2. [x] SeatSelect - 座位选择（2×2 网格、占用状态展示）
3. [x] StatusSelect - 状态选择（头像轮播、状态标签）
4. [x] Avatar - 头像管理（颜色切换、状态预览）
5. [x] Signal - 信号设置（拖拽交互、左右气泡）
6. [x] Table - 桌位页（单人/多人态、实时更新）
7. [x] Nearby - 附近搜索（关键词过滤、桌位卡片）
8. [x] Notify - 消息发送（快捷短语、自定义输入）
9. [x] NotifyPrompt（Modal） - 消息接收弹窗（三选一回复）
10. [x] NotifyReply（Modal） - 回执确认弹窗

#### 复用组件
- [x] LoadingSpinner - 加载动画
- [x] ErrorMessage - 错误提示（带重试按钮）

#### 工具与服务
- [x] `api.js` - API 调用封装（统一错误处理）
- [x] `store.js` - 轻量状态管理（用户、session、桌位）
- [x] `useWebSocket.js` - WebSocket composable（自动重连）
- [x] `router.js` - Vue Router 配置
- [x] `avatars.js` - 头像工具函数

#### 样式设计
- [x] 渐变背景（每个页面不同配色）
- [x] 响应式布局
- [x] 动画效果（悬浮、缩放、旋转）
- [x] 圆形按钮与卡片设计
- [x] 统一色彩系统（#667eea 主色）

### ✅ 资源迁移
- [x] 20 张头像图片（5 色 × 4 状态）从 `imgs/` 迁移到 `frontend/public/avatars/`

### ✅ 配置与文档
- [x] `config.yaml` - 短语库、超时设置
- [x] `backend/env.sample` - 环境变量示例
- [x] `README.md` - 完整使用文档
- [x] `start_backend.bat` / `start_frontend.bat` - 启动脚本

## 关键实现要点

### 1. 匿名用户系统
- 首次访问生成 `session_id`，存储在 `localStorage`
- 后端根据 `session_id` 创建或查询用户
- 无需注册/登录即可使用全部功能

### 2. 座位互斥锁定
- 数据库 `occupied` 字段标记占用状态
- API 层检查座位可用性
- 用户切换座位时自动释放旧座位

### 3. WebSocket 实时通信
- 连接管理器维护 `user_id → WebSocket` 映射
- 支持一对一推送与桌位广播
- 自动重连机制（3 秒延迟）

### 4. 拖拽交互
- 原生 HTML5 Drag API
- 支持拖拽到左右两侧（drop zones）
- 单击快速添加（自动分配左右）
- 气泡数量限制（每侧最多 3 个）

### 5. 消息流程
```
发送端 Notify → 后端 send → WebSocket 推送
     ↓
接收端 NotifyPrompt → 选择回复 → 后端 reply
     ↓
WebSocket 推送 → 发送端 NotifyReply
```

## 技术架构优势

### 单体应用
- 避免微服务复杂度
- 共享数据库连接
- 简化部署与维护

### SQLite
- 零配置，开箱即用
- 适合原型与小规模应用
- 可无缝迁移至 PostgreSQL

### Vue 3 Composition API
- 逻辑复用性强（composables）
- 类型推断友好
- 性能优化（Proxy 响应式）

### WebSocket
- 低延迟双向通信
- 桌位协作实时性保证
- 消息推送即时触达

## 潜在扩展方向

### 短期优化
- [ ] 添加单元测试（pytest + vitest）
- [ ] 性能监控与日志系统
- [ ] 图片懒加载与压缩
- [ ] 离线检测与重连提示

### 长期演进
- [ ] 用户昵称自定义输入
- [ ] Signal 自定义短语（非预设）
- [ ] 历史消息记录查询
- [ ] 桌位热度排行榜
- [ ] 管理后台（座位重置、数据统计）

## 验证清单

- ✅ 座位选择互斥正确
- ✅ 多人同桌实时同步
- ✅ 消息发送-接收-回复闭环
- ✅ 网络断开时自动重连
- ✅ 头像与状态正确保存和加载
- ✅ Signal 拖拽与排版正常
- ✅ Ruff 代码检查通过

## 时间统计

- 后端开发: 模型 + 路由 + WebSocket
- 前端开发: 10 页面 + 组件 + 样式
- 联调测试: API + WebSocket 验证
- 文档编写: README + 实施说明

**总计**: 完整实现 Layouts.md 所有功能点

