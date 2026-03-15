# 🧪 UI 更新测试与缓存清除指南

## ⚠️ 为什么看不到更新？

GitHub Pages 已成功部署最新版本，但你的浏览器可能缓存了旧版本文件。

---

## ✅ 本地测试（立即看到更新）

### 方法 1: 本地 HTTP 服务器（推荐）

已经在运行！访问：

**http://localhost:8080**

如果服务器未运行，执行：
```bash
cd /Users/dave/a-share-dashboard
python3 -m http.server 8080
```

### 方法 2: 直接打开文件

```bash
open /Users/dave/a-share-dashboard/index.html
```

---

## 🌐 GitHub Pages 测试

### 强制刷新方法

#### Mac
```
Cmd + Shift + R
```

#### Windows
```
Ctrl + Shift + R
```

#### 带版本号访问
```
https://zhewenzhang.github.io/a-share-dashboard/?v=20260315
```

### 清除浏览器缓存

#### Chrome/Safari
1. 打开开发者工具 (F12)
2. 右键刷新按钮 → "清空缓存并硬性重新加载"

#### 或使用无痕模式
```
Cmd + Shift + N (Mac)
Ctrl + Shift + N (Windows)
```

---

## 🧪 UI 测试页面

已创建测试页面，访问查看是否加载最新版本：

### 本地测试
```
http://localhost:8080/test-ui.html
```

### GitHub Pages
```
https://zhewenzhang.github.io/a-share-dashboard/test-ui.html
```

测试页面会显示：
- ✅ 当前文件版本（最新/缓存）
- 🎨 颜色对比（新红 #ff4d4f vs 旧红 #ef4444）
- 📐 字体检测（是否使用 Noto Sans SC）
- 🔘 按钮交互测试

---

## 🔍 如何确认已更新

### 检查点 1: 涨跌颜色

**新版本（优化后）:**
- 涨：`#ff4d4f` - 更鲜艳的红色
- 跌：`#00c853` - 更暖的绿色

**旧版本（优化前）:**
- 涨：`#ef4444`
- 跌：`#10b981`

### 检查点 2: 字体

打开浏览器控制台 (F12)，运行：
```javascript
getComputedStyle(document.body).fontFamily
```

**新版本应显示:**
```
"Inter", "Noto Sans SC", ...
```

**旧版本显示:**
```
"Plus Jakarta Sans", ...
```

### 检查点 3: 按钮悬停

悬停在"刷新"按钮上：

**新版本:**
- 按钮上移 1px
- 蓝色光晕阴影

**旧版本:**
- 仅阴影变化

---

## 📊 GitHub Pages 部署状态

✅ **部署成功**

- 最新提交：`7684b8d` (docs: 添加 UI 设计优化报告)
- 部署时间：2026-03-15 13:48:39 GMT
- 工作流：Deploy to GitHub Pages #21
- 状态：成功

---

## 🚀 推荐测试流程

1. **先测试本地** → http://localhost:8080
2. **确认 UI 变化** → 查看颜色/字体/交互
3. **清除浏览器缓存** → Cmd+Shift+R
4. **访问 GitHub Pages** → 带版本号 `?v=20260315`
5. **使用测试页面** → 自动检测版本

---

## 📝 技术细节

### 缓存头信息
```
HTTP/2 200
content-type: text/html; charset=utf-8
last-modified: Sun, 15 Mar 2026 13:48:39 GMT
cache-control: max-age=600
etag: "69b6b8b7-d473"
x-github-request-id: 454C:20F41A:6ABE5B:6EE577:69B6BA1E
```

缓存有效期：600 秒（10 分钟）

### 强制刷新原理
- `Cmd+Shift+R` 发送 `Cache-Control: no-cache` 头
- 带版本号参数 (`?v=xxx`) 创建新缓存键
- 无痕模式不使用现有缓存

---

## ❓ 仍然看不到更新？

### 检查清单

- [ ] 本地测试是否正常显示？
- [ ] 是否尝试过 Cmd+Shift+R？
- [ ] 是否使用无痕模式测试？
- [ ] 是否等待超过 10 分钟？
- [ ] 测试页面是否显示最新版本？

### 联系支持

如果以上步骤都失败，请：
1. 截图测试页面结果
2. 提供浏览器版本信息
3. 提交 Issue: https://github.com/zhewenzhang/a-share-dashboard/issues

---

**创建时间**: 2026-03-15  
**版本**: v3.0.5  
**部署状态**: ✅ 成功
