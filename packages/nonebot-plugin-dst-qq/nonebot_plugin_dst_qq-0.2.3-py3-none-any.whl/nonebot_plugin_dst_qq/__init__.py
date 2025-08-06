from pathlib import Path

import nonebot
from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="DMP 饥荒管理平台机器人",
    description="基于 NoneBot2 的饥荒管理平台 (DMP) QQ 机器人插件，支持游戏信息查询、命令执行和消息互通功能。",
    usage="""基础命令：
- /世界 或 /world - 获取世界信息
- /房间 或 /room - 获取房间信息  
- /系统 或 /sys - 获取系统信息
- /玩家 或 /players - 获取在线玩家列表
- /集群 或 /clusters - 获取集群列表
- /菜单 或 /help - 显示帮助信息

管理员命令：
- /管理命令 - 显示管理员功能菜单
- /备份 - 获取备份文件列表
- /创建备份 - 手动创建备份
- /执行 <世界> <命令> - 执行游戏命令
- /回档 <天数> - 回档指定天数 (1-5天)
- /重置世界 [世界名称] - 重置世界 (默认Master)
- /聊天历史 [世界名] [行数] - 获取聊天历史 (默认集群，默认50行)
- /聊天统计 - 获取聊天历史统计信息

消息互通功能：
- 消息互通 或 开启互通 - 开启游戏内消息与QQ消息互通
- 关闭互通 - 关闭消息互通功能
- 互通状态 - 查看当前互通状态
- 最新消息 - 获取游戏内最新消息

配置说明：
在 .env 文件中配置以下环境变量：
- DMP_BASE_URL: DMP服务器地址
- DMP_TOKEN: JWT认证令牌
- DEFAULT_CLUSTER: 默认集群名称""",
    
    type="application",
    homepage="https://github.com/uitok/nonebot-plugin-dst-qq",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

# 延迟配置获取，避免在导入时初始化 NoneBot
config = None

def get_config():
    """获取插件配置"""
    global config
    if config is None:
        config = get_plugin_config(Config)
    return config

# 延迟加载子插件，避免导入时的问题
def load_sub_plugins():
    """延迟加载子插件"""
    try:
        # 使用绝对路径加载子插件
        plugins_dir = Path(__file__).parent / "plugins"
        if plugins_dir.exists():
            # 将插件目录添加到 Python 路径
            import sys
            if str(plugins_dir) not in sys.path:
                sys.path.insert(0, str(plugins_dir))
            
            # 导入子插件模块
            import dmp_api
            import dmp_advanced
            import message_exchange
            
            return True
    except Exception as e:
        print(f"警告: 子插件加载失败: {e}")
        return False

# 延迟注册启动事件，避免导入时的问题
def register_startup_event():
    """注册启动事件"""
    try:
        driver = nonebot.get_driver()
        
        @driver.on_startup
        async def _load_plugins():
            """在 NoneBot 启动时加载子插件"""
            load_sub_plugins()
            
    except ValueError:
        # NoneBot 未初始化时，跳过注册
        pass

# 尝试注册启动事件
register_startup_event()

