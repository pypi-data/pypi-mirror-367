#!/usr/bin/env python3
"""
构建测试脚本
用于验证项目是否可以正确构建和安装
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {cmd}")
        print(f"错误输出: {e.stderr}")
        return None

def test_build():
    """测试构建过程"""
    print("🔨 开始构建测试...")
    
    # 清理之前的构建
    print("🧹 清理之前的构建文件...")
    if sys.platform == "win32":
        run_command("if exist dist rmdir /s /q dist")
        run_command("if exist build rmdir /s /q build")
        run_command("if exist *.egg-info rmdir /s /q *.egg-info")
    else:
        run_command("rm -rf dist/ build/ *.egg-info/")
    
    # 构建包
    print("📦 构建包...")
    result = run_command("python -m build --sdist --wheel")
    if result is None:
        print("❌ 构建失败")
        return False
    
    print("✅ 构建成功")
    
    # 检查构建产物
    print("🔍 检查构建产物...")
    if not os.path.exists("dist"):
        print("❌ dist 目录不存在")
        return False
    
    files = os.listdir("dist")
    print(f"📁 构建产物: {files}")
    
    # 验证包
    print("✅ 验证包...")
    result = run_command("python -m twine check dist/*")
    if result is None:
        print("❌ 包验证失败")
        return False
    
    print("✅ 包验证成功")
    return True

def test_install():
    """测试安装过程"""
    print("\n📥 开始安装测试...")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 创建临时目录: {temp_dir}")
        
        # 复制构建的包到临时目录
        if os.path.exists("dist"):
            for file in os.listdir("dist"):
                if file.endswith(".whl"):
                    shutil.copy(f"dist/{file}", temp_dir)
                    print(f"📋 复制包文件: {file}")
        
        # 创建虚拟环境
        print("🐍 创建虚拟环境...")
        venv_dir = os.path.join(temp_dir, "venv")
        run_command(f"python -m venv {venv_dir}")
        
        # 激活虚拟环境并安装
        if sys.platform == "win32":
            activate_script = os.path.join(venv_dir, "Scripts", "activate")
            pip_path = os.path.join(venv_dir, "Scripts", "pip")
        else:
            activate_script = os.path.join(venv_dir, "bin", "activate")
            pip_path = os.path.join(venv_dir, "bin", "pip")
        
        # 安装包
        print("📦 安装包...")
        wheel_files = [f for f in os.listdir(temp_dir) if f.endswith(".whl")]
        if not wheel_files:
            print("❌ 没有找到 wheel 文件")
            return False
        
        wheel_file = wheel_files[0]
        result = run_command(f"{pip_path} install {wheel_file}", cwd=temp_dir)
        if result is None:
            print("❌ 安装失败")
            return False
        
        print("✅ 安装成功")
        
        # 测试插件元数据（不初始化 NoneBot）
        print("📋 测试插件元数据...")
        python_path = os.path.join(venv_dir, "Scripts", "python") if sys.platform == "win32" else os.path.join(venv_dir, "bin", "python")
        result = run_command(f'{python_path} -c "from nonebot_plugin_dst_qq import __plugin_meta__; print(\'插件名称:\', __plugin_meta__.name)"', cwd=temp_dir)
        if result is None:
            print("❌ 插件元数据测试失败")
            return False
        
        print("✅ 插件元数据正常")
        
        # 测试配置模块导入
        print("🧪 测试配置模块导入...")
        result = run_command(f'{python_path} -c "import nonebot_plugin_dst_qq.config; print(\'配置模块导入成功\')"', cwd=temp_dir)
        if result is None:
            print("❌ 配置模块导入失败")
            return False
        
        print("✅ 配置模块导入成功")
    
    return True

def main():
    """主函数"""
    print("🚀 开始项目构建测试")
    print("=" * 50)
    
    # 检查必要文件
    required_files = [
        "pyproject.toml",
        "setup.py", 
        "requirements.txt",
        "README.md",
        "LICENSE",
        "CHANGELOG.md",
        "MANIFEST.in",
        "nonebot_plugin_dst_qq/__init__.py"
    ]
    
    print("📋 检查必要文件...")
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - 文件不存在")
            return False
    
    # 测试构建
    if not test_build():
        return False
    
    # 测试安装
    if not test_install():
        return False
    
    print("\n" + "=" * 50)
    print("🎉 所有测试通过！项目可以发布到 PyPI")
    print("\n📝 下一步:")
    print("1. 运行: twine upload dist/*")
    print("2. 前往 NoneBot 商店提交插件")
    print("3. 等待审核通过")

if __name__ == "__main__":
    main() 