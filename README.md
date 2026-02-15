# A股市场看板

每日投资检讨工具 - A股市场实时监控

## 访问地址

**GitHub Pages**: https://zhewenzhang.github.io/a-share-dashboard/

## 功能特性

- 📊 三大指数实时行情（上证/深证/创业板/沪深300）
- 📈 涨跌统计（上涨/下跌/平盘家数）
- 🔥 板块涨幅榜 TOP10
- 💰 资金流向（北向/南向/主力）
- ⭐ 重要股票监控列表

## 部署方式

### 方式一：GitHub Pages（推荐）
1. 创建GitHub仓库：`a-share-dashboard`
2. 上传 `index.html`
3. Settings → Pages → Main branch → Save
4. 访问：`https://你的用户名.github.io/a-share-dashboard/`

### 方式二：本地预览
```bash
cd a-share-dashboard
python3 -m http.server 8080
# 访问 http://localhost:8080
```

## 数据来源

- **生产环境**：TuShare API（需要配置token）
- **演示环境**：模拟数据（展示用）

## 配置TuShare API

在代码中替换 `generateMockData()` 函数为真实的TuShare API调用：

```javascript
async function fetchRealData() {
    const response = await fetch('https://api.tushare.pro', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            api_name: 'daily',
            token: '你的TUshare_TOKEN'
        })
    });
    return response.json();
}
```

## 刷新频率

- 手动点击"刷新"按钮
- 可配置自动刷新（每5分钟）

## 技术栈

- HTML5 + CSS3
- JavaScript (原生)
- ECharts 图表库
- 响应式设计

---

**作者**: 可乐 🤖
**版本**: 1.0.0
**更新**: 2026-02-16
