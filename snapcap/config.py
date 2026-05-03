"""
配置管理模块

管理 SnapCap 的全局配置，包括截图保存路径、图床提供商、API密钥、标注样式等。
配置文件以 JSON 格式存储在 ~/.snapcap/config.json。
"""

import json
import os
import shutil
from typing import Any, Dict, Optional


DEFAULT_CONFIG = {
    "capture": {
        "default_mode": "fullscreen",
        "default_output": "./screenshots/",
        "format": "png",
        "delay": 0,
    },
    "annotate": {
        "rect_color": "#FF0000",
        "rect_width": 3,
        "arrow_color": "#FF0000",
        "arrow_width": 2,
        "text_color": "#FFFFFF",
        "text_size": 24,
        "text_bg_color": "#000000",
        "mosaic_size": 10,
        "highlight_color": "#FFFF00",
        "highlight_opacity": 0.3,
        "number_color": "#FF0000",
        "number_size": 20,
    },
    "upload": {
        "default_provider": "fileio",
        "imgbb_api_key": "",
        "custom_endpoint": "",
        "custom_field_name": "file",
        "custom_headers": {},
        "output_format": "url",
    },
    "clipboard": {
        "auto_copy": True,
    },
    "history": {
        "enabled": True,
        "max_entries": 100,
        "file": "~/.snapcap/history.json",
    },
}


class ConfigManager:
    """SnapCap 配置管理器。

    负责加载、保存、读取和修改配置。配置文件存储在用户主目录下的
    ~/.snapcap/config.json 中。

    Attributes:
        config_dir: 配置目录路径。
        config_path: 配置文件路径。
        config: 当前配置字典。
    """

    def __init__(self, config_path: Optional[str] = None) -> None:
        """初始化配置管理器。

        Args:
            config_path: 自定义配置文件路径。如果为 None，使用默认路径
                         ~/.snapcap/config.json。
        """
        if config_path:
            self.config_path = os.path.expanduser(config_path)
            self.config_dir = os.path.dirname(self.config_path)
        else:
            self.config_dir = os.path.expanduser("~/.snapcap")
            self.config_path = os.path.join(self.config_dir, "config.json")

        self.config: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """从配置文件加载配置。

        如果配置文件不存在，则创建默认配置文件。
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                # 合并默认配置中缺失的键
                self.config = self._merge_with_defaults(self.config)
            except (json.JSONDecodeError, IOError) as e:
                self.config = self._deep_copy(DEFAULT_CONFIG)
        else:
            self.config = self._deep_copy(DEFAULT_CONFIG)
            self.save()

    def _deep_copy(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """深拷贝字典。

        Args:
            d: 源字典。

        Returns:
            深拷贝后的字典。
        """
        return json.loads(json.dumps(d))

    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """将用户配置与默认配置合并，确保所有键都存在。

        Args:
            config: 用户配置字典。

        Returns:
            合并后的完整配置字典。
        """
        result = self._deep_copy(DEFAULT_CONFIG)

        def _merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
            for key, value in override.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    base[key] = _merge(base[key], value)
                else:
                    base[key] = value
            return base

        return _merge(result, config)

    def save(self) -> None:
        """保存当前配置到配置文件。

        如果配置目录不存在，会自动创建。

        Raises:
            IOError: 当保存文件失败时。
        """
        os.makedirs(self.config_dir, exist_ok=True)
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except IOError as e:
            raise IOError(f"无法保存配置文件: {e}")

    def get(self, key_path: str, default: Any = None) -> Any:
        """使用点号分隔的路径获取配置值。

        例如: get('capture.default_mode') 返回 'fullscreen'。

        Args:
            key_path: 点号分隔的配置键路径。
            default: 键不存在时的默认返回值。

        Returns:
            配置值，如果键不存在则返回默认值。
        """
        keys = key_path.split(".")
        value: Any = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, key_path: str, value: Any) -> None:
        """使用点号分隔的路径设置配置值。

        例如: set('capture.default_mode', 'region')。

        Args:
            key_path: 点号分隔的配置键路径。
            value: 要设置的值。
        """
        keys = key_path.split(".")
        config = self.config
        for key in keys[:-1]:
            if key not in config or not isinstance(config[key], dict):
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self.save()

    def show(self) -> str:
        """以格式化的字符串形式展示当前配置。

        Returns:
            格式化的配置字符串。
        """
        return json.dumps(self.config, indent=4, ensure_ascii=False)

    def export_config(self, output_path: str) -> None:
        """导出配置到指定文件。

        Args:
            output_path: 导出文件路径。

        Raises:
            IOError: 当导出失败时。
        """
        output_path = os.path.expanduser(output_path)
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def import_config(self, input_path: str) -> None:
        """从指定文件导入配置。

        导入后会与默认配置合并，确保所有键都存在。

        Args:
            input_path: 导入文件路径。

        Raises:
            FileNotFoundError: 当导入文件不存在时。
            json.JSONDecodeError: 当文件不是有效的 JSON 时。
        """
        input_path = os.path.expanduser(input_path)
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"配置文件不存在: {input_path}")

        with open(input_path, "r", encoding="utf-8") as f:
            imported_config = json.load(f)

        self.config = self._merge_with_defaults(imported_config)
        self.save()

    def reset(self) -> None:
        """重置所有配置为默认值。"""
        self.config = self._deep_copy(DEFAULT_CONFIG)
        self.save()

    def get_history_path(self) -> str:
        """获取历史记录文件路径。

        Returns:
            历史记录文件的绝对路径。
        """
        history_file = self.get("history.file", "~/.snapcap/history.json")
        return os.path.expanduser(history_file)
