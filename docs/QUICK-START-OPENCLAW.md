# PlanAudit 快速开始 (OpenClaw 版)

> ⚠️ **状态：待验证** — 本文档基于 OpenClaw 官方文档编写，尚未经过实际测试验证。

**快速检测你的 CodingPlan 是否被多倍计数。**

## 原理

通过代理拦截你的 API 请求，统计实际调用次数，再与控制台显示的使用量对比，判断是否存在隐藏倍率。

```
计费倍率 = 控制台使用量增量 / 代理记录的请求数
```

## 准备工作

### 1. 安装 OpenClaw

```bash
npm install -g openclaw@latest
```

验证安装：

```bash
openclaw --version
```

### 2. 初始化 OpenClaw

```bash
openclaw setup
```

### 3. 安装 llm-proxy

```bash
git clone https://github.com/gabrielslls/llm-proxy.git
cd llm-proxy
npm install
```

## OpenClaw 配置文件

| 项目 | 路径 |
|------|------|
| 配置目录 | `$HOME/.openclaw/` |
| 配置文件 | `$HOME/.openclaw/openclaw.json` |
| 会话目录 | `$HOME/.openclaw/agents/main/sessions/` |

## 测试步骤

### 1. 记录控制台初始值

打开你的 CodingPlan 控制台，记录当前使用量：`_______`

### 2. 启动代理

```bash
cd llm-proxy
npm start -- --target <你的API地址> --plan
```

> `<你的API地址>` 从 OpenClaw 配置文件中获取，查看 `baseUrl` 字段

### 3. 修改 OpenClaw 配置

编辑 `$HOME/.openclaw/openclaw.json`，将 `baseUrl` 改为代理地址：

```json
{
  "models": {
    "providers": {
      "your-provider": {
        "baseUrl": "http://localhost:3000/v1",
        "apiKey": "${YOUR_API_KEY}",
        "api": "openai-completions",
        "models": [
          { "id": "your-model", "name": "Your Model" }
        ]
      }
    }
  }
}
```

### 4. 启动 OpenClaw Gateway

```bash
openclaw gateway
```

### 5. 发起若干次对话

在 OpenClaw 中进行几次对话，记住你发起的次数：`_______`

> ⚠️ **重要**：务必等待客户端**完全停止输出**后再进行下一步，确保流式响应被完整计数。

### 6. 查看代理日志

```bash
wc -l logs/requests.log
```

记录代理统计的请求数：`_______`

### 7. 等待后查看控制台

等待 5-10 分钟后，再次查看控制台使用量：`_______`

### 8. 计算倍率

```
控制台增量 = 步骤7 - 步骤1 = _______
代理请求数 = 步骤6 = _______
计费倍率 = 控制台增量 / 代理请求数 = _______
```

## 结果判断

| 倍率范围 | 判断 | 说明 |
|----------|------|------|
| ≈ 1.0 | ✅ 正常 | 计费透明 |
| 1.0 - 1.2 | ⚠️ 可能存在技术性偏差 | 网络重试、心跳等可能导致轻微偏差 |
| > 1.2 | 🚨 可疑 | 建议深入调查，可能存在隐藏倍率 |

## 注意事项

- 控制台数据可能有 5-30 分钟延迟，请耐心等待
- 流式响应（Streaming）可能导致技术性偏差
- 建议多次测试取平均值
- 测试期间确保所有模型指向同一代理后端

## OpenClaw 常用命令

| 命令 | 说明 |
|------|------|
| `openclaw setup` | 初始化配置 |
| `openclaw gateway` | 启动 Gateway |
| `openclaw models list` | 查看可用模型 |
| `openclaw models status` | 查看模型状态 |
| `openclaw sessions` | 查看会话列表 |

---

*本项目为公益活动"你的 CodingPlan 被几倍计数了"的一部分*

*如需严谨取证，请查看 [OpenClaw 取证指南](AUDIT-GUIDE-OPENCLAW.md)*
