#!/usr/bin/env python3
"""测试 Bing 翻译 - 方案3: 解决 statusCode 205 问题

205 状态码通常意味着请求被标记为可能的滥用。
需要正确构建 AbusePreventionHelper 参数。
"""
import re
import json
import time
import requests

proxies = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
})

# 1. 访问翻译页面
r = s.get('https://www.bing.com/translator', proxies=proxies, timeout=10)
ig = re.search(r'IG:"([^"]+)"', r.text).group(1)
iid = re.search(r'data-iid="([^"]+)"', r.text).group(1)
abuse = re.search(r'params_AbusePreventionHelper\s*=\s*(\[.*?\])', r.text)
abuse_val = json.loads(abuse.group(1)) if abuse else []

print(f"IG: {ig}")
print(f"IID: {iid}")
print(f"Abuse: {abuse_val}")
# abuse_val = [timestamp, key, maxDurationSec]
# timestamp 是当前时间戳(毫秒)，key 是一个 token

# 2. 构建翻译请求 - 关键是 AbusePreventionHelper 格式
url = f'https://www.bing.com/ttranslatev3?isVertical=1&IG={ig}&IID={iid}'

# 方案: 在请求体中带上 AbusePreventionHelper 作为列表
# 参数名可能是 "AbusePreventionHelper" 或 "abusePrevention"
print("\n=== 带 AbusePreventionHelper 列表格式 ===")
ts_now = int(time.time() * 1000)
if abuse_val:
    # [originalTimestamp, key, maxDuration]
    # 当前时间应该在原始时间戳后 maxDuration 内
    payload = {
        "text": "Hello world",
        "fromLang": "en",
        "to": "zh-Hans",
        "tryAttemptGeography": True,
        "AbusePreventionHelper": abuse_val,
    }
else:
    payload = {
        "text": "Hello world",
        "fromLang": "en",
        "to": "zh-Hans",
    }

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=UTF-8',
    'Referer': 'https://www.bing.com/translator',
    'Origin': 'https://www.bing.com',
    'X-MSEdge-Ref': '1',
}

r2 = s.post(url, json=payload, headers=headers, proxies=proxies, timeout=10)
print(f"Status: {r2.status_code}, Body: {r2.text[:500]}")

# 方案: URL 中带 token
print("\n=== URL 中带 abuse token ===")
if abuse_val:
    url2 = f'https://www.bing.com/ttranslatev3?isVertical=1&IG={ig}&IID={iid}&key={abuse_val[1]}&token={abuse_val[0]}'
    payload2 = {
        "text": "Hello world",
        "fromLang": "en",
        "to": "zh-Hans",
    }
    r3 = s.post(url2, json=payload2, headers=headers, proxies=proxies, timeout=10)
    print(f"Status: {r3.status_code}, Body: {r3.text[:500]}")

# 方案: 使用 JS 端点返回的实际翻译 API
# 在 Bing 翻译页面中搜索实际的翻译 API 调用 URL
print("\n=== 搜索页面中的其他 API 端点 ===")
# 搜索 ttranslatev3 前缀
api_matches = re.findall(r'(https?://[^"\']+ttranslatev3[^"\']*)', r.text)
for m in api_matches[:5]:
    print(f"  Found: {m}")

# 搜索 translate 相关的 URL
api_matches2 = re.findall(r'(https?://[^"\']+translate[^"\']*)', r.text)
for m in api_matches2[:10]:
    print(f"  Found: {m}")

# 搜索 /tdetect 或 /tSpeak
api_matches3 = re.findall(r'(/t\w+v?\d*)', r.text)
for m in set(api_matches3):
    print(f"  Endpoint: {m}")

# 方案: 使用 Bing 的 systran 端点
print("\n=== 尝试 systran/bing 旧端点 ===")
for alt_url in [
    "https://www.bing.com/translator/api/Translate/TranslateArray",
    "https://www.bing.com/api/v1/translator",
    "https://www.bing.com/translator/api/translate",
]:
    try:
        payload_alt = {"text": "Hello", "from": "en", "to": "zh-Hans"}
        r_alt = s.post(alt_url, json=payload_alt, headers=headers, proxies=proxies, timeout=5)
        print(f"  {alt_url}: {r_alt.status_code} -> {r_alt.text[:100]}")
    except Exception as e:
        print(f"  {alt_url}: {e}")

# 方案: 看看 cookies 中有什么特殊的
print("\n=== Cookies 详情 ===")
for name, value in s.cookies.items():
    print(f"  {name} = {value[:80]}")

# 查找 _U cookie (Bing 的用户 token)
u_cookie = s.cookies.get('_U')
print(f"\n_U cookie: {u_cookie}")
