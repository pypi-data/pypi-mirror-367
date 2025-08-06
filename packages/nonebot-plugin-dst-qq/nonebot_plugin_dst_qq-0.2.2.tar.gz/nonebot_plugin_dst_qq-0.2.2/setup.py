#!/usr/bin/env python3
"""
Setup script for nonebot-plugin-dst-qq
"""

from setuptools import setup, find_packages

# 读取 README 文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取 requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="nonebot-plugin-dst-qq",
    version="0.2.1",
    author="nonebot-plugin-dst-qq",
    author_email="nonebot-plugin-dst-qq@example.com",
    description="基于 NoneBot2 的饥荒管理平台 (DMP) QQ 机器人插件，支持游戏信息查询、命令执行和消息互通功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nonebot/nonebot-plugin-dst-qq",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: NoneBot",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    keywords=["nonebot", "nonebot2", "plugin", "dst", "dmp", "饥荒", "don't starve together", "qq-bot", "message-exchange"],
    project_urls={
        "Homepage": "https://github.com/nonebot/nonebot-plugin-dst-qq",
        "Repository": "https://github.com/nonebot/nonebot-plugin-dst-qq",
        "Documentation": "https://github.com/nonebot/nonebot-plugin-dst-qq#readme",
        "Bug Tracker": "https://github.com/nonebot/nonebot-plugin-dst-qq/issues",
    },
) 