#!/usr/bin/env python3
"""
测试整个翻译系统
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.translators import translator_manager

def test_translation_system():
    """测试整个翻译系统"""
    print("Testing translation system...")
    
    # 测试文本
    test_texts = [
        "Global economic trends are changing rapidly.",
        "Technology innovation drives market growth.",
        "Climate change is a global challenge.",
    ]
    
    for text in test_texts:
        print(f"\nTranslating: {text}")
        result = translator_manager.translate(text)
        print(f"Result: {result}")


if __name__ == "__main__":
    test_translation_system()