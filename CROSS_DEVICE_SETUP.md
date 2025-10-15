# 跨设备使用指南 - Cross-Device Setup Guide

## 📱 方案概述

你的系统**已经支持**跨设备、跨桌子通信！以下是三种部署方案：

### 方案对比

| 方案 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| **局域网** | 同一 WiFi | 免费、快速 | 仅限局域网 |
| **内网穿透** | 任何网络 | 配置简单 | 速度较慢 |
| **云部署** | 正式产品 | 稳定、快速 | 需要服务器 |

---

## 🏠 方案 1：局域网访问（推荐测试使用）

### 原理
- 后端运行在一台电脑（服务器）
- 同一 WiFi 下的其他设备通过 IP 地址访问

### 步骤

#### 1. 在服务器电脑上启动后端

```bash
# 双击运行
start_backend.bat

# 或手动运行
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**注意**：`--host 0.0.0.0` 允许局域网访问（已配置）

#### 2. 获取服务器 IP 地址

Windows 命令：
```bash
ipconfig
```

查找 "IPv4 地址"，例如：`192.168.1.100`

macOS/Linux 命令：
```bash
ifconfig | grep inet
```

#### 3. 配置前端

**在服务器电脑上**（运行 Table 1）：
```bash
cd frontend

# 创建 .env 文件
echo VITE_API_BASE=http://localhost:8000/api > .env

# 启动前端
npm run dev
```

**在其他电脑上**（运行 Table 2）：
```bash
cd frontend

# 创建 .env 文件，使用服务器 IP
echo VITE_API_BASE=http://192.168.1.100:8000/api > .env

# 启动前端
npm run dev
```

#### 4. 测试跨设备通信

- 电脑 1：访问 `http://localhost:5173`，加入 Table 1
- 电脑 2：访问 `http://localhost:5173`，加入 Table 2
- 尝试发送消息，验证跨桌通信

### 防火墙配置

如果无法连接，需要开放端口：

**Windows 防火墙**：
1. 控制面板 → Windows Defender 防火墙 → 高级设置
2. 入站规则 → 新建规则
3. 端口 → TCP → 特定端口 `8000`
4. 允许连接

**macOS**：
```bash
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add uvicorn
```

---

## 🌐 方案 2：内网穿透（快速公网访问）

使用 ngrok 或 frp 将本地服务暴露到公网。

### 使用 ngrok

#### 1. 安装 ngrok
下载：https://ngrok.com/download

#### 2. 启动后端
```bash
start_backend.bat
```

#### 3. 启动 ngrok
```bash
ngrok http 8000
```

会显示：
```
Forwarding  https://abcd1234.ngrok.io -> http://localhost:8000
```

#### 4. 配置前端

所有电脑的 `frontend/.env`：
```
VITE_API_BASE=https://abcd1234.ngrok.io/api
```

#### 5. 启动前端
```bash
cd frontend
npm run dev
```

现在任何电脑都可以通过 ngrok 地址访问！

### 注意事项
- ngrok 免费版地址会变化，每次重启需要更新配置
- 有速度限制
- 适合临时测试

---

## ☁️ 方案 3：云服务器部署（正式环境）

### 推荐平台
- **国内**：阿里云、腾讯云、华为云
- **国外**：AWS、Azure、DigitalOcean、Railway、Render

### 部署步骤（以 Railway 为例）

#### 1. 准备 Dockerfile（后端）

创建 `backend/Dockerfile`：
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. 部署后端

在 Railway：
1. 连接 GitHub 仓库
2. 选择 `backend` 目录
3. 自动检测 Dockerfile 并部署
4. 获得后端地址：`https://your-app.railway.app`

#### 3. 部署前端

在 Vercel/Netlify：
1. 连接 GitHub 仓库
2. 配置环境变量：
   ```
   VITE_API_BASE=https://your-app.railway.app/api
   ```
3. 自动部署

#### 4. 配置数据库

生产环境建议使用 PostgreSQL：

修改 `backend/app/database.py`：
```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nudgeeq.db")

# PostgreSQL URL format:
# postgresql://user:password@host:port/database
```

---

## 🔧 故障排查

### 问题 1：无法连接后端

**检查清单**：
- [ ] 后端是否运行在 `0.0.0.0:8000`？
- [ ] 防火墙是否开放 8000 端口？
- [ ] IP 地址是否正确？
- [ ] 是否在同一 WiFi？

**测试方法**：
```bash
# 在其他电脑上测试
curl http://192.168.1.100:8000/health

# 应返回：
# {"status":"healthy"}
```

### 问题 2：WebSocket 无法连接

**原因**：HTTP/HTTPS 协议不匹配

**解决**：
- HTTP 后端 → 使用 `ws://`
- HTTPS 后端 → 使用 `wss://`

代码已自动处理，检查浏览器控制台错误。

### 问题 3：CORS 错误

修改 `backend/app/main.py`：
```python
origins = [
    "http://localhost:5173",
    "http://192.168.1.100:5173",  # 添加其他电脑的地址
    "https://your-frontend.vercel.app",  # 云部署地址
]
```

---

## 📊 测试跨桌通信

### 完整流程

1. **电脑 A（Table 1）**：
   - 访问前端
   - 加入 Table 1
   - 设置座位、头像、信号

2. **电脑 B（Table 2）**：
   - 访问前端
   - 加入 Table 2
   - 设置座位、头像、信号

3. **发送消息（Table 1 → Table 2）**：
   - 在 Table 1 点击 "Nearby"
   - 搜索 Table 2 的成员
   - 发送消息

4. **接收消息（Table 2）**：
   - 收到弹窗通知
   - 选择回复：SORRY / IGNORE / SURE

5. **查看回执（Table 1）**：
   - 收到 Table 2 的回复

### 验证功能

- [ ] 跨设备登录不同桌子
- [ ] 实时看到对方的状态更新
- [ ] 发送消息成功
- [ ] 接收消息并回复
- [ ] 发送方收到回执

---

## 🎯 推荐配置

### 开发/测试阶段
**方案 1（局域网）**
- 优点：免费、快速、低延迟
- 适合：同一地点测试

### 演示阶段
**方案 2（内网穿透）**
- 优点：快速搭建、任何地点访问
- 适合：远程演示、用户测试

### 生产部署
**方案 3（云服务器）**
- 优点：稳定、快速、可扩展
- 适合：正式产品上线

---

## 💡 常见问题

### Q: 是否需要云服务器才能跨设备通信？
A: **不需要**！局域网方案即可实现（同一 WiFi）。

### Q: 数据会保存吗？
A: 会保存在 SQLite 数据库（`backend/nudgeeq.db`）。重启后端数据不丢失。

### Q: 支持多少桌子？
A: 代码已支持 Table 1 和 Table 2，每桌最多 4 人。可扩展更多桌子。

### Q: 是否支持手机访问？
A: 支持！使用局域网 IP 地址在手机浏览器访问即可。

---

## 📝 快速开始命令（局域网）

### 服务器电脑
```bash
# 1. 启动后端
start_backend.bat

# 2. 获取 IP
ipconfig  # 例如：192.168.1.100

# 3. 启动前端
cd frontend
npm run dev
```

### 其他电脑
```bash
# 1. 配置 API 地址
cd frontend
echo VITE_API_BASE=http://192.168.1.100:8000/api > .env

# 2. 启动前端
npm run dev
```

### 测试
- 电脑 1：Table 1 → 发送消息
- 电脑 2：Table 2 → 接收并回复 ✅

---

## 🚀 下一步

1. **立即测试**：使用局域网方案验证跨设备通信
2. **优化体验**：添加更多桌子、自定义消息模板
3. **部署上线**：选择云服务器进行正式部署

有问题随时联系！

