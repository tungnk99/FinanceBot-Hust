#!/usr/bin/env python3
"""
FinanceBot Demo Runner
Quick script to run the FinanceBot Gradio demo
"""
import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import gradio
        print("✅ Gradio is installed")
        return True
    except ImportError:
        print("❌ Gradio not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "gradio>=4.0.0"])
            print("✅ Gradio installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Gradio")
            return False

def check_environment():
    """Check if environment variables are set"""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    print("✅ Environment variables are set")
    return True

def main():
    """Main function to run the demo"""
    print("🚀 FinanceBot Demo Runner")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("❌ Requirements check failed")
        return 1
    
    # Check environment
    if not check_environment():
        print("❌ Environment check failed")
        return 1
    
    # Change to the ui directory
    ui_dir = Path(__file__).parent
    os.chdir(ui_dir)
    
    print("🌐 Starting FinanceBot Demo...")
    print("📍 Demo will be available at: http://localhost:7860")
    print("🛑 Press Ctrl+C to stop the demo")
    print("=" * 50)
    
    try:
        # Run the demo
        subprocess.run([sys.executable, "demo.py"])
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

