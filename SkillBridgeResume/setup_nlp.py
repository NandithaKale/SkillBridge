#!/usr/bin/env python3
"""
Download spaCy language model for NLP-based skill matching
"""

import subprocess
import sys

def setup_spacy():
    print("=" * 70)
    print("🧠 Setting up spaCy for NLP-based Skill Matching")
    print("=" * 70)
    print()
    
    print("📦 Installing spaCy...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "spacy"])
        print("✅ spaCy installed successfully!")
    except Exception as e:
        print(f"❌ Error installing spaCy: {e}")
        return False
    
    print("\n📥 Downloading English language model (en_core_web_md)...")
    print("   This may take a few minutes...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_md"])
        print("✅ Language model downloaded successfully!")
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        print("\n💡 Try running manually: python -m spacy download en_core_web_md")
        return False
    
    print("\n" + "=" * 70)
    print("✅ NLP Setup Complete!")
    print("=" * 70)
    print("\n🎯 The system can now understand:")
    print("   • 'python' matches 'python programming'")
    print("   • 'ML' matches 'machine learning'")
    print("   • 'js' matches 'javascript'")
    print("   • And many more semantic similarities!")
    print()
    
    return True

if __name__ == "__main__":
    success = setup_spacy()
    if success:
        print("🚀 Run the system: streamlit run dashboard/real_time_app.py")
    else:
        print("⚠️  Please fix the errors above and try again")
        sys.exit(1)