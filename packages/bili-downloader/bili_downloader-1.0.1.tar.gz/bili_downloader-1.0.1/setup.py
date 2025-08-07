#!/usr/bin/env python3
"""
BiliDownloader安装配置
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Bilibili视频下载器 - 类似yt-dlp的B站视频下载工具"

# 读取requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return requirements

setup(
    name="bili-downloader",
    version="1.0.1",
    author="BiliDownloader Team",
    author_email="",
    description="Bilibili视频下载器 - 类似yt-dlp的B站视频下载工具",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/bili-downloader",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "b-d=bili_downloader.cli:main",
            "bili-dl=bili_downloader.cli:main", 
            "bilidown=bili_downloader.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json"],
    },
    keywords="bilibili video downloader youtube-dl yt-dlp",
    project_urls={
        "Bug Reports": "https://github.com/your-username/bili-downloader/issues",
        "Source": "https://github.com/your-username/bili-downloader",
        "Documentation": "https://github.com/your-username/bili-downloader/blob/main/README.md",
    },
)