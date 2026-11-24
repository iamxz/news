#!/usr/bin/env python3
"""测试所有翻译器的实际可用性"""
import sys
sys.path.insert(0, '.')

from src.translators import translator_manager
from src.utils.logger import logger

test_text = "Hello world, this is a test."
print(f"测试文本: {test_text}")
print(f"已加载翻译器: {[t.name for t in translator_manager.translators]}")
print()

for translator in translator_manager.translators:
    print(f"--- 测试 {translator.name} ---")
    try:
        result = translator.translate(test_text, "en", "zh")
        if result:
            print(f"✅ 成功: {result[:100]}")
        else:
            print(f"❌ 返回空结果")
    except Exception as e:
        print(f"❌ 异常: {e}")
    print()

print("测试完成")
