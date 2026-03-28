# PlanAudit

**CodingPlan 计费透明度审计工具**

> 你的 CodingPlan 被几倍计数了？

## 项目简介

PlanAudit 是一个公益活动项目，旨在帮助用户验证云服务商 CodingPlan 的计费透明度。

通过中间人代理（MITM）捕获 API 请求，统计实际调用次数，再与控制台显示的使用量对比，判断是否存在隐藏计费倍率。

## 快速开始

### 简化版（快速自测）

适合个人用户快速验证：

```bash
git clone https://github.com/your-org/PlanAudit.git
cd PlanAudit
# 按照 docs/QUICK-START.md 操作
```

[→ 查看简化版指南](docs/QUICK-START.md)

### 取证版（严谨取证）

适合正式投诉、维权场景：

[→ 查看取证版指南](docs/AUDIT-GUIDE.md)

## 原理

```
计费倍率 = 控制台显示的使用量增量 / 本地代理记录的实际请求数
```

| 倍率范围 | 判断 |
|----------|------|
| ≈ 1.0 | ✅ 正常 |
| 1.0 - 1.2 | ⚠️ 可能存在技术性偏差 |
| > 1.2 | 🚨 可疑 |

## 项目结构

```
PlanAudit/
├── README.md              # 项目说明
├── LICENSE                # 许可证
├── docs/                  # 文档
│   ├── AUDIT-GUIDE.md     # 取证版指南
│   ├── QUICK-START.md     # 简化版指南
│   └── TEST-CASE.md       # 测试案例
├── tools/                 # 辅助工具
│   └── test-non-streaming.py  # 非流式调用测试脚本
├── results/               # 测试结果（不入库）
└── evidence/              # 证据目录（不入库）
```

## 支持的客户端

| 客户端 | 状态 |
|--------|------|
| opencode | ✅ 已验证 |
| openclaw | 🚧 开发中 |
| cursor | 📋 计划中 |

## 依赖工具

- [llm-proxy](https://github.com/gabrielslls/llm-proxy) - API 请求代理
- OBS Studio - 屏幕录制（取证版）

## 测试工具

### 非流式调用测试脚本

用于验证 Token 计数准确性（流式响应可能不返回 token 用量）：

```bash
cd tools

# 基本用法
python test-non-streaming.py <模型名称>

# 示例
python test-non-streaming.py glm-5
python test-non-streaming.py glm-5 --count 5
python test-non-streaming.py glm-5 --api-base http://127.0.0.1:9000

# 参数说明
#   model        模型名称（必填）
#   --api-base   API 地址（默认: http://127.0.0.1:9000）
#   --count      测试次数（默认: 10）
#   --api-key    API Key（或设置环境变量 API_KEY）
```

## 公益声明

本项目旨在：
- 推动计费透明化
- 保护消费者知情权
- 促进公平竞争的市场环境

## 免责声明

- 本项目属于第三方独立测试行为
- 测试结果仅代表特定环境下的技术观测
- 仅限用于技术研究与公益性质的透明度监督
- 禁止用于任何恶意攻击或违反服务条款的行为

## 贡献指南

欢迎社区贡献：
- 补充其他客户端的适配配置
- 提交测试结果和证据
- 完善测试方法论
- 翻译文档

## 许可证

[MIT License](LICENSE)

---

**你的 CodingPlan 被几倍计数了？** 🔍
