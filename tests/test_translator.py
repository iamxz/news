#!/usr/bin/env python3
"""
测试翻译器
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.translators.google import GoogleTranslator


def test_google_translator():
    """测试Google翻译器"""
    print("Testing Google Translator...")
    
    # 测试 GoogleTranslator（免费，不需要API密钥）
    google_translator = GoogleTranslator()
    if google_translator:
        text = "Global economic trends are changing rapidly."
        result = google_translator.translate(text)
        print(f"Google Translation: '{text}' -> '{result}'")


if __name__ == "__main__":
    test_google_translator()