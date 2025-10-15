# 第二台电脑快速配置（无需 Git）

## 📋 准备工作

只需要：
- ✅ 已安装 Node.js
- ✅ 连接同一 WiFi

**不需要 Git！**

---

## 🚀 三步配置法

### 第 1 步：获取代码

选择以下任一方式：

#### 方式 A：从 GitHub 下载 ZIP

1. **访问项目地址**：
   ```
   https://github.com/heiloMeow/Happy-Graduation/tree/Yueteng_Ma
   ```

2. **下载代码**：
   - 点击页面右上角绿色的 `Code` 按钮
   - 选择 `Download ZIP`
   - 保存到桌面或任意位置

3. **解压文件**：
   - 右键点击下载的 ZIP 文件
   - 选择 "解压到当前文件夹" 或 "提取全部"
   - 得到 `Happy-Graduation-Yueteng_Ma` 文件夹

#### 方式 B：从主电脑复制

如果两台电脑在一起：
1. 在主电脑上，右键项目文件夹 → 压缩
2. 通过 U 盘或共享文件夹复制到第二台电脑
3. 解压

---

### 第 2 步：运行配置脚本

1. **进入项目文件夹**：
   ```
   双击进入解压后的文件夹
   你应该看到：frontend、backend、setup_client_no_git.bat 等文件
   ```

2. **运行配置脚本**：
   ```
   双击运行：setup_client_no_git.bat
   ```

3. **输入主电脑 IP**：
   ```
   例如：192.168.1.100
   ```

脚本会自动完成所有配置！

---

### 第 3 步：访问应用

浏览器会自动打开，访问：
```
http://localhost:5173
```

完成！🎉

---

## 🔧 手动配置（如果脚本失败）

如果自动脚本有问题，手动执行：

```powershell
# 1. 打开 PowerShell，进入项目目录
cd 解压后的文件夹路径

# 2. 进入前端目录
cd frontend

# 3. 安装依赖
npm install

# 4. 创建配置文件（替换 IP）
"VITE_API_BASE=http://192.168.1.100:8000/api" | Out-File -Encoding ASCII .env

# 5. 启动前端
npm run dev

# 6. 打开浏览器
# 访问 http://localhost:5173
```

---

## 📝 获取主电脑 IP 地址

**在主电脑上执行**：

### Windows:
```bash
ipconfig
```
查找 "IPv4 地址"，例如：`192.168.1.100`

### 或者运行主电脑的启动脚本时会自动显示

---

## ✅ 验证配置

### 检查文件是否正确

1. **确认 .env 文件存在**：
   ```
   路径：Happy-Graduation\frontend\.env
   内容：VITE_API_BASE=http://192.168.1.100:8000/api
   ```

2. **测试连接**：
   打开浏览器访问：
   ```
   http://192.168.1.100:8000/health
   ```
   应该显示：`{"status":"healthy"}`

---

## 💡 完整示例

假设主电脑 IP 是 `192.168.1.100`：

### 在第二台电脑上：

```powershell
# 1. 下载并解压代码到桌面
# 2. 打开 PowerShell

cd C:\Users\你的用户名\Desktop\Happy-Graduation-Yueteng_Ma

# 3. 进入前端目录
cd frontend

# 4. 检查 Node.js
node --version
# 应显示版本号，如：v18.17.0

# 5. 安装依赖
npm install

# 6. 创建配置
"VITE_API_BASE=http://192.168.1.100:8000/api" | Out-File -Encoding ASCII .env

# 7. 检查配置
cat .env
# 应显示：VITE_API_BASE=http://192.168.1.100:8000/api

# 8. 启动
npm run dev

# 9. 访问
# 打开浏览器访问 http://localhost:5173
```

---

## ⚠️ 常见问题

### 问题 1：npm 命令不存在

**错误**：`npm : 无法将"npm"项识别为 cmdlet 的名称`

**解决**：
1. 安装 Node.js：https://nodejs.org/
2. 下载 LTS 版本（推荐）
3. 安装时确保勾选 "Add to PATH"
4. 重启 PowerShell
5. 验证：`node --version`

### 问题 2：.env 文件创建失败

**手动创建**：
1. 打开记事本
2. 输入：`VITE_API_BASE=http://192.168.1.100:8000/api`
3. 保存为：`frontend\.env`
4. 确保文件名是 `.env`，不是 `.env.txt`

**显示文件扩展名**：
- 文件资源管理器 → 查看 → 勾选 "文件扩展名"

### 问题 3：端口被占用

**错误**：`Port 5173 is already in use`

**解决**：
```bash
# 指定其他端口
npm run dev -- --port 5174
```

### 问题 4：无法连接服务器

**检查清单**：
- [ ] 主电脑的后端正在运行？
- [ ] IP 地址是否正确？
- [ ] 两台电脑在同一 WiFi？
- [ ] 主电脑防火墙是否允许？

**测试连接**：
```bash
# 在浏览器访问
http://192.168.1.100:8000/health

# 应该显示
{"status":"healthy"}
```

---

## 📊 配置清单

完成后检查：

- [ ] 代码已下载并解压
- [ ] Node.js 已安装（`node --version` 有效）
- [ ] 前端依赖已安装（`frontend/node_modules` 存在）
- [ ] `.env` 文件已创建且内容正确
- [ ] `npm run dev` 成功运行
- [ ] 浏览器可以访问 `http://localhost:5173`
- [ ] 可以登录并加入桌子
- [ ] 在 Nearby 页面能看到其他桌子

---

## 🎯 快速命令卡片

```powershell
# 完整流程（复制粘贴执行）
cd 项目文件夹路径
cd frontend
npm install
"VITE_API_BASE=http://主电脑IP:8000/api" | Out-File -Encoding ASCII .env
npm run dev
```

替换 `项目文件夹路径` 和 `主电脑IP`，然后一次性执行！

---

## 📸 截图说明

### 从 GitHub 下载 ZIP：

1. 访问项目页面
2. 确保分支选择器显示 `Yueteng_Ma`
3. 点击绿色 `Code` 按钮
4. 点击 `Download ZIP`

### 解压后的文件结构：

```
Happy-Graduation-Yueteng_Ma/
├── frontend/           ← 我们需要的
├── backend/            ← 不需要配置
├── setup_client_no_git.bat  ← 运行这个
├── README.md
└── ...
```

---

## 💪 成功标志

配置成功的标志：
- ✅ 前端正常启动
- ✅ 可以看到登录页面
- ✅ 可以选择座位
- ✅ 可以看到其他桌子的成员
- ✅ 可以发送和接收消息

全部完成 = 配置成功！🎉

---

## 🔗 相关文档

- 详细配置：`第二台电脑配置指南.md`
- 跨设备通信：`快速开始-跨设备通信.md`
- 完整说明：`CROSS_DEVICE_SETUP.md`

有问题随时参考这些文档！

