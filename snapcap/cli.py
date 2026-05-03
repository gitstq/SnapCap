"""
CLI 入口模块

SnapCap 命令行界面入口，使用 argparse 解析命令行参数。
支持截图、标注、上传、配置管理和历史查看功能。
支持管道操作，可在命令之间传递图片路径。
"""

import argparse
import json
import os
import sys
from typing import List, Optional

from . import __version__
from .annotate import AnnotationEngine, AnnotateError
from .capture import CaptureEngine, CaptureError
from .clipboard import copy_text, copy_image
from .config import ConfigManager
from .uploader import UploadError, format_upload_result, upload_image
from .utils import (
    Colors,
    colored,
    ensure_directory,
    get_file_size,
    print_error,
    print_info,
    print_success,
    print_warning,
    truncate_text,
)


def create_parser() -> argparse.ArgumentParser:
    """创建 CLI 参数解析器。

    Returns:
        配置好的 ArgumentParser 实例。
    """
    parser = argparse.ArgumentParser(
        prog="snapcap",
        description="SnapCap - 轻量级终端截图标注与分享工具",
        epilog="示例:\n"
        "  snapcap capture --mode fullscreen --output ./screenshots/\n"
        "  snapcap annotate screenshot.png --rect 10 10 200 200\n"
        "  snapcap upload screenshot.png --provider imgbb\n"
        "  snapcap capture | snapcap annotate --rect 10 10 200 200 | snapcap upload\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # ========== capture 命令 ==========
    capture_parser = subparsers.add_parser(
        "capture",
        help="截图",
        description="进行屏幕截图，支持全屏、窗口和区域选择模式。",
    )
    capture_parser.add_argument(
        "--mode",
        "-m",
        choices=["fullscreen", "window", "region"],
        default=None,
        help="截图模式: fullscreen(全屏), window(窗口), region(区域选择)",
    )
    capture_parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="输出目录路径 (默认: ./screenshots/)",
    )
    capture_parser.add_argument(
        "--filename",
        "-f",
        default=None,
        help="自定义输出文件名",
    )
    capture_parser.add_argument(
        "--region",
        "-r",
        nargs=4,
        type=int,
        metavar=("X1", "Y1", "X2", "Y2"),
        help="区域截图坐标 (仅在 region 模式下有效)",
    )
    capture_parser.add_argument(
        "--window-title",
        "-w",
        default=None,
        help="窗口标题 (仅在 window 模式下有效，支持部分匹配)",
    )

    # ========== annotate 命令 ==========
    annotate_parser = subparsers.add_parser(
        "annotate",
        help="标注图片",
        description="对图片进行标注，支持矩形框、箭头、文字、马赛克、高亮等。",
    )
    annotate_parser.add_argument(
        "image",
        nargs="?",
        default=None,
        help="图片文件路径 (如果未指定，从 stdin 读取)",
    )
    annotate_parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="输出文件路径 (默认: 原文件名_annotated.png)",
    )
    annotate_parser.add_argument(
        "--rect",
        nargs=4,
        type=int,
        metavar=("X1", "Y1", "X2", "Y2"),
        help="绘制矩形框 (坐标: x1 y1 x2 y2)",
    )
    annotate_parser.add_argument(
        "--arrow",
        nargs=4,
        type=int,
        metavar=("X1", "Y1", "X2", "Y2"),
        help="绘制箭头 (坐标: 起点x 起点y 终点x 终点y)",
    )
    annotate_parser.add_argument(
        "--text",
        nargs=3,
        metavar=("X", "Y", "CONTENT"),
        help="绘制文字标注 (坐标: x y 内容)",
    )
    annotate_parser.add_argument(
        "--mosaic",
        nargs=4,
        type=int,
        metavar=("X1", "Y1", "X2", "Y2"),
        help="马赛克效果 (坐标: x1 y1 x2 y2)",
    )
    annotate_parser.add_argument(
        "--blur",
        nargs=4,
        type=int,
        metavar=("X1", "Y1", "X2", "Y2"),
        help="模糊效果 (坐标: x1 y1 x2 y2)",
    )
    annotate_parser.add_argument(
        "--highlight",
        nargs=4,
        type=int,
        metavar=("X1", "Y1", "X2", "Y2"),
        help="高亮标注 (坐标: x1 y1 x2 y2)",
    )
    annotate_parser.add_argument(
        "--number",
        nargs=2,
        type=int,
        metavar=("X", "Y"),
        action="append",
        help="序号标注位置 (可多次使用: --number x y --number x y)",
    )
    annotate_parser.add_argument(
        "--color",
        default=None,
        help="标注颜色 (十六进制，如 #FF0000)",
    )
    annotate_parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="线条宽度",
    )
    annotate_parser.add_argument(
        "--font-size",
        type=int,
        default=None,
        help="文字大小",
    )

    # ========== upload 命令 ==========
    upload_parser = subparsers.add_parser(
        "upload",
        help="上传图片",
        description="将图片上传到图床服务，获取分享链接。",
    )
    upload_parser.add_argument(
        "image",
        nargs="?",
        default=None,
        help="图片文件路径 (如果未指定，从 stdin 读取)",
    )
    upload_parser.add_argument(
        "--provider",
        "-p",
        choices=["fileio", "imgbb", "custom"],
        default=None,
        help="图床提供商",
    )
    upload_parser.add_argument(
        "--api-key",
        default=None,
        help="API 密钥 (imgbb 需要)",
    )
    upload_parser.add_argument(
        "--endpoint",
        default=None,
        help="自定义 API 端点 (custom 需要)",
    )
    upload_parser.add_argument(
        "--format",
        choices=["url", "markdown", "html", "json"],
        default=None,
        help="输出格式",
    )
    upload_parser.add_argument(
        "--copy",
        action="store_true",
        default=None,
        help="自动复制链接到剪贴板",
    )

    # ========== config 命令 ==========
    config_parser = subparsers.add_parser(
        "config",
        help="管理配置",
        description="查看和修改 SnapCap 配置。",
    )
    config_parser.add_argument(
        "--show",
        action="store_true",
        help="显示当前配置",
    )
    config_parser.add_argument(
        "--set",
        metavar="KEY=VALUE",
        help="设置配置项 (格式: key=value，如 capture.default_mode=region)",
    )
    config_parser.add_argument(
        "--get",
        metavar="KEY",
        help="获取指定配置项",
    )
    config_parser.add_argument(
        "--reset",
        action="store_true",
        help="重置为默认配置",
    )
    config_parser.add_argument(
        "--export",
        metavar="FILE",
        help="导出配置到文件",
    )
    config_parser.add_argument(
        "--import",
        dest="import_file",
        metavar="FILE",
        help="从文件导入配置",
    )

    # ========== history 命令 ==========
    history_parser = subparsers.add_parser(
        "history",
        help="查看截图历史",
        description="查看和管理截图历史记录。",
    )
    history_parser.add_argument(
        "--limit",
        "-n",
        type=int,
        default=20,
        help="显示的记录数量 (默认: 20)",
    )
    history_parser.add_argument(
        "--clear",
        action="store_true",
        help="清空历史记录",
    )
    history_parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出",
    )

    return parser


def _get_image_from_stdin() -> Optional[str]:
    """从 stdin 读取图片路径（用于管道操作）。

    Returns:
        图片文件路径，如果 stdin 没有数据则返回 None。
    """
    if not sys.stdin.isatty():
        try:
            line = sys.stdin.read().strip()
            if line and os.path.exists(line):
                return line
        except Exception:
            pass
    return None


def _output_for_pipeline(filepath: str) -> None:
    """将文件路径输出到 stdout（用于管道操作）。

    Args:
        filepath: 要传递的文件路径。
    """
    print(filepath)


def cmd_capture(args: argparse.Namespace, config: ConfigManager) -> int:
    """处理 capture 命令。

    Args:
        args: 命令行参数。
        config: 配置管理器。

    Returns:
        退出码，0 表示成功。
    """
    mode = args.mode or config.get("capture.default_mode", "fullscreen")
    output_dir = args.output or config.get("capture.default_output", "./screenshots/")

    try:
        engine = CaptureEngine(history_path=config.get_history_path())

        if mode == "fullscreen":
            filepath = engine.capture_fullscreen(
                output_dir=output_dir,
                filename=args.filename,
            )
        elif mode == "window":
            filepath = engine.capture_window(
                output_dir=output_dir,
                window_title=args.window_title,
            )
        elif mode == "region":
            region = tuple(args.region) if args.region else None  # type: ignore
            filepath = engine.capture_region(
                output_dir=output_dir,
                region=region,  # type: ignore
            )
        else:
            print_error(f"不支持的截图模式: {mode}")
            return 1

        _output_for_pipeline(filepath)
        return 0

    except CaptureError as e:
        print_error(str(e))
        return 1
    except KeyboardInterrupt:
        print_warning("\n操作已取消")
        return 130


def cmd_annotate(args: argparse.Namespace, config: ConfigManager) -> int:
    """处理 annotate 命令。

    Args:
        args: 命令行参数。
        config: 配置管理器。

    Returns:
        退出码，0 表示成功。
    """
    image_path = args.image or _get_image_from_stdin()

    if not image_path:
        print_error("请指定图片路径，或通过管道传入: snapcap capture | snapcap annotate")
        return 1

    if not os.path.exists(image_path):
        print_error(f"图片文件不存在: {image_path}")
        return 1

    try:
        engine = AnnotationEngine(image_path)

        # 获取标注样式配置
        color = args.color or config.get("annotate.rect_color", "#FF0000")
        width = args.width or config.get("annotate.rect_width", 3)
        font_size = args.font_size or config.get("annotate.text_size", 24)

        # 应用标注
        has_annotation = False

        if args.rect:
            x1, y1, x2, y2 = args.rect
            engine.draw_rect(x1, y1, x2, y2, color=color, width=width)
            has_annotation = True

        if args.arrow:
            x1, y1, x2, y2 = args.arrow
            engine.draw_arrow(x1, y1, x2, y2, color=color, width=width)
            has_annotation = True

        if args.text:
            x, y, content = args.text
            text_color = config.get("annotate.text_color", "#FFFFFF")
            bg_color = config.get("annotate.text_bg_color", "#000000")
            engine.draw_text(
                x, y, content,
                color=text_color,
                font_size=font_size,
                bg_color=bg_color,
            )
            has_annotation = True

        if args.mosaic:
            x1, y1, x2, y2 = args.mosaic
            mosaic_size = config.get("annotate.mosaic_size", 10)
            engine.draw_mosaic(x1, y1, x2, y2, block_size=mosaic_size)
            has_annotation = True

        if args.blur:
            x1, y1, x2, y2 = args.blur
            engine.draw_blur(x1, y1, x2, y2)
            has_annotation = True

        if args.highlight:
            x1, y1, x2, y2 = args.highlight
            hl_color = config.get("annotate.highlight_color", "#FFFF00")
            hl_opacity = config.get("annotate.highlight_opacity", 0.3)
            engine.draw_highlight(x1, y1, x2, y2, color=hl_color, opacity=hl_opacity)
            has_annotation = True

        if args.number:
            num_color = config.get("annotate.number_color", "#FF0000")
            num_bg = config.get("annotate.number_bg_color", "#FFFFFF")
            num_size = config.get("annotate.number_size", 20)
            engine.draw_numbers_auto(
                [(x, y) for x, y in args.number],
                color=num_color,
                bg_color=num_bg,
                size=num_size,
            )
            has_annotation = True

        if not has_annotation:
            print_warning("未指定任何标注操作。可用的标注: --rect, --arrow, --text, --mosaic, --blur, --highlight, --number")
            return 0

        output_path = engine.save(output_path=args.output)
        _output_for_pipeline(output_path)
        return 0

    except AnnotateError as e:
        print_error(str(e))
        return 1


def cmd_upload(args: argparse.Namespace, config: ConfigManager) -> int:
    """处理 upload 命令。

    Args:
        args: 命令行参数。
        config: 配置管理器。

    Returns:
        退出码，0 表示成功。
    """
    image_path = args.image or _get_image_from_stdin()

    if not image_path:
        print_error("请指定图片路径，或通过管道传入: snapcap capture | snapcap upload")
        return 1

    if not os.path.exists(image_path):
        print_error(f"图片文件不存在: {image_path}")
        return 1

    provider = args.provider or config.get("upload.default_provider", "fileio")
    api_key = args.api_key or config.get("upload.imgbb_api_key", "")
    endpoint = args.endpoint or config.get("upload.custom_endpoint", "")
    output_format = args.format or config.get("upload.output_format", "url")
    auto_copy = args.copy if args.copy is not None else config.get("clipboard.auto_copy", True)

    try:
        result = upload_image(
            filepath=image_path,
            provider=provider,
            api_key=api_key,
            endpoint=endpoint,
            field_name=config.get("upload.custom_field_name", "file"),
            headers=config.get("upload.custom_headers", {}),
            response_url_path=config.get("upload.custom_response_url_path", "data.url"),
        )

        formatted = format_upload_result(result, output_format)
        print_success(f"上传成功 ({result.get('provider', 'unknown')})")
        print(f"  {colored('URL:', Colors.CYAN)} {formatted}")

        if auto_copy and output_format in ("url", "markdown"):
            if copy_text(formatted):
                print_info("链接已复制到剪贴板")
            else:
                print_warning("复制到剪贴板失败")

        return 0

    except (UploadError, ValueError, FileNotFoundError) as e:
        print_error(str(e))
        return 1


def cmd_config(args: argparse.Namespace, config: ConfigManager) -> int:
    """处理 config 命令。

    Args:
        args: 命令行参数。
        config: 配置管理器。

    Returns:
        退出码，0 表示成功。
    """
    if args.show:
        print(colored("SnapCap 配置", Colors.BOLD))
        print(f"  配置文件: {config.config_path}")
        print("-" * 40)
        print(config.show())
        return 0

    if args.set:
        if "=" not in args.set:
            print_error("配置格式错误，请使用 key=value 格式")
            return 1
        key, value = args.set.split("=", 1)
        # 尝试解析 JSON 值
        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            parsed_value = value
        config.set(key, parsed_value)
        print_success(f"已设置 {key} = {parsed_value}")
        return 0

    if args.get:
        value = config.get(args.get)
        if value is None:
            print_warning(f"配置项 '{args.get}' 不存在")
            return 1
        print(json.dumps(value, indent=2, ensure_ascii=False))
        return 0

    if args.reset:
        config.reset()
        print_success("配置已重置为默认值")
        return 0

    if args.export:
        try:
            config.export_config(args.export)
            print_success(f"配置已导出到: {args.export}")
            return 0
        except IOError as e:
            print_error(str(e))
            return 1

    if args.import_file:
        try:
            config.import_config(args.import_file)
            print_success(f"已从 {args.import_file} 导入配置")
            return 0
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print_error(str(e))
            return 1

    # 没有指定参数时显示配置
    print(colored("SnapCap 配置", Colors.BOLD))
    print(f"  配置文件: {config.config_path}")
    print("-" * 40)
    print(config.show())
    return 0


def cmd_history(args: argparse.Namespace, config: ConfigManager) -> int:
    """处理 history 命令。

    Args:
        args: 命令行参数。
        config: 配置管理器。

    Returns:
        退出码，0 表示成功。
    """
    engine = CaptureEngine(history_path=config.get_history_path())

    if args.clear:
        engine.clear_history()
        return 0

    history = engine.get_history(limit=args.limit)

    if not history:
        print_info("暂无截图历史记录")
        return 0

    if args.json:
        print(json.dumps(history, indent=2, ensure_ascii=False))
        return 0

    # 格式化输出
    print(colored("截图历史", Colors.BOLD))
    print(f"  共 {len(engine.history)} 条记录，显示最近 {len(history)} 条")
    print("-" * 70)
    print(
        f"  {'#':<4} {'时间':<20} {'模式':<12} {'大小':<10} {'路径'}"
    )
    print("-" * 70)

    for i, entry in enumerate(history, 1):
        timestamp = entry.get("timestamp", "N/A")[:19]
        mode = entry.get("mode", "N/A")
        size = entry.get("size", "N/A")
        filepath = entry.get("filepath", "N/A")

        # 彩色模式标签
        mode_colors = {
            "fullscreen": Colors.GREEN,
            "window": Colors.BLUE,
            "region": Colors.YELLOW,
        }
        mode_display = colored(
            mode, mode_colors.get(mode, Colors.WHITE)
        )

        print(
            f"  {i:<4} {timestamp:<20} {mode_display:<22} {size:<10} {truncate_text(filepath, 35)}"
        )

    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """SnapCap CLI 主入口函数。

    Args:
        argv: 命令行参数列表。如果为 None，使用 sys.argv[1:]。

    Returns:
        退出码，0 表示成功。
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # 没有指定命令时显示帮助
    if not args.command:
        parser.print_help()
        return 0

    # 加载配置
    config = ConfigManager()

    # 分发命令
    if args.command == "capture":
        return cmd_capture(args, config)
    elif args.command == "annotate":
        return cmd_annotate(args, config)
    elif args.command == "upload":
        return cmd_upload(args, config)
    elif args.command == "config":
        return cmd_config(args, config)
    elif args.command == "history":
        return cmd_history(args, config)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
