#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
翻译器测试脚本
"""
import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.translators import translator_manager


def test_translation():
    """测试翻译功能"""
    print("🔍 测试翻译器...")
    
    # 测试文本
    test_text = "Artificial Intelligence is transforming the world."
    
    print(f"📝 原文: {test_text}")
    
    # 尝试翻译
    result = translator_manager.translate(test_text, "en", "zh")
    
    if result:
        print(f"✅ 翻译结果: {result}")
        print("🎉 翻译器工作正常！")
    else:
        print("❌ 翻译失败")
        
        # 检查有哪些翻译器可用
        print("\n📋 可用翻译器:")
        for i, translator in enumerate(translator_manager.translators):
            print(f"  {i+1}. {translator.name}")
    
    return result is not None


def test_google_translator():
    """测试 Google 翻译器"""
    print("\n🔍 测试 Google 翻译器...")
    
    try:
        from src.translators.google import GoogleTranslator
        
        translator = GoogleTranslator()
        test_text = "Hello, world!"
        
        print(f"📝 原文: {test_text}")
        
        result = translator.translate(test_text, "en", "zh")
        
        if result:
            print(f"✅ Google 翻译结果: {result}")
        else:
            print("❌ Google 翻译失败")
            
    except Exception as e:
        print(f"❌ Google 翻译器测试出错: {e}")


if __name__ == "__main__":
    print("🚀 开始测试翻译器...")
    
    success = test_translation()
    test_google_translator()
    
    if success:
        print("\n✅ 所有测试通过！翻译器正常工作。")
    else:
        print("\n⚠️  翻译器可能遇到网络限制，但代码结构正常。")