# 🧰 免费大模型额度导航（Free LLM Quota Hub）

集全网（国内 + 海外）送免费 Token 的大模型平台、限时免费资源于一体的静态查询网站。

在线地址：https://f1re-03.github.io/free-llm-hub/

## 功能

- 🔍 **实时搜索**：按平台名 / 英文名 / 支持模型（如 DeepSeek、Gemini、千帆）模糊搜索
- 🏷️ **分类筛选**：
  - 地区：国内直连 / 海外需外网
  - 类型：注册赠金 / 永久免费层 / 限时免费
  - 标签：是否需信用卡、是否需科学上网
- 📊 **排序**：按额度大小 / 名称
- 📱 **移动端适配**：360px 起的手机上单列展示，筛选栏与按钮在窄屏横向滑动，实时模型区限高滚动，计算器改为竖排结果

## 使用

直接用浏览器打开 `index.html` 即可，无需任何后端或构建步骤。

## 部署（可选）

纯静态页面，任选其一：

```bash
# GitHub Pages：把仓库推上去，Settings → Pages → Source 选 "Deploy from a branch" → main / (root)

# Vercel
vercel deploy free-llm-hub

# Cloudflare Pages
# 控制台上传目录，或 wrangler pages deploy free-llm-hub
```

## 更新数据

编辑 `data.js` 中的 `items` 数组即可，字段说明：

注意：`data.js` 由 `scripts/update_data.py` 从 `data_base.json` 生成，直接改 `data.js` 会在下次更新时被覆盖。要长期维护，请改 `data_base.json`。

| 字段 | 说明 |
|---|---|
| `name` / `nameEn` | 平台中文 / 英文名 |
| `url` | 注册或领额度页面 |
| `region` | `cn`（国内直连）或 `global`（需外网） |
| `type` | `credit` 注册赠金 / `free_tier` 永久免费层 / `limited` 限时免费 |
| `quota` | 免费额度描述（含"万"字会被用于额度排序） |
| `validity` | 有效期 / 重置规则 |
| `creditCard` | 是否需要信用卡 |
| `vpn` | 是否需要科学上网 |
| `models` | 支持的主要模型系列 |
| `notes` | 补充说明 |
| `category` | 分类标签（聚合平台 / 官方 API / 推理加速等） |

### 自动更新范围

`.github/workflows/daily-update.yml` 每天 UTC 01:00（北京时间 09:00）运行一次，做两件事：

1. 从 OpenRouter 公开接口拉取当前价格为 0 的模型，写入 `data.js` 的 `live.openrouterFreeModels`；
2. 提交并推送变更。

各平台的额度、有效期等字段不会自动抓取（没有统一接口且页面结构经常变），属于人工核对快照，页面上的「快照时间」即为该快照的生成时间。修改额度请编辑 `data_base.json`。

## ⚠️ 免责声明

各平台免费政策变动频繁，数据采集自公开资料，仅供查询参考，实际额度请以各官网为准。

推荐链接的范围、各平台奖励规则与合规红线见 [monetization.md](monetization.md)。
