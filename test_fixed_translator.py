#!/usr/bin/env python3
"""
测试修正后的免费翻译器
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.translators.free_translator import FreeTranslator


def test_free_translator_fixed():
    """测试修正后的免费翻译器"""
    print("Testing Fixed Free Translator...")
    
    # 测试 FreeTranslator（使用googletrans库）
    free_translator = FreeTranslator()
    if free_translator and free_translator.translator:
        text = "Technology innovation drives market growth."
        result = free_translator.translate(text)
        print(f"Free Translator (en->zh): '{text}' -> '{result}'")
        
        # 测试不同的语言组合
        result2 = free_translator.translate("Hello, how are you?", "en", "zh")
        print(f"Free Translator (en->zh): 'Hello, how are you?' -> '{result2}'")
        
        result3 = free_translator.translate("你好，世界！", "zh", "en")
        print(f"Free Translator (zh->en): '你好，世界！' -> '{result3}'")
    else:
        print("Free Translator not available")


if __name__ == "__main__":
    test_free_translator_fixed()