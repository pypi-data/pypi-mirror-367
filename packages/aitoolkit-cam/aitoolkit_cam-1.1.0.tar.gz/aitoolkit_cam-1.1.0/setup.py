#!/usr/bin/env python3
"""
AIToolkit Camera - 简单易用的摄像头工具包
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "AIToolkit Camera - 简单易用的摄像头工具包"

# 读取requirements
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return ["opencv-python>=4.5.0", "numpy>=1.19.0", "Flask>=2.0.0"]

setup(
    name="aitoolkit-cam",
    version="1.1.0",
    author="aitoolkit",
    author_email="your.email@example.com", 
    description="极简Python摄像头库 - 为中学生和ARM64设备特别优化",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/bosscoder-ai/aitoolkit_cam",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video :: Capture",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Education",
        "Framework :: Jupyter",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    keywords="camera opencv video streaming web cv2 jupyter notebook education arm64 raspberry-pi real-time smart-stop",
    project_urls={
        "Bug Reports": "https://github.com/bosscoder-ai/aitoolkit_cam/issues",
        "Source": "https://github.com/bosscoder-ai/aitoolkit_cam",
        "Documentation": "https://github.com/bosscoder-ai/aitoolkit_cam/blob/main/README.md",
    },
    include_package_data=True,
    zip_safe=False,
) 