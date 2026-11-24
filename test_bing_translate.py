#!/usr/bin/env python3
"""测试 Bing 翻译的多种方案"""
import re
import requests

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
})

# 获取页面和 token
r = s.get('https://www.bing.com/translator', timeout=10)
ig = re.search(r'IG:"([^"]+)"', r.text)
iid = re.search(r'data-iid="([^"]+)"', r.text)
print(f"IG={ig.group(1) if ig else 'NOT FOUND'}")
print(f"IID={iid.group(1) if iid else 'NOT FOUND'}")

if not ig:
    print("无法获取 IG token，退出")
    exit(1)

ig_val = ig.group(1)
iid_val = iid.group(1) if iid else "translator.5023"

# 方案1: ttranslatev3 用对象格式
print("\n=== 方案1: ttranslatev3 对象格式 ===")
url1 = f'https://www.bing.com/ttranslatev3?isVertical=1&IG={ig_val}&IID={iid_val}'
payload1 = {"text": "Hello world", "fromLang": "en", "to": "zh-Hans", "tryAttemptGeography": True}
try:
    r1 = s.post(url1, json=payload1, timeout=10)
    print(f"Status={r1.status_code} len={len(r1.text)} body={r1.text[:300]}")
except Exception as e:
    print(f"Error: {e}")

# 方案2: ttranslatev3 用数组格式
print("\n=== 方案2: ttranslatev3 数组格式 ===")
url2 = f'https://www.bing.com/ttranslatev3?isVertical=1&IG={ig_val}&IID={iid_val}'
payload2 = [{"text": "Hello world", "to": "zh-Hans", "from": "en"}]
try:
    r2 = s.post(url2, json=payload2, timeout=10)
    print(f"Status={r2.status_code} len={len(r2.text)} body={r2.text[:300]}")
except Exception as e:
    print(f"Error: {e}")

# 方案3: datapi 端点
print("\n=== 方案3: datapi 端点 ===")
url3 = f'https://www.bing.com/datapi/translate?IG={ig_val}'
payload3 = [{"text": "Hello world", "to": "zh-Hans", "from": "en"}]
try:
    r3 = s.post(url3, json=payload3, timeout=10)
    print(f"Status={r3.status_code} len={len(r3.text)} body={r3.text[:300]}")
except Exception as e:
    print(f"Error: {e}")

# 方案4: 搜索 AbusePreventionHelper token
print("\n=== 搜索页面中的 token/params ===")
abuse = re.search(r'params_AbusePreventionHelper\s*=\s*(\[.*?\])', r.text)
if abuse:
    print(f"AbusePreventionHelper: {abuse.group(1)[:200]}")
else:
    print("AbusePreventionHelper not found")

# 查找 key 和 token
key_match = re.search(r'"key":"([^"]+)"', r.text)
token_match = re.search(r'"token":"([^"]+)"', r.text)
if key_match:
    print(f"Key: {key_match.group(1)[:100]}")
if token_match:
    print(f"Token: {token_match.group(1)[:100]}")

# 查找 pid 和 sid
pid_match = re.search(r'params_pid\s*=\s*"([^"]+)"', r.text)
if pid_match:
    print(f"PID: {pid_match.group(1)}")
