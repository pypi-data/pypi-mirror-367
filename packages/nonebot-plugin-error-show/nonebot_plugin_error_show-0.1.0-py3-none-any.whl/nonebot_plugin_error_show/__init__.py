import traceback
from typing import Optional
from datetime import datetime

from nonebot import logger, require, get_driver, on_command
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot.message import run_postprocessor
from nonebot.adapters import Event, Bot
from nonebot.exception import MatcherException, FinishedException

require("nonebot_plugin_alconna")
require("nonebot_plugin_localstore")
require("nonebot_plugin_htmlrender")

from .config import Config, plugin_config, DATA_DIR, PLUGIN_PATH, NICKNAME
from .utils import generate_qr_code

from nonebot_plugin_alconna import UniMessage
from nonebot_plugin_htmlrender import template_to_pic

__plugin_meta__ = PluginMetadata(
    name="自动报错",
    description="nonebot报错输出插件",
    usage="自动输出报错",
    type="application",
    homepage="https://github.com/zifox666/nonebot-plugin-error-show",
    config=Config,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={"author": "zifox666 <zifox666@mail.com>"},
)

driver = get_driver()
bot_qrcode_path, group_qrcode_path = None, None


@driver.on_startup
async def _startup():
    global bot_qrcode_path, group_qrcode_path
    if plugin_config.e_bot_link:
        bot_qrcode_path = generate_qr_code(
            data=str(plugin_config.e_bot_link),
            path=DATA_DIR / "img",
            filename="e_bot_link.png"
        )

    if plugin_config.e_bot_group_link:
         group_qrcode_path = generate_qr_code(
            data=str(plugin_config.e_bot_group_link),
            path=DATA_DIR / "img",
            filename="e_bot_group_link.png"
        )

    logger.info(f"二维码生成路径:\n机器人：{bot_qrcode_path}\n交流群：{group_qrcode_path}")


async def render_error(event: Event, exception: Exception):
    if isinstance(exception, (MatcherException, FinishedException)):
        return None

    error_str = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))

    templates_path = PLUGIN_PATH / "templates"
    error_json = {
        "e": str(exception),
        "event": str(event),
        "traceback": error_str,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "bot_link": bot_qrcode_path,
        "group_link": group_qrcode_path,
        "bot_id": plugin_config.e_bot_id,
        "group_id": plugin_config.e_bot_group_id,
        "nickname": NICKNAME
    }

    image = await template_to_pic(
        template_path=templates_path,
        template_name="error.html.jinja2",
        templates=error_json,
        pages={
            "viewport": {"width": 1080, "height": 100},
            "base_url": f"file://{templates_path}",
        },
    )

    return image



@run_postprocessor
async def handle_exception(bot: Bot, event: Event, exception: Optional[Exception]):
    if exception:
        await UniMessage.image(
            raw=await render_error(event, exception)
        ).send(target=event, bot=bot)
        logger.error(f"发生错误：{exception}")

