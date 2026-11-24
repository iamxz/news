#!/usr/bin/env python3
"""测试 Bing 翻译 - 带 AbusePreventionHelper token"""
import re
import json
import requests

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
})

# 获取页面和 token
r = s.get('https://www.bing.com/translator', timeout=10)
ig = re.search(r'IG:"([^"]+)"', r.text).group(1)
iid = re.search(r'data-iid="([^"]+)"', r.text).group(1)

# 提取 AbusePreventionHelper
abuse_match = re.search(r'params_AbusePreventionHelper\s*=\s*(\[.*?\])', r.text)
abuse_data = json.loads(abuse_match.group(1)) if abuse_match else []
print(f"IG={ig}")
print(f"IID={iid}")
print(f"AbusePreventionHelper={abuse_data}")

# 提取 pid
pid_match = re.search(r'params_pid\s*=\s*"([^"]+)"', r.text)
pid = pid_match.group(1) if pid_match else ""
print(f"PID={pid}")

# 方案: 带 abuse prevention token 的 ttranslatev3
print("\n=== 带 token 的 ttranslatev3 ===")
url = f'https://www.bing.com/ttranslatev3?isVertical=1&IG={ig}&IID={iid}'

# 构建请求体 - 包含 abuse prevention 信息
payload = {
    "text": "Hello world",
    "fromLang": "en",
    "to": "zh-Hans",
    "tryAttemptGeography": True,
    "serverPD": "translator",
}

if abuse_data:
    payload["AbusePreventionHelper"] = abuse_data

# 也试试在 header 中带 token
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Referer': 'https://www.bing.com/translator',
}

r2 = s.post(url, json=payload, headers=headers, timeout=10)
print(f"Status={r2.status_code} len={len(r2.text)} body={r2.text[:500]}")

# 方案: 使用 key 和 token 在 URL 参数中
print("\n=== 带 key 和 token 在 URL 参数中 ===")
if abuse_data:
    # abuse_data = [timestamp, key, maxDuration]
    ts = abuse_data[0]
    key = abuse_data[1]
    url2 = f'https://www.bing.com/ttranslatev3?isVertical=1&IG={ig}&IID={iid}&key={key}&token={ts}'
    payload2 = {
        "text": "Hello world",
        "fromLang": "en",
        "to": "zh-Hans",
        "tryAttemptGeography": True,
    }
    r3 = s.post(url2, json=payload2, headers=headers, timeout=10)
    print(f"Status={r3.status_code} len={len(r3.text)} body={r3.text[:500]}")

# 方案: 直接使用 /ttranslatev3 不带任何额外参数，只带 Referer
print("\n=== 最简请求 + Referer ===")
url3 = f'https://www.bing.com/ttranslatev3'
payload3 = {
    "text": "Hello world",
    "fromLang": "en",
    "to": "zh-Hans",
}
r4 = s.post(url3, json=payload3, headers=headers, timeout=10)
print(f"Status={r4.status_code} len={len(r4.text)} body={r4.text[:500]}")

# 方案: 使用 /api/v1/translator/translate
print("\n=== 使用 edge-api ===")
url4 = 'https://www.bing.com/translator/api/translate'
payload4 = {"text": "Hello world", "from": "en", "to": "zh-Hans"}
try:
    r5 = s.post(url4, json=payload4, headers=headers, timeout=10)
    print(f"Status={r5.status_code} len={len(r5.text)} body={r5.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
