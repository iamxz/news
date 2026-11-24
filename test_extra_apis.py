#!/usr/bin/env python3
"""测试其他免费翻译 API"""
import requests
import json

proxies = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
text = "Hello world, this is a test."

# 1. MyMemory（已知可用，验证稳定性）
print("=== MyMemory ===")
try:
    r = requests.get(
        "https://api.mymemory.translated.net/get",
        params={"q": text, "langpair": "en|zh-CN"},
        proxies=proxies, timeout=10
    )
    print(f"  Status: {r.status_code}, Result: {r.json().get('responseData', {}).get('translatedText', '')[:100]}")
except Exception as e:
    print(f"  Error: {e}")

# 2. Google Translate（不同客户端参数）
print("\n=== Google Translate (client=at) ===")
try:
    r = requests.get(
        "https://translate.googleapis.com/translate_a/single",
        params={"client": "at", "sl": "en", "tl": "zh-CN", "dt": "t", "q": text},
        headers={'User-Agent': 'Mozilla/5.0 (Android 10; Mobile; rv:131.0) Gecko/131.0 Firefox/131.0'},
        proxies=proxies, timeout=10
    )
    if r.status_code == 200:
        result = r.json()
        translated = "".join(item[0] for item in result[0] if item and item[0])
        print(f"  Status: {r.status_code}, Result: {translated[:100]}")
    else:
        print(f"  Status: {r.status_code}, Body: {r.text[:200]}")
except Exception as e:
    print(f"  Error: {e}")

# 3. Google Translate (client=gtx)
print("\n=== Google Translate (client=gtx) ===")
try:
    r = requests.get(
        "https://translate.googleapis.com/translate_a/single",
        params={"client": "gtx", "sl": "en", "tl": "zh-CN", "dt": "t", "q": text},
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'},
        proxies=proxies, timeout=10
    )
    if r.status_code == 200:
        result = r.json()
        translated = "".join(item[0] for item in result[0] if item and item[0])
        print(f"  Status: {r.status_code}, Result: {translated[:100]}")
    else:
        print(f"  Status: {r.status_code}, Body: {r.text[:200]}")
except Exception as e:
    print(f"  Error: {e}")

# 4. Google Translate 不用代理
print("\n=== Google Translate (无代理) ===")
try:
    r = requests.get(
        "https://translate.googleapis.com/translate_a/single",
        params={"client": "gtx", "sl": "en", "tl": "zh-CN", "dt": "t", "q": text},
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'},
        timeout=10
    )
    if r.status_code == 200:
        result = r.json()
        translated = "".join(item[0] for item in result[0] if item and item[0])
        print(f"  Status: {r.status_code}, Result: {translated[:100]}")
    else:
        print(f"  Status: {r.status_code}, Body: {r.text[:200]}")
except Exception as e:
    print(f"  Error: {e}")

# 5. MyMemory 第二次测试（验证限流）
print("\n=== MyMemory (第二次) ===")
try:
    r = requests.get(
        "https://api.mymemory.translated.net/get",
        params={"q": "Good morning", "langpair": "en|zh-CN"},
        proxies=proxies, timeout=10
    )
    print(f"  Status: {r.status_code}, Result: {r.json().get('responseData', {}).get('translatedText', '')[:100]}")
except Exception as e:
    print(f"  Error: {e}")

# 6. Yandex 翻译 (免费 web 接口)
print("\n=== Yandex Translate ===")
try:
    r = requests.post(
        "https://translate.yandex.net/api/v1/tr.json/translate",
        params={"id": "12345678-1234-1234-1234-123456789012-0"},
        data={"text": text, "lang": "en-zh"},
        headers={'User-Agent': 'Mozilla/5.0'},
        proxies=proxies, timeout=10
    )
    print(f"  Status: {r.status_code}, Body: {r.text[:200]}")
except Exception as e:
    print(f"  Error: {e}")

# 7. DuckDuckGo 翻译
print("\n=== DuckDuckGo Translate ===")
try:
    r = requests.post(
        "https://duckduckgo.com/translation.js",
        data={"q": text, "to": "zh"},
        headers={'User-Agent': 'Mozilla/5.0'},
        proxies=proxies, timeout=10
    )
    print(f"  Status: {r.status_code}, Body: {r.text[:200]}")
except Exception as e:
    print(f"  Error: {e}")

# 8. Reverso
print("\n=== Reverso Translate ===")
try:
    r = requests.post(
        "https://api.reverso.net/translate/v1/translation",
        json={"input": text, "from": "eng", "to": "chi", "format": "text"},
        headers={
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        proxies=proxies, timeout=10
    )
    print(f"  Status: {r.status_code}, Body: {r.text[:200]}")
except Exception as e:
    print(f"  Error: {e}")
