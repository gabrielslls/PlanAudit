#!/usr/bin/env python3
"""
PlanAudit 非流式调用测试脚本
用于验证云厂商 CodingPlan 的 token 计数准确性

用法:
  python test-non-streaming.py <模型名称> [选项]

示例:
  python test-non-streaming.py glm-5
  python test-non-streaming.py glm-5 --api-base http://127.0.0.1:9000
  python test-non-streaming.py glm-5 --count 5
"""

import argparse
import json
import os
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

os.environ["no_proxy"] = "*"

TEST_CASES = [
    {"name": "简单问候", "messages": [{"role": "user", "content": "你好"}], "max_tokens": 50},
    {"name": "数学计算", "messages": [{"role": "user", "content": "计算 123 + 456 等于多少？"}], "max_tokens": 100},
    {"name": "代码生成", "messages": [{"role": "user", "content": "用 Python 写一个斐波那契数列函数"}], "max_tokens": 200},
    {"name": "文本总结", "messages": [{"role": "user", "content": "请用一句话总结什么是机器学习"}], "max_tokens": 100},
    {"name": "角色扮演", "messages": [{"role": "system", "content": "你是一个资深程序员"}, {"role": "user", "content": "解释一下什么是 RESTful API"}], "max_tokens": 150},
    {"name": "长文本输入", "messages": [{"role": "user", "content": "请详细解释 Python 中的装饰器模式，包括原理、用法和示例代码"}], "max_tokens": 300},
    {"name": "多轮对话", "messages": [{"role": "user", "content": "什么是 Git？"}, {"role": "assistant", "content": "Git 是一个分布式版本控制系统。"}, {"role": "user", "content": "它有哪些主要功能？"}], "max_tokens": 150},
    {"name": "JSON 格式输出", "messages": [{"role": "user", "content": "以 JSON 格式输出一个包含 name、age、city 字段的人员信息示例"}], "max_tokens": 100},
    {"name": "翻译任务", "messages": [{"role": "user", "content": "将以下英文翻译成中文: Artificial Intelligence is transforming every industry."}], "max_tokens": 100},
    {"name": "推理问题", "messages": [{"role": "user", "content": "如果 A 比 B 大，B 比 C 大，那么 A 和 C 谁大？为什么？"}], "max_tokens": 100},
]


def call_api(api_base: str, api_key: str, model: str, messages: list, max_tokens: int = 100) -> dict:
    url = f"{api_base}/chat/completions"
    payload = {"model": model, "messages": messages, "max_tokens": max_tokens, "stream": False}
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    data = json.dumps(payload).encode("utf-8")
    request = Request(url, data=data, headers=headers, method="POST")

    try:
        with urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        return {"error": True, "status": e.code, "message": error_body}
    except URLError as e:
        return {"error": True, "message": str(e)}


def run_tests(api_base: str, api_key: str, model: str, test_count: int):
    print("=" * 60)
    print("PlanAudit 非流式调用测试")
    print("=" * 60)
    print(f"API 地址: {api_base}")
    print(f"模型: {model}")
    print(f"测试次数: {test_count}")
    print("=" * 60)

    print(f"\n开始执行 {test_count} 次非流式调用测试...\n")

    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_tokens = 0
    success_count = 0
    error_count = 0
    total_elapsed = 0

    for i, test_case in enumerate(TEST_CASES[:test_count], 1):
        print(f"  [{i}/{test_count}] {test_case['name']}...", end=" ", flush=True)

        start_time = time.time()
        response = call_api(api_base, api_key, model, test_case["messages"], test_case.get("max_tokens", 100))
        elapsed = time.time() - start_time

        if "error" in response:
            print(f"❌ 失败 ({response.get('status', 'N/A')}): {response.get('message', '')[:50]}")
            error_count += 1
        else:
            usage = response.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            tokens = usage.get("total_tokens", 0)

            total_prompt_tokens += prompt_tokens
            total_completion_tokens += completion_tokens
            total_tokens += tokens
            success_count += 1
            total_elapsed += elapsed

            print(f"✅ prompt={prompt_tokens}, completion={completion_tokens}, total={tokens}, {int(elapsed * 1000)}ms")

    print("\n" + "=" * 60)
    print("测试统计")
    print("=" * 60)
    print(f"  成功请求: {success_count}")
    print(f"  失败请求: {error_count}")
    print(f"  总输入 Token: {total_prompt_tokens}")
    print(f"  总输出 Token: {total_completion_tokens}")
    print(f"  总 Token: {total_tokens}")
    if success_count > 0:
        print(f"  平均响应时间: {int(total_elapsed * 1000 / success_count)}ms")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="PlanAudit 非流式调用测试脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python test-non-streaming.py glm-5
  python test-non-streaming.py glm-5 --api-base http://127.0.0.1:9000
  python test-non-streaming.py deepseek-chat --count 5
        """,
    )
    parser.add_argument("model", help="模型名称（必填）")
    parser.add_argument("--api-base", default="http://127.0.0.1:9000", help="API 地址（默认: http://127.0.0.1:9000）")
    parser.add_argument("--count", type=int, default=10, help="测试次数（默认: 10）")
    parser.add_argument("--api-key", help="API Key（也可通过环境变量 API_KEY 设置）")

    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("API_KEY")

    if not api_key:
        print("=" * 60)
        print("请输入 API Key")
        print("=" * 60)
        print("未检测到 API_KEY 环境变量，请粘贴您的 API Key：")
        print("（粘贴后按回车继续）")
        print()
        try:
            api_key = input("API Key: ").strip()
        except KeyboardInterrupt:
            print("\n\n已取消")
            sys.exit(1)

        if not api_key:
            print("❌ 错误: API Key 不能为空")
            sys.exit(1)

    run_tests(args.api_base, api_key, args.model, args.count)


if __name__ == "__main__":
    main()
