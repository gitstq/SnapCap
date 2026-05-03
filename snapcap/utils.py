"""
工具函数模块

提供文件大小格式化、图片格式转换、时间戳生成、终端彩色输出、文件哈希计算等通用工具函数。
"""

import hashlib
import os
import platform
import time
from datetime import datetime
from typing import Optional, Tuple


class Colors:
    """ANSI 终端颜色码常量类。

    提供常用的终端颜色和样式常量，用于彩色终端输出。
    """

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"


def colored(text: str, color: str) -> str:
    """为文本添加ANSI颜色。

    Args:
        text: 需要着色的文本。
        color: ANSI颜色码，使用Colors类中的常量。

    Returns:
        添加了颜色码的文本字符串。
    """
    return f"{color}{text}{Colors.RESET}"


def print_success(message: str) -> None:
    """打印成功信息（绿色）。

    Args:
        message: 成功信息文本。
    """
    print(f"{Colors.GREEN}[OK]{Colors.RESET} {message}")


def print_error(message: str) -> None:
    """打印错误信息（红色）。

    Args:
        message: 错误信息文本。
    """
    print(f"{Colors.RED}[ERROR]{Colors.RESET} {message}")


def print_warning(message: str) -> None:
    """打印警告信息（黄色）。

    Args:
        message: 警告信息文本。
    """
    print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {message}")


def print_info(message: str) -> None:
    """打印信息提示（蓝色）。

    Args:
        message: 信息文本。
    """
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} {message}")


def generate_timestamp() -> str:
    """生成当前时间戳字符串。

    格式为 YYYYMMDD_HHMMSS，用于文件命名。

    Returns:
        时间戳字符串，例如 '20240101_120000'。
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def generate_unique_filename(prefix: str = "screenshot", extension: str = ".png") -> str:
    """生成唯一的文件名。

    Args:
        prefix: 文件名前缀，默认为 'screenshot'。
        extension: 文件扩展名，默认为 '.png'。

    Returns:
        唯一文件名字符串，格式为 'prefix_YYYYMMDD_HHMMSS.ext'。
    """
    return f"{prefix}_{generate_timestamp()}{extension}"


def format_file_size(size_bytes: int) -> str:
    """将文件大小（字节）格式化为人类可读的字符串。

    Args:
        size_bytes: 文件大小，单位为字节。

    Returns:
        格式化后的文件大小字符串，例如 '1.5 MB'。
    """
    if size_bytes < 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)

    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1

    return f"{size:.1f} {units[unit_index]}"


def get_file_size(filepath: str) -> str:
    """获取文件大小并格式化。

    Args:
        filepath: 文件路径。

    Returns:
        格式化后的文件大小字符串。如果文件不存在则返回 'N/A'。
    """
    if not os.path.exists(filepath):
        return "N/A"
    return format_file_size(os.path.getsize(filepath))


def calculate_file_hash(filepath: str, algorithm: str = "md5") -> str:
    """计算文件的哈希值。

    Args:
        filepath: 文件路径。
        algorithm: 哈希算法，支持 'md5'、'sha1'、'sha256'，默认为 'md5'。

    Returns:
        文件的十六进制哈希值字符串。

    Raises:
        FileNotFoundError: 当文件不存在时。
        ValueError: 当哈希算法不支持时。
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件不存在: {filepath}")

    supported_algorithms = {"md5", "sha1", "sha256"}
    if algorithm not in supported_algorithms:
        raise ValueError(f"不支持的哈希算法: {algorithm}，支持: {supported_algorithms}")

    hash_func = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def convert_image_format(
    input_path: str,
    output_path: str,
    quality: int = 85,
) -> bool:
    """转换图片格式。

    支持在 PNG、JPEG、BMP、WEBP 等格式之间转换。

    Args:
        input_path: 输入图片路径。
        output_path: 输出图片路径（扩展名决定输出格式）。
        quality: 输出质量（1-100），仅对 JPEG 有效，默认为 85。

    Returns:
        转换成功返回 True，失败返回 False。
    """
    try:
        from PIL import Image

        img = Image.open(input_path)
        output_ext = os.path.splitext(output_path)[1].lower()

        save_kwargs = {}
        if output_ext in (".jpg", ".jpeg"):
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            save_kwargs["quality"] = quality
        elif output_ext == ".webp":
            save_kwargs["quality"] = quality

        img.save(output_path, **save_kwargs)
        return True
    except Exception:
        return False


def ensure_directory(filepath: str) -> str:
    """确保文件所在的目录存在，如果不存在则创建。

    Args:
        filepath: 文件路径。

    Returns:
        文件所在的目录路径。
    """
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    return directory


def get_system_info() -> dict:
    """获取当前系统信息。

    Returns:
        包含操作系统、平台、Python版本等信息的字典。
    """
    return {
        "os": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
    }


def is_gui_available() -> bool:
    """检测当前环境是否有GUI可用。

    Returns:
        如果有GUI可用返回 True，否则返回 False。
    """
    system = platform.system()
    if system == "Linux":
        display = os.environ.get("DISPLAY", "")
        wayland = os.environ.get("WAYLAND_DISPLAY", "")
        return bool(display or wayland)
    return True  # Windows 和 macOS 通常有GUI


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """截断过长的文本。

    Args:
        text: 原始文本。
        max_length: 最大长度，默认为 50。
        suffix: 截断后添加的后缀，默认为 '...'。

    Returns:
        截断后的文本。
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix
