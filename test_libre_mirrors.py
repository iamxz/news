#!/usr/bin/env python3
"""测试多个 LibreTranslate 公共实例"""
import requests

proxies = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}

mirrors = [
    "https://translate.terraprint.co",
    "https://translapi.com",
    "https://libretranslate.org",
    "https://lt.vern.cc",
    "https://translate.bus-hit.me",
    "https://libretranslate.0xfc.de",
    "https://translate.mentaml.0xem.in.ua",
    # 旧镜像
    "https://translate.argosopentech.com",
    "https://libretranslate.de",
    "https://libretranslate.com",
]

for base in mirrors:
    url = f"{base}/translate"
    payload = {"q": "Hello world", "source": "en", "target": "zh", "format": "text"}
    try:
        r = requests.post(url, json=payload, proxies=proxies, timeout=8)
        if r.status_code == 200 and "translatedText" in r.text:
            print(f"✅ {base}: {r.status_code} -> {r.json().get('translatedText', '')[:80]}")
        else:
            print(f"❌ {base}: {r.status_code} -> {r.text[:100]}")
    except Exception as e:
        print(f"❌ {base}: {e}")
