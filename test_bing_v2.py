#!/usr/bin/env python3
"""测试 Bing 翻译 - 方案2: 完整 cookie + ttranslatev3"""
import re
import json
import time
import requests

proxies = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
})

# 1. 访问翻译页面，获取 cookie 和 IG token
r = s.get('https://www.bing.com/translator', proxies=proxies, timeout=10)
print(f"页面状态: {r.status_code}")
print(f"Cookies: {dict(s.cookies)}")

ig = re.search(r'IG:"([^"]+)"', r.text)
iid = re.search(r'data-iid="([^"]+)"', r.text)
abuse = re.search(r'params_AbusePreventionHelper\s*=\s*(\[.*?\])', r.text)

if not ig:
    print("无法获取 IG token")
    exit(1)

ig_val = ig.group(1)
iid_val = iid.group(1) if iid else "translator.5023"
abuse_val = json.loads(abuse.group(1)) if abuse else []

print(f"IG: {ig_val}")
print(f"IID: {iid_val}")
print(f"Abuse: {abuse_val}")

# 2. 构建翻译请求
url = f'https://www.bing.com/ttranslatev3?isVertical=1&IG={ig_val}&IID={iid_val}'

# 方案 A: 标准格式
print("\n=== 方案 A: 标准格式 ===")
payload_a = {
    "text": "Hello world",
    "fromLang": "en",
    "to": "zh-Hans",
    "tryAttemptGeography": True,
}
headers_a = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8',
    'Referer': 'https://www.bing.com/translator',
    'Origin': 'https://www.bing.com',
}
r2 = s.post(url, json=payload_a, headers=headers_a, proxies=proxies, timeout=10)
print(f"Status: {r2.status_code}, Length: {len(r2.text)}, Body: {r2.text[:300]}")

# 方案 B: 数组格式（像 Azure 翻译 API）
print("\n=== 方案 B: 数组格式 ===")
payload_b = [{"text": "Hello world", "to": "zh-Hans", "from": "en"}]
r3 = s.post(url, json=payload_b, headers=headers_a, proxies=proxies, timeout=10)
print(f"Status: {r3.status_code}, Length: {len(r3.text)}, Body: {r3.text[:300]}")

# 方案 C: 带 abuse prevention token
print("\n=== 方案 C: 带 abuse prevention ===")
if abuse_val:
    payload_c = {
        "text": "Hello world",
        "fromLang": "en",
        "to": "zh-Hans",
        "tryAttemptGeography": True,
        "AbusePreventionHelper": abuse_val,
    }
    r4 = s.post(url, json=payload_c, headers=headers_a, proxies=proxies, timeout=10)
    print(f"Status: {r4.status_code}, Length: {len(r4.text)}, Body: {r4.text[:300]}")

# 方案 D: 不用代理直接访问
print("\n=== 方案 D: 不用代理 ===")
s2 = requests.Session()
s2.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html',
})
r5 = s2.get('https://www.bing.com/translator', timeout=10)
ig2 = re.search(r'IG:"([^"]+)"', r5.text)
if ig2:
    url2 = f'https://www.bing.com/ttranslatev3?isVertical=1&IG={ig2.group(1)}'
    payload_d = {"text": "Hello world", "fromLang": "en", "to": "zh-Hans"}
    r6 = s2.post(url2, json=payload_d, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=UTF-8',
        'Referer': 'https://www.bing.com/translator',
    }, timeout=10)
    print(f"Status: {r6.status_code}, Length: {len(r6.text)}, Body: {r6.text[:300]}")
else:
    print("无法获取 IG token（无代理）")

# 方案 E: 使用 sw-cdn 上的 Edge 侧边栏翻译 API（另一种已知方案）
print("\n=== 方案 E: edge.flipfl ag 等其他端点 ===")
# 尝试新版 edge translate 端点
for edge_url in [
    "https://edge.microsoft.com/translate_auth",
    "https://api-edge.cognitive.microsofttranslator.com/auth",
    "https://edge.microsoft.com/translate/auth/token",
    "https://api.cognitive.microsoft.com/sts/v1.0/issueToken",
]:
    try:
        rr = requests.get(edge_url, proxies=proxies, timeout=5, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36',
        })
        print(f"  {edge_url}: {rr.status_code} -> {rr.text[:80]}")
    except Exception as e:
        print(f"  {edge_url}: ERROR {e}")
