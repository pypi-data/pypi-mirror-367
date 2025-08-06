#!/usr/bin/env python3
"""
简单的导入测试脚本
"""

def test_import():
    """测试插件导入"""
    try:
        print("🧪 测试插件导入...")
        
        # 测试主插件导入
        import nonebot_plugin_dst_qq
        print("✅ 主插件导入成功")
        
        # 测试插件元数据
        from nonebot_plugin_dst_qq import __plugin_meta__
        print(f"✅ 插件元数据: {__plugin_meta__.name}")
        
        # 测试配置模块
        import nonebot_plugin_dst_qq.config
        print("✅ 配置模块导入成功")
        
        # 测试数据库模块
        import nonebot_plugin_dst_qq.database
        print("✅ 数据库模块导入成功")
        
        print("\n🎉 所有导入测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 导入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_import() 