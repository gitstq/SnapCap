"""
剪贴板操作模块

提供跨平台的剪贴板操作功能，包括复制图片和文本到剪贴板。
零外部依赖实现，仅使用 Python 标准库和系统命令。
"""

import os
import platform
import subprocess
import tempfile
from typing import Optional


class ClipboardError(Exception):
    """剪贴板操作异常。"""

    pass


def copy_text(text: str) -> bool:
    """复制文本到系统剪贴板。

    支持跨平台操作：Windows (clip)、macOS (pbcopy)、Linux (xclip/wl-copy)。

    Args:
        text: 要复制的文本字符串。

    Returns:
        复制成功返回 True，失败返回 False。
    """
    if not text:
        return False

    system = platform.system()

    try:
        if system == "Windows":
            process = subprocess.Popen(
                ["clip"],
                stdin=subprocess.PIPE,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW,  # type: ignore
            )
            process.communicate(text.encode("utf-8"))
            return process.returncode == 0

        elif system == "Darwin":
            process = subprocess.Popen(
                ["pbcopy"],
                stdin=subprocess.PIPE,
            )
            process.communicate(text.encode("utf-8"))
            return process.returncode == 0

        else:  # Linux
            # 优先尝试 Wayland
            if os.environ.get("WAYLAND_DISPLAY"):
                process = subprocess.Popen(
                    ["wl-copy"],
                    stdin=subprocess.PIPE,
                )
                process.communicate(text.encode("utf-8"))
                if process.returncode == 0:
                    return True

            # 回退到 X11
            process = subprocess.Popen(
                ["xclip", "-selection", "clipboard"],
                stdin=subprocess.PIPE,
            )
            process.communicate(text.encode("utf-8"))
            return process.returncode == 0

    except (FileNotFoundError, subprocess.SubprocessError, OSError):
        return False


def paste_text() -> Optional[str]:
    """从系统剪贴板粘贴文本。

    支持跨平台操作：Windows (powershell)、macOS (pbpaste)、Linux (xclip/wl-paste)。

    Returns:
        剪贴板中的文本内容，失败返回 None。
    """
    system = platform.system()

    try:
        if system == "Windows":
            process = subprocess.Popen(
                ["powershell", "-command", "Get-Clipboard"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,  # type: ignore
            )
            stdout, _ = process.communicate()
            return stdout.decode("utf-8").strip() if stdout else None

        elif system == "Darwin":
            process = subprocess.Popen(
                ["pbpaste"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, _ = process.communicate()
            return stdout.decode("utf-8").strip() if stdout else None

        else:  # Linux
            # 优先尝试 Wayland
            if os.environ.get("WAYLAND_DISPLAY"):
                process = subprocess.Popen(
                    ["wl-paste"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                stdout, _ = process.communicate()
                if process.returncode == 0 and stdout:
                    return stdout.decode("utf-8").strip()

            # 回退到 X11
            process = subprocess.Popen(
                ["xclip", "-selection", "clipboard", "-o"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, _ = process.communicate()
            return stdout.decode("utf-8").strip() if stdout else None

    except (FileNotFoundError, subprocess.SubprocessError, OSError):
        return None


def copy_image(image_path: str) -> bool:
    """复制图片到系统剪贴板。

    支持跨平台操作：
    - Windows: 使用 PowerShell
    - macOS: 使用 osascript
    - Linux: 使用 xclip (X11) 或 wl-copy (Wayland)

    Args:
        image_path: 图片文件的绝对路径。

    Returns:
        复制成功返回 True，失败返回 False。

    Raises:
        FileNotFoundError: 当图片文件不存在时。
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件不存在: {image_path}")

    abs_path = os.path.abspath(image_path)
    system = platform.system()

    try:
        if system == "Windows":
            return _copy_image_windows(abs_path)
        elif system == "Darwin":
            return _copy_image_macos(abs_path)
        else:
            return _copy_image_linux(abs_path)
    except (subprocess.SubprocessError, OSError) as e:
        raise ClipboardError(f"复制图片到剪贴板失败: {e}")


def _copy_image_windows(image_path: str) -> bool:
    """在 Windows 上复制图片到剪贴板。

    Args:
        image_path: 图片文件路径。

    Returns:
        成功返回 True，失败返回 False。
    """
    ps_script = f"""
Add-Type -AssemblyName System.Windows.Forms
$img = [System.Drawing.Image]::FromFile('{image_path}')
[System.Windows.Forms.Clipboard]::SetImage($img)
$img.Dispose()
"""
    process = subprocess.Popen(
        ["powershell", "-command", ps_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW,  # type: ignore
    )
    _, stderr = process.communicate()
    return process.returncode == 0


def _copy_image_macos(image_path: str) -> bool:
    """在 macOS 上复制图片到剪贴板。

    Args:
        image_path: 图片文件路径。

    Returns:
        成功返回 True，失败返回 False。
    """
    script = f'set the clipboard to (read POSIX file "{image_path}" as «class PNGf»)'
    process = subprocess.Popen(
        ["osascript", "-e", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    _, stderr = process.communicate()
    return process.returncode == 0


def _copy_image_linux(image_path: str) -> bool:
    """在 Linux 上复制图片到剪贴板。

    优先使用 xclip (X11)，回退到 wl-copy (Wayland)。

    Args:
        image_path: 图片文件路径。

    Returns:
        成功返回 True，失败返回 False。
    """
    # 尝试 X11 xclip
    try:
        process = subprocess.Popen(
            ["xclip", "-selection", "clipboard", "-t", "image/png", "-i", image_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        process.communicate()
        if process.returncode == 0:
            return True
    except (FileNotFoundError, subprocess.SubprocessError):
        pass

    # 尝试 Wayland wl-copy
    try:
        process = subprocess.Popen(
            ["wl-copy", "--type", "image/png", image_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        process.communicate()
        if process.returncode == 0:
            return True
    except (FileNotFoundError, subprocess.SubprocessError):
        pass

    return False


def save_clipboard_image(output_path: str) -> bool:
    """从剪贴板保存图片到文件。

    Args:
        output_path: 输出文件路径。

    Returns:
        成功返回 True，失败返回 False。
    """
    system = platform.system()

    try:
        if system == "Windows":
            ps_script = f"""
Add-Type -AssemblyName System.Windows.Forms
$img = [System.Windows.Forms.Clipboard]::GetImage()
if ($img) {{
    $img.Save('{output_path}', [System.Drawing.Imaging.ImageFormat]::Png)
    $img.Dispose()
}}
"""
            process = subprocess.Popen(
                ["powershell", "-command", ps_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,  # type: ignore
            )
            process.communicate()
            return process.returncode == 0 and os.path.exists(output_path)

        elif system == "Darwin":
            script = f"""
set png_data to the clipboard as «class PNGf»
set fp to open for access POSIX file "{output_path}" with write permission
write png_data to fp
close access fp
"""
            process = subprocess.Popen(
                ["osascript", "-e", script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            process.communicate()
            return process.returncode == 0 and os.path.exists(output_path)

        else:  # Linux
            # 尝试 xclip
            try:
                with open(output_path, "wb") as f:
                    process = subprocess.Popen(
                        ["xclip", "-selection", "clipboard", "-t", "image/png", "-o"],
                        stdout=f,
                        stderr=subprocess.PIPE,
                    )
                    process.communicate()
                    if process.returncode == 0:
                        return True
            except (FileNotFoundError, subprocess.SubprocessError):
                pass

            # 尝试 wl-paste
            try:
                with open(output_path, "wb") as f:
                    process = subprocess.Popen(
                        ["wl-paste", "--type", "image/png"],
                        stdout=f,
                        stderr=subprocess.PIPE,
                    )
                    process.communicate()
                    if process.returncode == 0:
                        return True
            except (FileNotFoundError, subprocess.SubprocessError):
                pass

            return False

    except (subprocess.SubprocessError, OSError):
        return False


def check_clipboard_support() -> dict:
    """检查当前系统的剪贴板支持情况。

    Returns:
        包含支持情况的字典，键为功能名称，值为是否支持。
    """
    system = platform.system()
    support = {
        "copy_text": False,
        "paste_text": False,
        "copy_image": False,
        "save_image": False,
    }

    # 检查文本复制
    try:
        support["copy_text"] = copy_text("test")
    except Exception:
        pass

    # 检查文本粘贴
    try:
        support["paste_text"] = paste_text() is not None
    except Exception:
        pass

    # 检查图片操作（仅检查工具是否可用）
    if system == "Windows":
        support["copy_image"] = True
        support["save_image"] = True
    elif system == "Darwin":
        support["copy_image"] = shutil.which("osascript") is not None
        support["save_image"] = shutil.which("osascript") is not None
    else:
        support["copy_image"] = (
            shutil.which("xclip") is not None or shutil.which("wl-copy") is not None
        )
        support["save_image"] = (
            shutil.which("xclip") is not None or shutil.which("wl-paste") is not None
        )

    return support
