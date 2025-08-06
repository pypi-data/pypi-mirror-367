#!/usr/bin/env python3
"""
BiliDownloader命令行脚本
"""

import sys
import os

# 添加当前目录到Python路径以便导入
def setup_path():
    """设置Python路径"""
    # 获取包的安装目录
    package_dir = os.path.dirname(os.path.abspath(__file__))
    if package_dir not in sys.path:
        sys.path.insert(0, package_dir)

def main():
    """主函数"""
    setup_path()
    
    try:
        # 导入主程序
        from main import main as app_main
        return app_main()
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保所有依赖都已正确安装")
        return 1

if __name__ == "__main__":
    sys.exit(main())