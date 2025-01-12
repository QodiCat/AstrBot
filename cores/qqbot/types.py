from model.platform.qq_official import NakuruGuildMessage
from model.provider.provider import Provider as LLMProvider
from model.platform._platfrom import Platform
from nakuru import (
    GroupMessage,
    FriendMessage,
    GuildMessage,
)
from typing import Union, List, ClassVar
from types import ModuleType
from enum import Enum
from dataclasses import dataclass

class PluginType(Enum):
    PLATFORM = 'platfrom' # 平台类插件。
    LLM = 'llm' # 大语言模型类插件
    COMMON = 'common' # 其他插件

@dataclass
class PluginMetadata:
    '''
    插件的元数据。
    '''
    # required
    plugin_name: str
    plugin_type: PluginType
    author: str # 插件作者
    desc: str # 插件简介
    version: str # 插件版本
    
    # optional
    repo: str = None # 插件仓库地址
    
    def __str__(self) -> str:
        return f"PluginMetadata({self.plugin_name}, {self.plugin_type}, {self.desc}, {self.version}, {self.repo})"
    
@dataclass
class RegisteredPlugin:
    '''
    注册在 AstrBot 中的插件。
    '''
    metadata: PluginMetadata
    plugin_instance: object
    module_path: str
    module: ModuleType
    root_dir_name: str

    def __str__(self) -> str:
        return f"RegisteredPlugin({self.metadata}, {self.module_path}, {self.root_dir_name})"
    
RegisteredPlugins = List[RegisteredPlugin]

@dataclass
class RegisteredPlatform:
    '''
    注册在 AstrBot 中的平台。平台应当实现 Platform 接口。
    '''
    platform_name: str
    platform_instance: Platform
    origin: str = None # 注册来源
    
@dataclass
class RegisteredLLM:
    '''
    注册在 AstrBot 中的大语言模型调用。大语言模型应当实现 LLMProvider 接口。
    '''
    llm_name: str
    llm_instance: LLMProvider
    origin: str = None # 注册来源
    
class GlobalObject:
    '''
    存放一些公用的数据，用于在不同模块(如core与command)之间传递
    '''
    version: str # 机器人版本
    nick: str # 用户定义的机器人的别名
    base_config: dict # config.json 中导出的配置
    cached_plugins: List[RegisteredPlugin] # 加载的插件
    platforms: List[RegisteredPlatform]
    llms: List[RegisteredLLM]
    
    web_search: bool # 是否开启了网页搜索
    reply_prefix: str # 回复前缀
    unique_session: bool # 是否开启了独立会话
    cnt_total: int # 总消息数
    default_personality: dict
    dashboard_data = None
    logger: None
    
    def __init__(self):
        self.nick = None # gocq 的昵称
        self.base_config = None # config.yaml
        self.cached_plugins = [] # 缓存的插件
        self.web_search = False # 是否开启了网页搜索
        self.reply_prefix = None
        self.unique_session = False
        self.cnt_total = 0
        self.platforms = []
        self.llms = []
        self.default_personality = None
        self.dashboard_data = None
        self.stat = {}

class AstrMessageEvent():
    '''
    消息事件。
    '''
    context: GlobalObject # 一些公用数据
    message_str: str # 纯消息字符串
    message_obj: Union[GroupMessage, FriendMessage, GuildMessage, NakuruGuildMessage] # 消息对象
    platform: RegisteredPlatform # 来源平台
    role: str # 基本身份。`admin` 或 `member`
    session_id: int # 会话 id

    def __init__(self, 
                 message_str: str, 
                 message_obj: Union[GroupMessage, FriendMessage, GuildMessage, NakuruGuildMessage], 
                 platform: RegisteredPlatform, 
                 role: str,
                 context: GlobalObject,
                 session_id: str = None):
        self.context = context
        self.message_str = message_str
        self.message_obj = message_obj
        self.platform = platform
        self.role = role
        self.session_id = session_id
        
class CommandResult():
    '''
    用于在Command中返回多个值
    '''
    def __init__(self, hit: bool, success: bool, message_chain: list, command_name: str = "unknown_command") -> None:
        self.hit = hit
        self.success = success
        self.message_chain = message_chain
        self.command_name = command_name
        
    def _result_tuple(self):
        return (self.success, self.message_chain, self.command_name)