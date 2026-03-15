# 🔧 GitHub Pages 修复说明

## 问题描述

1. **GitHub Pages 无法访问** - 显示网站无法打开
2. **README badges 显示错误** - Version badge 显示 "no releases or repo not found"

---

## 已修复的问题

### 1. GitHub Pages 部署配置

**问题原因**: GitHub Actions 工作流配置部署 `frontend/dist` 目录，但该目录的文件不是最新的。

**修复方案**:
- ✅ 更新 `.github/workflows/deploy.yml`，在部署前自动复制最新 HTML 文件到 `frontend/dist`
- ✅ 手动同步了 `frontend/dist` 目录的文件
- ✅ 推送代码触发自动部署

**部署流程**:
```
推送代码 → GitHub Actions 触发 → 复制 HTML 文件 → 上传到 Pages → 自动部署
```

### 2. README Version Badge

**问题原因**: Badge URL 使用的是 `/releases`，当没有 release 时会显示错误。

**修复方案**:
- ✅ 将 badge URL 从 `/releases` 改为 `/releases/latest`
- ✅ 这样即使没有创建 release，也会显示最新版本号

**修改前**:
```markdown
[![Version](https://img.shields.io/github/v/release/zhewenzhang/a-share-dashboard?label=Version&color=6366f1)](https://github.com/zhewenzhang/a-share-dashboard/releases)
```

**修改后**:
```markdown
[![Version](https://img.shields.io/github/v/release/zhewenzhang/a-share-dashboard?label=Version&color=6366f1)](https://github.com/zhewenzhang/a-share-dashboard/releases/latest)
```

---

## 如何验证修复

### 1. 检查 GitHub Pages 状态

访问：https://github.com/zhewenzhang/a-share-dashboard/actions

查看最新的 "Deploy to GitHub Pages" 工作流是否成功。

### 2. 访问 GitHub Pages

等待 2-5 分钟（GitHub Pages 需要时间部署），然后访问：

👉 **https://zhewenzhang.github.io/a-share-dashboard/**

如果仍然无法访问，尝试：
- 清除浏览器缓存
- 使用无痕模式打开
- 检查 GitHub Pages 是否启用

### 3. 检查 GitHub Pages 设置

在 GitHub 仓库页面：
1. 点击 **Settings** → **Pages**
2. 确认 **Source** 设置为 **GitHub Actions**
3. 确认 URL 显示为：`https://zhewenzhang.github.io/a-share-dashboard/`

---

## 手动部署（可选）

如果自动部署失败，可以手动部署：

### 方法 1：触发 GitHub Actions

1. 访问 https://github.com/zhewenzhang/a-share-dashboard/actions
2. 点击左侧 "Deploy to GitHub Pages"
3. 点击 "Run workflow" 按钮
4. 选择 main 分支
5. 点击 "Run workflow"

### 方法 2：使用 GitHub CLI

```bash
# 安装 GitHub CLI (如果未安装)
brew install gh

# 触发工作流
gh workflow run deploy.yml
```

---

## 常见问题

### Q: GitHub Pages 仍然显示旧版本
**A**: 
- 清除浏览器缓存 (Cmd+Shift+R 强制刷新)
- 等待 5-10 分钟，GitHub Pages 需要时间更新
- 检查 Actions 中部署是否成功

### Q: Version badge 仍然显示错误
**A**: 
- README 已缓存，等待几分钟刷新
- 或者创建一个新的 release：
  ```bash
  git tag v3.0.5
  git push origin v3.0.5
  ```

### Q: 自定义域名问题
**A**: 
- 如果使用自定义域名，确保 DNS 配置正确
- 检查 CNAME 文件是否存在

---

## 文件结构说明

```
a-share-dashboard/
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Pages 部署工作流
├── frontend/
│   └── dist/                   # 部署到 GitHub Pages 的文件
│       ├── index.html          # 主页面（数据看板）
│       ├── portfolio.html      # 投资组合页面
│       ├── backtest.html       # 策略回测页面
│       └── simulate.html       # 模拟交易页面
├── index.html                  # 源文件（自动复制到 frontend/dist）
├── portfolio.html              # 源文件
├── backtest.html               # 源文件
└── simulate.html               # 源文件
```

---

## 联系支持

如果问题持续，请：
1. 检查 GitHub Actions 日志
2. 查看 GitHub Pages 设置
3. 提交 Issue: https://github.com/zhewenzhang/a-share-dashboard/issues

---

**最后更新**: 2026-03-15  
**版本**: v3.0.5
