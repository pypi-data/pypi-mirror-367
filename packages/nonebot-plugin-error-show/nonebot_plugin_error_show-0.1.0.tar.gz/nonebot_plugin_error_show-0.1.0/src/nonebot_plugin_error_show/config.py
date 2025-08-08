from typing import Optional
from pathlib import Path

from nonebot import get_driver, get_plugin_config
from pydantic import BaseModel
import nonebot_plugin_localstore as localstore


class Config(BaseModel):
    e_bot_link: Optional[str] = None        # BOT 好友链接
    e_bot_group_link: Optional[str] = None  # BOT 用户交流群链接
    e_bot_id: Optional[str|int] = None          # BOT 账号
    e_bot_group_id: Optional[str|int] = None    # BOT 用户交流群号


# 配置加载
plugin_config: Config = get_plugin_config(Config)
global_config = get_driver().config

# 全局名称
NICKNAME: str = next(iter(global_config.nickname), "机器人")

# Data目录
DATA_DIR = localstore.get_plugin_data_dir()
PLUGIN_PATH = Path(__file__).resolve().parent
