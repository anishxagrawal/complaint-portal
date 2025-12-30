#!/usr/bin/env python3
"""
Check available Gemini models for your API key
Run from backend directory: python check_models.py
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ GEMINI_API_KEY not found in .env")
    exit(1)

print("🔍 Checking available Gemini models...\n")

# Configure API
genai.configure(api_key=api_key)

# List all available models
print("=" * 70)
print("Available Models for generateContent:")
print("=" * 70)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"\n✅ {model.name}")
        print(f"   Display Name: {model.display_name}")
        print(f"   Description: {model.description[:100]}...")

print("\n" + "=" * 70)
print("\n💡 Recommended models to use:")
print("   - gemini-pro (stable)")
print("   - gemini-1.5-pro-latest (newest)")
print("   - gemini-1.5-flash-latest (fastest)")
print("\n🧪 Testing gemini-pro...")

try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say hello in one word")
    print(f"✅ gemini-pro works! Response: {response.text}")
except Exception as e:
    print(f"❌ gemini-pro failed: {e}")

print("\n🧪 Testing gemini-1.5-pro-latest...")
try:
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    response = model.generate_content("Say hello in one word")
    print(f"✅ gemini-1.5-pro-latest works! Response: {response.text}")
except Exception as e:
    print(f"❌ gemini-1.5-pro-latest failed: {e}")

print("\n🧪 Testing gemini-1.5-flash-latest...")
try:
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content("Say hello in one word")
    print(f"✅ gemini-1.5-flash-latest works! Response: {response.text}")
except Exception as e:
    print(f"❌ gemini-1.5-flash-latest failed: {e}")