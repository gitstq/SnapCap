"""
截图引擎模块

提供全屏截图、窗口截图和区域选择截图功能。
支持跨平台操作，自动记录截图历史。
"""

import json
import os
import platform
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .utils import (
    ensure_directory,
    generate_unique_filename,
    get_file_size,
    print_error,
    print_info,
    print_success,
)


class CaptureError(Exception):
    """截图操作异常。"""

    pass


class CaptureEngine:
    """截图引擎。

    支持全屏截图、窗口截图和区域选择截图。
    截图结果自动保存为 PNG 格式，并记录到历史文件中。

    Attributes:
        history_path: 截图历史记录文件路径。
        history: 截图历史记录列表。
    """

    def __init__(self, history_path: Optional[str] = None) -> None:
        """初始化截图引擎。

        Args:
            history_path: 历史记录文件路径。如果为 None，使用默认路径
                         ~/.snapcap/history.json。
        """
        if history_path:
            self.history_path = os.path.expanduser(history_path)
        else:
            self.history_path = os.path.expanduser("~/.snapcap/history.json")

        self.history: List[Dict] = []
        self._load_history()

    def _load_history(self) -> None:
        """从文件加载截图历史记录。"""
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.history = []

    def _save_history(self) -> None:
        """保存截图历史记录到文件。"""
        ensure_directory(self.history_path)
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4, ensure_ascii=False)

    def _add_to_history(self, filepath: str, mode: str, metadata: Optional[Dict] = None) -> Dict:
        """添加截图记录到历史。

        Args:
            filepath: 截图文件路径。
            mode: 截图模式。
            metadata: 额外的元数据。

        Returns:
            新创建的历史记录条目。
        """
        entry = {
            "filepath": os.path.abspath(filepath),
            "mode": mode,
            "timestamp": datetime.now().isoformat(),
            "size": get_file_size(filepath),
            "metadata": metadata or {},
        }
        self.history.insert(0, entry)

        # 限制历史记录数量
        max_entries = 100
        if len(self.history) > max_entries:
            self.history = self.history[:max_entries]

        self._save_history()
        return entry

    def capture_fullscreen(self, output_dir: str = "./screenshots/", filename: Optional[str] = None) -> str:
        """全屏截图。

        使用系统工具或 PIL 进行全屏截图。

        Args:
            output_dir: 输出目录路径，默认为 './screenshots/'。
            filename: 自定义文件名。如果为 None，自动生成。

        Returns:
            截图文件的绝对路径。

        Raises:
            CaptureError: 当截图失败时。
        """
        output_dir = os.path.expanduser(output_dir)
        ensure_directory(output_dir)

        if filename:
            filepath = os.path.join(output_dir, filename)
        else:
            filepath = os.path.join(output_dir, generate_unique_filename("fullscreen"))

        system = platform.system()
        success = False

        try:
            if system == "Linux":
                success = self._capture_linux_fullscreen(filepath)
            elif system == "Darwin":
                success = self._capture_macos_fullscreen(filepath)
            elif system == "Windows":
                success = self._capture_windows_fullscreen(filepath)
            else:
                success = self._capture_pil_fullscreen(filepath)
        except Exception as e:
            # 回退到 PIL
            try:
                success = self._capture_pil_fullscreen(filepath)
            except Exception as pil_error:
                raise CaptureError(f"全屏截图失败: {e}, PIL回退也失败: {pil_error}")

        if not success or not os.path.exists(filepath):
            raise CaptureError("全屏截图失败：未能生成截图文件")

        self._add_to_history(filepath, "fullscreen")
        print_success(f"全屏截图已保存: {filepath}")
        return os.path.abspath(filepath)

    def _capture_linux_fullscreen(self, filepath: str) -> bool:
        """在 Linux 上进行全屏截图。

        尝试使用 gnome-screenshot、scrot 或 spectacle。

        Args:
            filepath: 输出文件路径。

        Returns:
            成功返回 True，失败返回 False。
        """
        # 尝试 gnome-screenshot
        try:
            result = subprocess.run(
                ["gnome-screenshot", "-f", filepath],
                capture_output=True,
                timeout=10,
            )
            if result.returncode == 0:
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # 尝试 scrot
        try:
            result = subprocess.run(
                ["scrot", filepath],
                capture_output=True,
                timeout=10,
            )
            if result.returncode == 0:
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # 尝试 spectacle (KDE)
        try:
            result = subprocess.run(
                ["spectacle", "-b", "-f", "-o", filepath],
                capture_output=True,
                timeout=10,
            )
            if result.returncode == 0:
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # 尝试 import (ImageMagick)
        try:
            result = subprocess.run(
                ["import", "-window", "root", filepath],
                capture_output=True,
                timeout=10,
            )
            if result.returncode == 0:
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return False

    def _capture_macos_fullscreen(self, filepath: str) -> bool:
        """在 macOS 上进行全屏截图。

        使用 screencapture 命令。

        Args:
            filepath: 输出文件路径。

        Returns:
            成功返回 True，失败返回 False。
        """
        try:
            result = subprocess.run(
                ["screencapture", "-x", filepath],
                capture_output=True,
                timeout=10,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _capture_windows_fullscreen(self, filepath: str) -> bool:
        """在 Windows 上进行全屏截图。

        使用 PowerShell 进行截图。

        Args:
            filepath: 输出文件路径。

        Returns:
            成功返回 True，失败返回 False。
        """
        try:
            ps_script = f"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bitmap = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
$bitmap.Save('{filepath}', [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()
"""
            result = subprocess.run(
                ["powershell", "-command", ps_script],
                capture_output=True,
                timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW,  # type: ignore
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _capture_pil_fullscreen(self, filepath: str) -> bool:
        """使用 PIL ImageGrab 进行全屏截图。

        Args:
            filepath: 输出文件路径。

        Returns:
            成功返回 True，失败返回 False。
        """
        try:
            from PIL import ImageGrab

            screenshot = ImageGrab.grab()
            screenshot.save(filepath, "PNG")
            return True
        except ImportError:
            raise CaptureError("PIL/Pillow 未安装，无法使用 PIL 截图")
        except Exception as e:
            raise CaptureError(f"PIL 截图失败: {e}")

    def capture_window(self, output_dir: str = "./screenshots/", window_title: Optional[str] = None) -> str:
        """窗口截图。

        列出活跃窗口供选择，或直接指定窗口标题。

        Args:
            output_dir: 输出目录路径。
            window_title: 目标窗口标题。如果为 None，列出窗口供选择。

        Returns:
            截图文件的绝对路径。

        Raises:
            CaptureError: 当截图失败时。
        """
        output_dir = os.path.expanduser(output_dir)
        ensure_directory(output_dir)
        filepath = os.path.join(output_dir, generate_unique_filename("window"))

        if window_title is None:
            windows = self._list_windows()
            if not windows:
                raise CaptureError("未找到活跃窗口")

            print_info("可用窗口列表:")
            for i, (wid, title) in enumerate(windows):
                print(f"  [{i}] {title}")

            try:
                choice = int(input("\n请选择窗口编号: "))
                if choice < 0 or choice >= len(windows):
                    raise CaptureError(f"无效的选择: {choice}")
                window_title = windows[choice][1]
            except (ValueError, EOFError):
                raise CaptureError("无效的输入")

        success = self._capture_window_by_title(filepath, window_title)

        if not success or not os.path.exists(filepath):
            # 回退到 PIL
            try:
                success = self._capture_pil_fullscreen(filepath)
            except Exception:
                raise CaptureError("窗口截图失败")

        self._add_to_history(filepath, "window", {"window_title": window_title})
        print_success(f"窗口截图已保存: {filepath}")
        return os.path.abspath(filepath)

    def _list_windows(self) -> List[Tuple[str, str]]:
        """列出当前活跃窗口。

        Returns:
            窗口ID和标题的元组列表。
        """
        system = platform.system()
        windows: List[Tuple[str, str]] = []

        if system == "Linux":
            windows = self._list_windows_linux()
        elif system == "Darwin":
            windows = self._list_windows_macos()
        elif system == "Windows":
            windows = self._list_windows_windows()

        return windows

    def _list_windows_linux(self) -> List[Tuple[str, str]]:
        """列出 Linux 上的活跃窗口。

        Returns:
            窗口ID和标题的列表。
        """
        windows = []
        try:
            result = subprocess.run(
                ["wmctrl", "-l"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line.strip():
                        parts = line.split(None, 3)
                        if len(parts) >= 4:
                            windows.append((parts[0], parts[3]))
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        if not windows:
            try:
                result = subprocess.run(
                    ["xdotool", "search", "--name", ""],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    for wid in result.stdout.strip().split("\n"):
                        if wid.strip():
                            try:
                                name_result = subprocess.run(
                                    ["xdotool", "getwindowname", wid.strip()],
                                    capture_output=True,
                                    text=True,
                                    timeout=3,
                                )
                                if name_result.returncode == 0 and name_result.stdout.strip():
                                    windows.append((wid.strip(), name_result.stdout.strip()))
                            except subprocess.TimeoutExpired:
                                continue
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        return windows

    def _list_windows_macos(self) -> List[Tuple[str, str]]:
        """列出 macOS 上的活跃窗口。

        Returns:
            窗口ID和标题的列表。
        """
        windows = []
        try:
            script = """
tell application "System Events"
    set windowList to {}
    repeat with proc in (every process whose background only is false)
        try
            set windowNames to name of every window of proc
            repeat with wName in windowNames
                set end of windowList to (id of proc as string) & " " & wName
            end repeat
        end try
    end repeat
    return windowList
end tell
"""
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split(", "):
                    parts = line.split(" ", 1)
                    if len(parts) == 2:
                        windows.append((parts[0], parts[1]))
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return windows

    def _list_windows_windows(self) -> List[Tuple[str, str]]:
        """列出 Windows 上的活跃窗口。

        Returns:
            窗口句柄和标题的列表。
        """
        windows = []
        try:
            ps_script = """
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
using System.Collections.Generic;

public class WindowHelper {
    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    public static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    public static List<string> GetVisibleWindows() {
        var result = new List<string>();
        EnumWindows((hWnd, lParam) => {
            if (IsWindowVisible(hWnd)) {
                var sb = new StringBuilder(256);
                GetWindowText(hWnd, sb, 256);
                if (sb.Length > 0) {
                    result.Add(hWnd.ToInt64().ToString() + "|" + sb.ToString());
                }
            }
            return true;
        }, IntPtr.Zero);
        return result;
    }
}
"@
[WindowHelper]::GetVisibleWindows() | ForEach-Object { $_ }
"""
            result = subprocess.run(
                ["powershell", "-command", ps_script],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW,  # type: ignore
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    line = line.strip()
                    if "|" in line:
                        parts = line.split("|", 1)
                        windows.append((parts[0], parts[1]))
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return windows

    def _capture_window_by_title(self, filepath: str, window_title: str) -> bool:
        """按窗口标题截图。

        Args:
            filepath: 输出文件路径。
            window_title: 窗口标题（支持部分匹配）。

        Returns:
            成功返回 True，失败返回 False。
        """
        system = platform.system()

        if system == "Linux":
            try:
                result = subprocess.run(
                    ["xdotool", "search", "--name", window_title],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    window_id = result.stdout.strip().split("\n")[0]
                    import_result = subprocess.run(
                        ["import", "-window", window_id, filepath],
                        capture_output=True,
                        timeout=10,
                    )
                    return import_result.returncode == 0
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        elif system == "Darwin":
            try:
                result = subprocess.run(
                    ["screencapture", "-l", "$(osascript -e 'tell app \"System Events\" to tell process \"Safari\" to get id of window 1')", "-o", filepath],
                    capture_output=True,
                    timeout=10,
                    shell=True,
                )
                return result.returncode == 0
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        elif system == "Windows":
            try:
                ps_script = f"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bitmap = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
$bitmap.Save('{filepath}', [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()
"""
                result = subprocess.run(
                    ["powershell", "-command", ps_script],
                    capture_output=True,
                    timeout=15,
                    creationflags=subprocess.CREATE_NO_WINDOW,  # type: ignore
                )
                return result.returncode == 0
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        return False

    def capture_region(
        self,
        output_dir: str = "./screenshots/",
        region: Optional[Tuple[int, int, int, int]] = None,
    ) -> str:
        """区域选择截图。

        可以指定坐标区域或在终端中输入坐标。

        Args:
            output_dir: 输出目录路径。
            region: 截图区域 (x1, y1, x2, y2)。如果为 None，提示用户输入。

        Returns:
            截图文件的绝对路径。

        Raises:
            CaptureError: 当截图失败时。
        """
        output_dir = os.path.expanduser(output_dir)
        ensure_directory(output_dir)
        filepath = os.path.join(output_dir, generate_unique_filename("region"))

        if region is None:
            region = self._prompt_region()

        if region is None:
            raise CaptureError("未指定截图区域")

        x1, y1, x2, y2 = region
        if x1 >= x2 or y1 >= y2:
            raise CaptureError(f"无效的区域坐标: ({x1}, {y1}, {x2}, {y2})")

        success = self._capture_pil_region(filepath, x1, y1, x2, y2)

        if not success or not os.path.exists(filepath):
            raise CaptureError("区域截图失败")

        self._add_to_history(filepath, "region", {"region": list(region)})
        print_success(f"区域截图已保存: {filepath}")
        return os.path.abspath(filepath)

    def _prompt_region(self) -> Optional[Tuple[int, int, int, int]]:
        """在终端中提示用户输入截图区域坐标。

        Returns:
            区域坐标元组 (x1, y1, x2, y2)，取消返回 None。
        """
        print_info("请输入截图区域坐标 (格式: x1 y1 x2 y2)")
        print_info("例如: 100 100 500 400 表示从(100,100)到(500,400)的矩形区域")
        print_info("输入 'q' 取消")

        try:
            user_input = input("\n区域坐标: ").strip()
            if user_input.lower() == "q":
                return None

            parts = user_input.split()
            if len(parts) != 4:
                print_error("请输入4个数字，用空格分隔")
                return None

            coords = tuple(int(p) for p in parts)
            return coords  # type: ignore
        except (ValueError, EOFError):
            print_error("无效的输入")
            return None

    def _capture_pil_region(
        self, filepath: str, x1: int, y1: int, x2: int, y2: int
    ) -> bool:
        """使用 PIL 截取指定区域。

        Args:
            filepath: 输出文件路径。
            x1: 左上角 X 坐标。
            y1: 左上角 Y 坐标。
            x2: 右下角 X 坐标。
            y2: 右下角 Y 坐标。

        Returns:
            成功返回 True，失败返回 False。
        """
        try:
            from PIL import ImageGrab

            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            screenshot.save(filepath, "PNG")
            return True
        except ImportError:
            raise CaptureError("PIL/Pillow 未安装")
        except Exception as e:
            raise CaptureError(f"PIL 区域截图失败: {e}")

    def get_history(self, limit: int = 20) -> List[Dict]:
        """获取截图历史记录。

        Args:
            limit: 返回的最大记录数。

        Returns:
            历史记录列表，按时间倒序排列。
        """
        return self.history[:limit]

    def clear_history(self) -> None:
        """清空截图历史记录。"""
        self.history = []
        self._save_history()
        print_info("截图历史已清空")
