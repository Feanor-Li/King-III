#!/usr/bin/env python3
"""
Development Environment Startup Script
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_directories():
    """创建必要的目录"""
    dirs = [
        "/tmp/smart_photo_uploads",
        "/tmp/smart_photo_output"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ 创建目录: {dir_path}")

def check_dependencies():
    """检查依赖是否安装"""
    print("检查Python依赖...")
    
    try:
        import fastapi
        import uvicorn
        import langgraph
        import cv2
        import numpy as np
        from PIL import Image
        print("✓ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def create_env_file():
    """创建开发环境配置文件"""
    env_file = Path(".env")
    if not env_file.exists():
        print("创建开发环境配置文件...")
        with open(env_file, "w") as f:
            f.write("""# 开发环境配置
HOST=127.0.0.1
PORT=8000
DEBUG=true
LOG_LEVEL=debug
UPLOAD_DIR=/tmp/smart_photo_uploads
OUTPUT_DIR=/tmp/smart_photo_output
IPHONE_API_ENDPOINT=http://localhost:8080/iphone-control
CAPTURE_API_ENDPOINT=http://localhost:8080/iphone-capture
""")
        print("✓ 已创建 .env 文件")

def run_tests():
    """运行简单测试"""
    print("\n运行基本测试...")
    
    try:
        from smart_photo_system import PhotoSystemState
        from smart_photo_system.models.state import CameraParams
        
        # 测试状态创建
        state = PhotoSystemState(session_id="test-123")
        print("✓ 状态模型测试通过")
        
        # 测试参数创建
        params = CameraParams(aperture="f/2.8", exposure=1.0)
        print("✓ 参数模型测试通过")
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def start_server():
    """启动开发服务器"""
    print("\n🚀 启动开发服务器...")
    print("服务地址: http://127.0.0.1:8000")
    print("API文档: http://127.0.0.1:8000/docs")
    print("按 Ctrl+C 停止服务器\n")
    
    try:
        os.system("python main.py")
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")

def main():
    """主函数"""
    print("🔧 智能拍照系统开发环境启动器")
    print("=" * 40)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 设置目录
    setup_directories()
    
    # 创建配置文件
    create_env_file()
    
    # 运行测试
    if not run_tests():
        print("测试失败，请检查代码")
        sys.exit(1)
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()
