# PlanAudit 取证指南 (OpenClaw 版)

> ⚠️ **状态：待验证** — 本文档基于 OpenClaw 官方文档编写，尚未经过实际测试验证。

> CodingPlan 计费透明度验证（取证版）

本方案旨在通过**中间人代理（MITM）捕获**与**本地会话对比**的双重校验机制，透明化远程 LLM 服务的计费行为，揭露可能存在的隐藏计费倍率问题。

- **核心逻辑**：利用 `llm-proxy` 拦截 OpenClaw 发出的所有 API 请求并记录日志，同时在测试前后对本地会话目录进行快照与统计。
- **校验维度**：
  1. **请求一致性**：验证本地记录的对话次数与代理拦截到的实际出站请求数是否 1:1 匹配。
  2. **存活与计数验证**：确保配置文件中的所有模型均真实可用，且每一个调用都能触发计费反馈。
  3. **计费透明度**：比对测试前后的控制台余额/使用量变动，推算是否存在隐藏的"单次调用最小倍率"或非预期的额外扣费。
- **取证强度**：全流程引入 `SHA256` 哈希校验，确保从配置文件到会话记录的每一个环节都具备不可篡改性，为公益维权提供数据底座。

## 适用范围

本方案适用于任何提供 LLM CodingPlan 服务的服务商。

## OpenClaw 客户端信息

| 项目 | 路径 |
|------|------|
| 配置目录 | `$HOME/.openclaw/` |
| 配置文件 | `$HOME/.openclaw/openclaw.json` |
| 会话目录 | `$HOME/.openclaw/agents/main/sessions/` |
| 日志目录 | `$HOME/.openclaw/logs/` |

---

## 测试工具

| 工具 | 版本 | 说明 |
|------|------|------|
| OpenClaw | 2026.3.31+ | AI Coding 客户端 |
| OBS Studio | 30.0.2.1 | 屏幕录制，用于取证 |
| llm-proxy | latest | 代理拦截 API 请求 |

**辅助工具：**
- https://github.com/gabrielslls/llm-proxy.git — 转发 OpenClaw 对云服务的请求，用以获取实际调用的请求次数

## 目录与文件

| 路径 | 说明 |
|------|------|
| `$HOME/.openclaw/openclaw.json` | OpenClaw 配置文件 |
| `$HOME/.openclaw/agents/main/sessions/` | OpenClaw 会话目录 |
| `<PROJECT_ROOT>/llm-proxy/logs` | 转发 API 请求日志目录 |
| `<PROJECT_ROOT>/evidence` | 固定证据目录 |
| `docs/TEST-CASE.md` | 测试任务 |

## 终端准备

开启四个终端：

1. 打开本文件
2. 运行 OpenClaw Gateway
3. 运行 `llm-proxy`
4. `tail -f llm-proxy/logs/requests.log`

---

## 测试步骤

### 0. 准备

**重要提示：**
- ⚠️ **多模型混用风险**：测试期间，请确保所有模型均指向**同一代理后端**，否则会导致统计污染。
- ⚠️ **屏幕录制**：启动 OBS 录屏，范围需覆盖终端窗口与浏览器控制台页面，这对于证据链至关重要。

```bash
echo "检查 OpenClaw 配置的目标服务"
date
mkdir -p ./evidence
date > ./evidence/sha256sum.lst

# 检查 OpenClaw 配置
cat $HOME/.openclaw/openclaw.json

# 停止 OpenClaw Gateway
pkill -f "openclaw gateway" || true
ps -ef | grep openclaw

# 对配置文件进行哈希校验
sha256sum $HOME/.openclaw/openclaw.json | tee -a ./evidence/sha256sum.lst
```

### 1. 清空 OpenClaw 会话目录

```bash
rm -rf $HOME/.openclaw/agents/main/sessions/*
ls -la $HOME/.openclaw/agents/main/sessions/
```

### 2. 确认会话目录已清空

```bash
echo "=== sessions directory ==="
ls -la $HOME/.openclaw/agents/main/sessions/
echo "=== session count ==="
ls $HOME/.openclaw/agents/main/sessions/ | wc -l
```

### 3. 控制台：配置 API_KEY

- 停用以前全部 API_KEY
- 启用一个新 API_KEY
- 在终端中执行（替换为你的 API_KEY）：

```bash
export API_KEY=<your_api_key>
env | grep API_KEY
```

> ⚠️ **安全提醒**：录屏或分享日志时，请注意遮蔽 API_KEY，防止密钥泄露。

### 4. 控制台：确认当前周期使用量

打开目标服务的 CodingPlan 控制台页面，记录当前周期的使用量/余额。

### 5. 在新终端监控请求记录

```bash
rm -fr ./llm-proxy/logs/*
ls -l ./llm-proxy/logs/
touch ./llm-proxy/logs/requests.log
tail -f ./llm-proxy/logs/requests.log
```

### 6. 在新终端启动代理

```bash
cd llm-proxy
# 替换 <TARGET_URL> 为目标服务的 API 地址（从 OpenClaw 配置文件的 baseUrl 字段获取）
npm start -- --target <TARGET_URL> --plan
```

**参数说明：**
- `--target`：目标服务的 LLM API 端点地址
- `--plan`：启用计费计数模式

### 7. 修改 OpenClaw 配置指向代理

编辑 `$HOME/.openclaw/openclaw.json`，将 `baseUrl` 改为代理地址：

```json
{
  "models": {
    "providers": {
      "your-provider": {
        "baseUrl": "http://localhost:3000/v1",
        "apiKey": "${API_KEY}",
        "api": "openai-completions",
        "models": [
          { "id": "your-model", "name": "Your Model" }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "your-provider/your-model"
      }
    }
  }
}
```

### 8. 启动 OpenClaw Gateway

```bash
openclaw gateway
```

### 9. 开启一个会话，粘贴需求 `docs/TEST-CASE.md`

在 OpenClaw 中进行对话测试。

### 10. OpenClaw 运行状态

```bash
ps -ef | grep openclaw
```

### 11. 停止 OpenClaw Gateway

> ⚠️ **重要**：正确的停止流程对于计费测试至关重要。

**OpenClaw 停止方式：**

| 方式 | 说明 |
|------|------|
| `Ctrl+C` | 停止 Gateway |
| `openclaw gateway stop` | 通过命令停止服务 |

```bash
# 确认 OpenClaw 进程已停止
ps -ef | grep openclaw
```

### 12. 统计 OpenClaw 会话数

```bash
echo "=== sessions directory ==="
ls -la $HOME/.openclaw/agents/main/sessions/

echo "=== session count ==="
ls $HOME/.openclaw/agents/main/sessions/ | wc -l

# 对会话目录进行哈希校验
find $HOME/.openclaw/agents/main/sessions/ -type f -exec sha256sum {} \; | tee -a ./evidence/sha256sum.lst
```

### 13. 从代理日志统计 API 访问量

```bash
sha256sum ./llm-proxy/logs/calls.jsonl | tee -a ./evidence/sha256sum.lst
sha256sum ./llm-proxy/logs/requests.log | tee -a ./evidence/sha256sum.lst
wc -l ./llm-proxy/logs/requests.log
```

### 14. 保留证据

```bash
cp -p ./llm-proxy/logs/calls.jsonl ./evidence
cp -p ./llm-proxy/logs/requests.log ./evidence
cp -p $HOME/.openclaw/openclaw.json ./evidence
cp -r $HOME/.openclaw/agents/main/sessions ./evidence/openclaw-sessions

ls -la ./evidence
```

### 15. 查看控制台

打开目标服务的控制台，查看 CodingPlan 使用情况。对比：
- 代理日志记录的请求次数
- OpenClaw 会话目录中的会话数
- 控制台显示的使用量

**关键问题**：是否存在 `控制台使用量 / 实际请求数 > 1` 的情况？

---

## OpenClaw 常用命令

| 命令 | 说明 |
|------|------|
| `openclaw setup` | 初始化配置 |
| `openclaw gateway` | 启动 Gateway |
| `openclaw gateway --help` | 查看 Gateway 帮助 |
| `openclaw models list` | 查看可用模型 |
| `openclaw models status` | 查看模型状态 |
| `openclaw sessions` | 查看会话列表 |
| `openclaw doctor` | 健康检查 |
| `openclaw config validate` | 验证配置文件 |

---

## 关键技术说明：关于计费数据的非实时性

在测试过程中，必须考虑以下两个导致"数据不一致"的客观因素：

1. **计数触发时机差异**：
   - **本地代理 (`llm-proxy`)**：通常在流式响应（Streaming）完全结束、连接关闭后才完成单次请求的最终计数。
   - **服务端后端**：部分服务商在接收到请求头或发出首个 Token 时即开始计算预扣费，或在流式传输过程中分段计算。
2. **控制台入账延迟**：
   - 服务商的计费系统（Billing System）与 API 网关通常是异步处理的。控制台显示的使用量更新可能存在 **1-30 分钟不等的延迟**。
   - **对策**：在完成所有本地测试步骤后，建议**静置 30 分钟以上**再观察控制台最终数值，并以多次测试后的累计增量作为核心参考。

## 计费倍率计算方法

```
计费倍率 = 控制台显示的使用量增量 / 本地代理记录的实际请求数
```

**判定标准：**

| 倍率范围 | 判断 | 说明 |
|----------|------|------|
| ≈ 1.0 | ✅ 正常 | 计费透明 |
| 1.0 - 1.2 | ⚠️ 可能存在技术性偏差 | 网络重试、心跳等可能导致轻微偏差 |
| > 1.2 | 🚨 可疑 | 建议深入调查，可能存在隐藏倍率 |

**示例**：
- 本地发起 10 次 API 调用
- 控制台显示使用了 15 次
- 计费倍率 = 15 / 10 = **1.5 倍** → 🚨 可疑

---

## 免责声明

**在使用本测试方案前，请仔细阅读以下条款：**

1. **非官方合规性**：本方案属于第三方独立测试行为，其测试结果仅代表特定环境下的技术观测，不代表相关服务商的官方立场。
2. **数据安全风险**：测试过程中涉及 API 密钥（API Key）的配置与请求拦截，请确保在受信任的本地环境中操作。因使用本方案导致的密钥泄露、账号封禁或欠费损失，由使用者自行承担。
3. **技术局限性**：鉴于流式响应（Streaming）在 Token 统计上的技术限制，本方案的统计结果可能与最终账单存在合理范围内的技术性偏差（如网络重试导致的重复计数）。
4. **合法合规用途**：本测试方案仅限用于技术研究与公益性质的透明度监督，禁止用于任何形式的恶意攻击、滥用 API 资源或违反服务商《服务条款》（ToS）的行为。
5. **解释权**：本方案的逻辑针对当前接口版本，服务商后续的技术调整可能导致本方案部分或全部失效。

## 公益声明

本项目为公益活动"你的 CodingPlan 被几倍计数了"的测试方案，旨在：
- 推动计费透明化
- 保护消费者知情权
- 促进公平竞争的市场环境

**欢迎社区贡献**：
- 提交测试结果和证据
- 完善测试方法论
- 翻译文档
