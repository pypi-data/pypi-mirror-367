import warnings
from collections.abc import Callable

import typing_extensions
from nonebot import logger

from .chatmanager import chat_manager
from .config import Config, ConfigManager, config_manager
from .utils.admin import send_to_admin
from .utils.libchat import (
    ModelAdapter,
    adapter_class,
    get_chat,
    protocols_adapters,
    tools_caller,
)
from .utils.tokenizer import Tokenizer, hybrid_token_count

__all__ = [
    "ConfigManager",
    "Tokenizer",
    "config_manager",
    "hybrid_token_count",
    "tools_caller",
]


class Adapter:
    """用于处理Adapter注册的类"""

    @typing_extensions.deprecated(
        "请使用register_adapter_class方法",
        category=None,
    )
    def register_adapter(self, func: Callable, protocol: str):
        """注册一个适配器。

        Args:
            func (Callable): 适配器函数
            protocol (str): 协议

        Raises:
            ValueError: 这个协议的适配器已经注册了。
        """
        warnings.warn(
            "请使用Adapter.register_adapter()注册适配器，请使用新的Adapter规范",
            DeprecationWarning,
        )
        if protocol in protocols_adapters and not config_manager.config_dir:
            raise ValueError("协议适配器已存在")
        else:
            protocols_adapters[protocol] = func

    def register_adapter_class(self, adapter: type[ModelAdapter]) -> None:
        """注册一个适配器类。

        Args:
            adapter (type[ModelAdapter]): 适配器类

        Raises:
            ValueError: 这个适配器类已经注册了。
        """
        if adapter.get_adapter_protocol() in adapter_class:
            raise ValueError(
                f"这个适配器类已经注册了：{adapter.get_adapter_protocol()}"
            )
        adapter_class[adapter.get_adapter_protocol()] = adapter

    @typing_extensions.deprecated(
        "请使用 get_adapter_class() 方法获取适配器。", category=None
    )
    def get_adapter(self, protocol: str) -> Callable:
        """获取适配器方法。

        Args:
            protocol (str): 协议

        Raises:
            ValueError: 不存在

        Returns:
            Callable: 返回的函数
        """
        warnings.warn(
            "请使用 get_adapter_protocol() 方法获取协议适配器", DeprecationWarning
        )
        if protocol not in protocols_adapters:
            raise ValueError("协议适配器不存在")
        return protocols_adapters[protocol]

    def get_adapter_class(self, protocol: str) -> type[ModelAdapter]:
        if protocol not in adapter_class:
            raise ValueError("协议适配器不存在")
        return adapter_class[protocol]

    def get_adapter_classes(self) -> dict[str, type[ModelAdapter]]:
        return adapter_class

    @typing_extensions.deprecated(
        "请使用 get_adapters_classes() 方法获取适配器。", category=None
    )
    def get_adapters(self) -> dict[str, Callable]:
        """获取适配器方法

        Returns:
            dict[str,Callable]: 包含适配器与协议的字典
        """
        warnings.warn("请使用get_adapters()方法", DeprecationWarning)
        return protocols_adapters

    @property
    @typing_extensions.deprecated("请使用 adapter_classes 获取适配器。", category=None)
    def adapters(self) -> dict[str, Callable]:
        """获取适配器方法

        Returns:
            dict[str,Callable]: 包含适配器与协议的字典
        """
        warnings.warn("请使用adapter_classes属性", DeprecationWarning)
        return protocols_adapters

    @property
    def adapter_classes(self) -> dict[str, type[ModelAdapter]]:
        """获取适配器类方法

        Returns:
            dict[str,Type[ModelAdapter]]: 适配器类字典
        """
        return adapter_class


class Menu:
    """
    Menu 类用于通过注册菜单项来构建菜单。
    """

    def reg_menu(self, cmd_name: str, describe: str, args: str = "") -> "Menu":
        """
        注册一个新的菜单项。

        参数:
        - cmd_name (str): 菜单项的命令名称。
        - describe (str): 菜单项的描述。

        返回:
        - Menu: 返回 Menu 类的实例，支持方法链式调用。
        """
        chat_manager.menu_msg += f"/{cmd_name} {args} 说明：{describe} \n"
        return self

    @property
    def menu(self) -> str:
        """
        获取菜单项。
        """
        return chat_manager.menu_msg


class Admin:
    """
    管理员管理类，负责处理与管理员相关的操作，如发送消息、错误处理和管理员权限管理。
    """

    config: Config

    def __init__(self):
        """
        构造函数
        """
        self.config = config_manager.ins_config

    async def send_with(self, msg: str) -> "Admin":
        """
        异步发送消息给管理员。

        参数:
        - msg (str): 要发送的消息内容。

        返回:
        - Admin: 返回Admin实例，支持链式调用。
        """
        await send_to_admin(msg)
        return self

    async def send_error(self, msg: str) -> "Admin":
        """
        异步发送错误消息给管理员，并记录错误日志。

        参数:
        - msg (str): 要发送的错误消息内容。

        返回:
        - Admin: 返回Admin实例，支持链式调用。
        """
        logger.error(msg)
        await send_to_admin(msg)
        return self

    def is_admin(self, user_id: str) -> bool:
        """
        检查用户是否是管理员。

        参数:
        - user_id (str): 用户ID。

        返回:
        - bool: 用户是否是管理员。
        """
        return int(user_id) in self.config.admin.admins

    def add_admin(self, user_id: int) -> "Admin":
        """
        添加新的管理员用户ID到配置中。

        参数:
        - user_id (int): 要添加的用户ID。

        返回:
        - Admin: 返回Admin实例，支持链式调用。
        """
        self.config.admin.admins.append(user_id)
        return self._save_config_to_toml()

    def set_admin_group(self, group_id: int) -> "Admin":
        """
        设置管理员组ID。

        参数:
        - group_id (int): 管理员组ID。

        返回:
        - Admin: 返回Admin实例，支持链式调用。
        """
        self.config.admin.admin_group = group_id
        return self._save_config_to_toml()

    def _save_config_to_toml(self):
        self.config.save_to_toml(config_manager.toml_config)
        self.config = config_manager.ins_config
        return self


class Chat:
    """
    Chat 类用于处理与LLM相关操作，如获取消息。
    """

    config: Config

    def __init__(self):
        """
        构造函数
        """
        self.config = config_manager.ins_config

    async def get_msg(self, prompt: str, message: list):
        """
        获取LLM响应

        :param prompt[str]: 提示词
        :param message[list]: 消息列表
        """

        message.insert(0, {"role": "assistant", "content": prompt})
        return await self.get_msg_on_list(message)

    async def get_msg_on_list(self, message: list):
        """
        获取LLM响应

        :param message[list]: 消息列表
        """

        return await get_chat(messages=message)
