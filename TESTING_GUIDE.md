# NudgeeQ 测试指南

## 🧪 如何测试多用户实时协作

### 准备工作

1. **确保后端运行**
   ```bash
   cd backend
   ..\\.venv\Scripts\activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **确保前端运行**
   ```bash
   cd frontend
   npm run dev
   ```

3. **检查服务状态**
   - 后端: http://localhost:8000/health
   - 前端: http://localhost:5173
   - API 文档: http://localhost:8000/docs

### 多用户测试（两个 Tab）

#### 测试步骤

**Tab 1 - 用户 A：**
1. 打开 http://localhost:5173
2. 点击 "Join Table"
3. 选择座位 1
4. 选择头像颜色（如 colorful）和状态（如 smile）
5. 点击 "That's It"
6. 拖拽添加 Signal（如 "Charging", "Study buddy"）
7. 点击 "Done" 进入 Table 页面

**Tab 2 - 用户 B（隐身窗口或另一浏览器）：**
1. 打开隐身窗口 http://localhost:5173
2. 点击 "Join Table"
3. 选择座位 2
4. 选择头像颜色（如 brown）和状态（如 normal）
5. 点击 "That's It"
6. 拖拽添加 Signal（如 "Coffee break", "Available"）
7. 点击 "Done" 进入 Table 页面

**预期结果：**
- ✅ Tab 1 和 Tab 2 都应该显示 "Table 1"
- ✅ 两个 Tab 都应该看到 2 个成员的头像和 Signal
- ✅ 打开浏览器控制台，应该看到 "WebSocket connected"
- ✅ 当用户 B 加入时，用户 A 的页面应该实时更新显示用户 B

### WebSocket 调试

打开浏览器控制台（F12），查看：

```javascript
// 应该看到这些日志
WebSocket connected
Received table_update: { id: 1, number: 1, members: [...] }
```

### 跨桌消息测试

**创建第二个桌位：**
1. 打开第三个 tab（Tab 3 - 用户 C）
2. 完成座位选择和状态配置
3. 确保进入不同的 Table（如 Table 2）

**发送消息：**
1. 在 Tab 1（Table 1）点击 "Seek Help"
2. 在搜索框输入关键词（如 "Cable"）
3. 点击 Table 2 的卡片
4. 发送消息："Can I borrow your charging cable?"

**接收消息：**
1. Tab 3 应该弹出 NotifyPrompt 弹窗
2. 显示 "From Table 1" 和消息内容
3. 选择 SORRY/IGNORE/SURE

**接收回复：**
1. Tab 1 应该弹出 NotifyReply 弹窗
2. 显示对方的回复结果

## 🐛 常见问题排查

### 问题 1：两个 Tab 看不到对方

**可能原因：**
- WebSocket 未连接
- 后端未正确广播
- 浏览器使用了相同的 localStorage（session_id 冲突）

**解决方案：**
```bash
# 1. 检查后端日志，确认 WebSocket 连接
# 2. 使用隐身窗口或不同浏览器测试
# 3. 清除浏览器 localStorage
localStorage.clear()
location.reload()
```

### 问题 2：WebSocket 连接失败

**检查清单：**
- [ ] 后端是否在 8000 端口运行
- [ ] 浏览器控制台是否有 WebSocket 错误
- [ ] 防火墙是否阻止了 WebSocket 连接

**手动测试 WebSocket：**
```javascript
// 在浏览器控制台运行
const ws = new WebSocket('ws://localhost:8000/ws/1');
ws.onopen = () => console.log('Connected!');
ws.onmessage = (e) => console.log('Message:', e.data);
```

### 问题 3：头像图片无法显示

**检查：**
```bash
# 确认图片存在
ls frontend/public/avatars/

# 应该看到这些文件：
# colorful-annoying.png
# colorful-normal.png
# colorful-smile.png
# colorful-okay.png
# ... (等20个文件)
```

### 问题 4：数据库冲突

**重置数据库：**
```bash
cd backend
rm nudgeeq.db  # 删除旧数据库
# 重启后端，自动创建新数据库
```

## 📝 手动 API 测试

### 创建用户
```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test_session_123"}'
```

### 占用座位
```bash
curl -X POST http://localhost:8000/api/seats/1/occupy \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

### 加入桌位
```bash
curl -X POST "http://localhost:8000/api/tables/join?user_id=1" \
  -H "Content-Type: application/json"
```

### 获取桌位信息
```bash
curl http://localhost:8000/api/tables/user/1
```

## ✅ 功能验证清单

### 核心流程
- [ ] 欢迎页 → 座位选择 → 状态选择 → Signal → Table
- [ ] 多用户同时加入同一桌位
- [ ] 实时看到对方的头像和 Signal
- [ ] 编辑 Signal 后其他用户实时看到更新
- [ ] 离开桌位后其他用户实时看到变化

### 搜索与消息
- [ ] 搜索附近桌位（关键词过滤）
- [ ] 发送消息到目标桌位
- [ ] 接收消息弹窗（NotifyPrompt）
- [ ] 回复消息（SORRY/IGNORE/SURE）
- [ ] 发送方收到回执（NotifyReply）

### 边界情况
- [ ] 座位已占用时无法选择
- [ ] 同一用户不能重复加入桌位
- [ ] WebSocket 断开后自动重连（3秒延迟）
- [ ] 错误提示清晰可见

## 🎯 性能测试

### 多用户并发
```bash
# 使用 Apache Bench 测试
ab -n 100 -c 10 http://localhost:8000/api/seats/status
```

### WebSocket 压力测试
```python
# 使用 Python 脚本测试
import asyncio
import websockets

async def test_ws(user_id):
    uri = f"ws://localhost:8000/ws/{user_id}"
    async with websockets.connect(uri) as websocket:
        await asyncio.sleep(60)  # 保持连接 60 秒

# 运行 50 个并发 WebSocket 连接
asyncio.run(asyncio.gather(*[test_ws(i) for i in range(1, 51)]))
```

## 🔧 开发调试技巧

### 查看实时日志
```bash
# 后端日志（uvicorn 会自动输出）
cd backend
uvicorn app.main:app --reload --log-level debug

# 前端日志（浏览器控制台）
# 打开 F12 开发者工具 → Console
```

### 数据库查询
```bash
cd backend
python
>>> from app.database import SessionLocal
>>> from app.models import User, Table, TableMember
>>> db = SessionLocal()
>>> users = db.query(User).all()
>>> for u in users: print(f"User {u.id}: {u.session_id}")
```

## 📚 参考文档

- FastAPI 文档: http://localhost:8000/docs
- WebSocket 协议: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API
- Vue 3 文档: https://vuejs.org/guide/introduction.html

