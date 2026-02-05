#!/usr/bin/env python3
"""
测试新的免费翻译器
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.translators.free_translator import FreeTranslator
from src.translators.google import GoogleTranslator


def test_free_translator():
    """测试免费翻译器"""
    print("Testing Free Translator...")
    
    # 测试 GoogleTranslator（免费，不需要API密钥）
    google_translator = GoogleTranslator()
    if google_translator:
        text = "Global economic trends are changing rapidly."
        result = google_translator.translate(text)
        print(f"Google Translation: '{text}' -> '{result}'")
    
    # 测试 FreeTranslator（使用googletrans库）
    free_translator = FreeTranslator()
    if free_translator and free_translator.translator:
        text = "Technology innovation drives market growth."
        result = free_translator.translate(text)
        print(f"Free Translator: '{text}' -> '{result}'")
    else:
        print("Free Translator not available (可能由于依赖库问题)")


if __name__ == "__main__":
    test_free_translator()