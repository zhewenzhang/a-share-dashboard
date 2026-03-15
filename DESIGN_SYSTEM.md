# 🎨 A 股资金追踪系统 - 设计系统文档

## 设计理念

**专业金融终端 × 现代数据可视化**

融合彭博终端的专业性和现代 SaaS 应用的优雅体验，打造沉浸式金融数据分析界面。

---

## 🎯 设计原则

### 1. 数据优先 (Data-First)
- 信息层次清晰，关键数据突出显示
- 减少视觉干扰，让数据成为主角
- 使用等宽字体展示数值，确保精确对齐

### 2. 专业克制 (Professional Restraint)
- 避免过度装饰和动画
- 色彩使用克制，仅用于强调关键信息
- 统一的视觉语言建立信任感

### 3. 高效交互 (Efficient Interaction)
- 减少点击次数，关键操作触手可及
- 即时反馈，无延迟感
- 支持键盘快捷键

### 4. 暗色优先 (Dark-First)
- 专为长时间使用优化
- 降低蓝光，减少视觉疲劳
- 高对比度确保可读性

---

## 🎨 色彩系统

### 主色调

```css
/* 背景色系 */
--bg-primary: #020617;      /* 主背景 - 深蓝黑 */
--bg-secondary: #0f172a;    /* 侧边栏背景 */
--bg-card: #1e293b;         /* 卡片背景 */
--bg-elevated: #334155;     /* 悬浮元素 */

/* 边框和分隔 */
--border-subtle: rgba(148, 163, 184, 0.08);
--border-default: rgba(148, 163, 184, 0.15);
--border-strong: rgba(148, 163, 184, 0.25);

/* 文本色系 */
--text-primary: #f8fafc;    /* 主要文字 */
--text-secondary: #94a3b8;  /* 次要文字 */
--text-muted: #64748b;      /* 弱化文字 */
--text-inverse: #0f172a;    /* 反色文字 */
```

### 功能色

```css
/* 涨跌颜色 - 符合中国股市习惯 */
--bull: #ef4444;            /* 涨 - 红色 */
--bull-bg: rgba(239, 68, 68, 0.1);
--bull-border: rgba(239, 68, 68, 0.3);

--bear: #10b981;            /* 跌 - 绿色 */
--bear-bg: rgba(16, 185, 129, 0.1);
--bear-border: rgba(16, 185, 129, 0.3);

/* 状态色 */
--accent: #3b82f6;          /* 主强调色 - 蓝色 */
--accent-hover: #2563eb;
--accent-bg: rgba(59, 130, 246, 0.1);

--warning: #f59e0b;         /* 警告 - 橙色 */
--warning-bg: rgba(245, 158, 11, 0.1);

--danger: #ef4444;          /* 危险 - 红色 */
--danger-bg: rgba(239, 68, 68, 0.1);

--success: #10b981;         /* 成功 - 绿色 */
--success-bg: rgba(16, 185, 129, 0.1);
```

### 渐变色

```css
/* 品牌渐变 */
--gradient-primary: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
--gradient-bull: linear-gradient(135deg, #ef4444 0%, #f97316 100%);
--gradient-bear: linear-gradient(135deg, #10b981 0%, #059669 100%);

/* 背景装饰渐变 */
--gradient-glow: radial-gradient(ellipse at 30% 20%, rgba(59, 130, 246, 0.08) 0%, transparent 60%);
```

---

## 📐 间距系统

基于 4px 网格系统：

```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;
```

---

## 🔤 字体系统

### 字体栈

```css
/* 主字体 - 现代无衬线 */
--font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

/* 等宽字体 - 数据展示 */
--font-mono: 'JetBrains Mono', 'Fira Code', 'SF Mono', Consolas, monospace;
```

### 字号阶梯

```css
--text-xs: 11px;    /* 辅助文字 */
--text-sm: 12px;    /* 次要文字 */
--text-base: 13px;  /* 正文 */
--text-lg: 14px;    /* 小标题 */
--text-xl: 16px;    /* 卡片标题 */
--text-2xl: 18px;   /* 页面副标题 */
--text-3xl: 24px;   /* 页面标题 */
--text-4xl: 32px;   /* 大数字展示 */
```

### 字重

```css
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

---

## 🔲 圆角系统

```css
--radius-sm: 4px;   /* 小元素 */
--radius-md: 6px;   /* 按钮、输入框 */
--radius-lg: 8px;   /* 卡片 */
--radius-xl: 12px;  /* 大卡片、弹窗 */
--radius-full: 9999px; /* 圆形 */
```

---

## 🌑 阴影系统

```css
/* 层级阴影 */
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
--shadow-md: 0 4px 8px rgba(0, 0, 0, 0.4);
--shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.5);
--shadow-xl: 0 12px 32px rgba(0, 0, 0, 0.6);

/* 特殊阴影 */
--shadow-glow: 0 0 24px rgba(59, 130, 246, 0.3);
--shadow-bull: 0 0 16px rgba(239, 68, 68, 0.3);
--shadow-bear: 0 0 16px rgba(16, 185, 129, 0.3);
```

---

## 🎬 动效系统

### 过渡时间

```css
--duration-fast: 150ms;
--duration-normal: 200ms;
--duration-slow: 300ms;
--duration-slower: 500ms;
```

### 缓动函数

```css
--ease-out: cubic-bezier(0.215, 0.61, 0.355, 1);
--ease-in-out: cubic-bezier(0.645, 0.045, 0.355, 1);
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### 动效原则

1. **克制使用** - 仅在有意义的交互时使用
2. **性能优先** - 使用 transform 和 opacity
3. **一致性** - 相同类型的交互使用相同的动效

---

## 🧩 组件规范

### 卡片 (Card)

```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  transition: all var(--duration-normal) var(--ease-out);
}

.card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-md);
}
```

### 按钮 (Button)

```css
/* 主按钮 */
.btn-primary {
  background: var(--gradient-primary);
  color: white;
  padding: 10px 18px;
  border-radius: var(--radius-md);
  font-weight: var(--font-semibold);
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-glow);
}

/* 次级按钮 */
.btn-secondary {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  color: var(--text-primary);
}

/* 幽灵按钮 */
.btn-ghost {
  background: transparent;
  border: 1px solid var(--border-default);
  color: var(--text-secondary);
}
```

### 数据表格 (Data Table)

```css
.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--border-default);
}

.data-table td {
  padding: var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
}

.data-table tbody tr:hover {
  background: var(--bg-elevated);
}
```

### 数值展示 (Stat Value)

```css
.stat-value {
  font-family: var(--font-mono);
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  letter-spacing: -0.02em;
}

.stat-change.bull {
  color: var(--bull);
}

.stat-change.bear {
  color: var(--bear);
}
```

---

## ♿ 无障碍规范

### 对比度要求

- 正常文字：至少 4.5:1
- 大文字：至少 3:1
- UI 组件：至少 3:1

### 键盘导航

- 所有交互元素可 Tab 到达
- 焦点状态清晰可见
- 支持 Escape 关闭弹窗

### 焦点样式

```css
:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}
```

---

## 📱 响应式断点

```css
/* 移动端 */
@media (max-width: 640px) { }

/* 平板 */
@media (min-width: 641px) and (max-width: 1024px) { }

/* 桌面 */
@media (min-width: 1025px) { }

/* 大桌面 */
@media (min-width: 1440px) { }
```

---

## 🎯 关键体验指标

### 性能目标

- 首屏加载 < 2s
- 交互响应 < 100ms
- 动画帧率 > 60fps

### 视觉目标

- 信息密度适中，避免拥挤
- 关键数据 3 秒内可找到
- 减少眼动距离

---

## 📋 检查清单

### 发布前检查

- [ ] 色彩对比度符合 WCAG AA
- [ ] 所有交互元素有焦点状态
- [ ] 动效时间符合规范
- [ ] 响应式布局测试通过
- [ ] 深色模式一致性检查

### 设计审查

- [ ] 符合金融终端专业感
- [ ] 数据展示清晰易读
- [ ] 交互符合用户预期
- [ ] 视觉层次清晰

---

<div align="center">

**设计系统版本**: v1.0  
**最后更新**: 2026-03-15

</div>
