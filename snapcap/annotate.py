"""
标注引擎模块

使用 Pillow 提供图片标注功能，包括矩形框、箭头、文字、马赛克、高亮和序号标注。
"""

import math
import os
from typing import List, Optional, Tuple

from .utils import print_error, print_success


class AnnotateError(Exception):
    """标注操作异常。"""

    pass


class AnnotationEngine:
    """图片标注引擎。

    使用 Pillow 在图片上绘制各种标注，包括矩形框、箭头、文字、
    马赛克效果、高亮覆盖和序号标记。

    Attributes:
        image_path: 当前操作的图片路径。
        image: Pillow Image 对象。
    """

    def __init__(self, image_path: str) -> None:
        """初始化标注引擎并加载图片。

        Args:
            image_path: 图片文件路径。

        Raises:
            AnnotateError: 当图片加载失败时。
        """
        try:
            from PIL import Image

            self.image_path = os.path.abspath(image_path)
            self.image = Image.open(image_path)
            # 确保图片为 RGBA 模式以支持透明度
            if self.image.mode != "RGBA":
                self.image = self.image.convert("RGBA")
        except FileNotFoundError:
            raise AnnotateError(f"图片文件不存在: {image_path}")
        except Exception as e:
            raise AnnotateError(f"无法加载图片: {e}")

    def _get_draw_context(self):
        """获取绘图上下文。

        Returns:
            PIL ImageDraw.Draw 对象。
        """
        from PIL import ImageDraw

        return ImageDraw.Draw(self.image)

    def draw_rect(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str = "#FF0000",
        width: int = 3,
        fill: Optional[str] = None,
    ) -> "AnnotationEngine":
        """绘制矩形框标注。

        Args:
            x1: 左上角 X 坐标。
            y1: 左上角 Y 坐标。
            x2: 右下角 X 坐标。
            y2: 右下角 Y 坐标。
            color: 边框颜色，十六进制格式，默认为 '#FF0000'。
            width: 边框线宽，默认为 3。
            fill: 填充颜色，如果为 None 则不填充。

        Returns:
            self，支持链式调用。
        """
        draw = self._get_draw_context()
        draw.rectangle(
            [(x1, y1), (x2, y2)],
            outline=color,
            width=width,
            fill=fill,
        )
        return self

    def draw_arrow(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str = "#FF0000",
        width: int = 2,
        head_length: int = 15,
        head_width: int = 10,
    ) -> "AnnotationEngine":
        """绘制箭头标注。

        Args:
            x1: 起点 X 坐标。
            y1: 起点 Y 坐标。
            x2: 终点 X 坐标。
            y2: 终点 Y 坐标。
            color: 箭头颜色，默认为 '#FF0000'。
            width: 线条宽度，默认为 2。
            head_length: 箭头头部长度，默认为 15。
            head_width: 箭头头部宽度，默认为 10。

        Returns:
            self，支持链式调用。
        """
        draw = self._get_draw_context()

        # 绘制主线
        draw.line([(x1, y1), (x2, y2)], fill=color, width=width)

        # 计算箭头头部
        angle = math.atan2(y2 - y1, x2 - x1)
        arrow_angle = math.pi / 6  # 30度

        # 箭头左翼
        left_x = x2 - head_length * math.cos(angle - arrow_angle)
        left_y = y2 - head_length * math.sin(angle - arrow_angle)

        # 箭头右翼
        right_x = x2 - head_length * math.cos(angle + arrow_angle)
        right_y = y2 - head_length * math.sin(angle + arrow_angle)

        # 绘制箭头头部（填充三角形）
        draw.polygon(
            [(x2, y2), (left_x, left_y), (right_x, right_y)],
            fill=color,
        )

        return self

    def draw_text(
        self,
        x: int,
        y: int,
        text: str,
        color: str = "#FFFFFF",
        font_size: int = 24,
        bg_color: Optional[str] = "#000000",
        padding: int = 5,
    ) -> "AnnotationEngine":
        """绘制文字标注。

        Args:
            x: 文字左上角 X 坐标。
            y: 文字左上角 Y 坐标。
            text: 文字内容。
            color: 文字颜色，默认为 '#FFFFFF'。
            font_size: 字体大小，默认为 24。
            bg_color: 背景颜色，如果为 None 则无背景。
            padding: 文字与背景的间距，默认为 5。

        Returns:
            self，支持链式调用。
        """
        from PIL import ImageDraw, ImageFont

        draw = self._get_draw_context()

        # 尝试加载字体
        font = self._load_font(font_size)

        # 获取文字边界框
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # 绘制背景
        if bg_color:
            draw.rectangle(
                [
                    (x - padding, y - padding),
                    (x + text_width + padding, y + text_height + padding),
                ],
                fill=bg_color,
            )

        # 绘制文字
        draw.text((x, y), text, fill=color, font=font)

        return self

    def draw_mosaic(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        block_size: int = 10,
    ) -> "AnnotationEngine":
        """绘制马赛克效果（像素化）。

        Args:
            x1: 区域左上角 X 坐标。
            y1: 区域左上角 Y 坐标。
            x2: 区域右下角 X 坐标。
            y2: 区域右下角 Y 坐标。
            block_size: 马赛克块大小（像素），默认为 10。

        Returns:
            self，支持链式调用。
        """
        from PIL import Image

        # 确保坐标在图片范围内
        img_width, img_height = self.image.size
        x1 = max(0, min(x1, img_width))
        y1 = max(0, min(y1, img_height))
        x2 = max(0, min(x2, img_width))
        y2 = max(0, min(y2, img_height))

        if x1 >= x2 or y1 >= y2:
            return self

        # 裁剪目标区域
        region = self.image.crop((x1, y1, x2, y2))

        # 缩小再放大实现像素化
        small_width = max(1, (x2 - x1) // block_size)
        small_height = max(1, (y2 - y1) // block_size)

        small_region = region.resize((small_width, small_height), Image.NEAREST)
        mosaic_region = small_region.resize(
            (x2 - x1, y2 - y1), Image.NEAREST
        )

        # 将马赛克区域粘贴回原图
        self.image.paste(mosaic_region, (x1, y1))

        return self

    def draw_highlight(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str = "#FFFF00",
        opacity: float = 0.3,
    ) -> "AnnotationEngine":
        """绘制高亮标注（半透明彩色覆盖）。

        Args:
            x1: 区域左上角 X 坐标。
            y1: 区域左上角 Y 坐标。
            x2: 区域右下角 X 坐标。
            y2: 区域右下角 Y 坐标。
            color: 高亮颜色，默认为 '#FFFF00'。
            opacity: 透明度 (0.0-1.0)，默认为 0.3。

        Returns:
            self，支持链式调用。
        """
        from PIL import Image

        # 确保坐标在图片范围内
        img_width, img_height = self.image.size
        x1 = max(0, min(x1, img_width))
        y1 = max(0, min(y1, img_height))
        x2 = max(0, min(x2, img_width))
        y2 = max(0, min(y2, img_height))

        if x1 >= x2 or y1 >= y2:
            return self

        # 创建半透明覆盖层
        overlay = Image.new(
            "RGBA",
            (x2 - x1, y2 - y1),
            color,
        )

        # 设置透明度
        alpha = overlay.split()[3]
        alpha = alpha.point(lambda p: int(p * opacity))
        overlay.putalpha(alpha)

        # 合并覆盖层
        self.image.paste(
            overlay,
            (x1, y1),
            mask=overlay,
        )

        return self

    def draw_number(
        self,
        x: int,
        y: int,
        number: int,
        color: str = "#FF0000",
        bg_color: str = "#FFFFFF",
        size: int = 20,
    ) -> "AnnotationEngine":
        """绘制序号标注（带背景的圆形数字标记）。

        Args:
            x: 圆心 X 坐标。
            y: 圆心 Y 坐标。
            number: 序号数字。
            color: 数字颜色，默认为 '#FF0000'。
            bg_color: 圆形背景颜色，默认为 '#FFFFFF'。
            size: 圆形半径，默认为 20。

        Returns:
            self，支持链式调用。
        """
        from PIL import ImageDraw, ImageFont

        draw = self._get_draw_context()

        # 绘制圆形背景
        draw.ellipse(
            [(x - size, y - size), (x + size, y + size)],
            fill=bg_color,
            outline=color,
            width=2,
        )

        # 绘制数字
        font = self._load_font(int(size * 1.2))
        text = str(number)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = x - text_width // 2
        text_y = y - text_height // 2 - size // 6

        draw.text((text_x, text_y), text, fill=color, font=font)

        return self

    def draw_numbers_auto(
        self,
        points: List[Tuple[int, int]],
        start_number: int = 1,
        color: str = "#FF0000",
        bg_color: str = "#FFFFFF",
        size: int = 20,
    ) -> "AnnotationEngine":
        """自动在多个位置绘制序号标注。

        Args:
            points: 坐标列表，每个元素为 (x, y) 元组。
            start_number: 起始序号，默认为 1。
            color: 数字颜色，默认为 '#FF0000'。
            bg_color: 圆形背景颜色，默认为 '#FFFFFF'。
            size: 圆形半径，默认为 20。

        Returns:
            self，支持链式调用。
        """
        for i, (x, y) in enumerate(points, start=start_number):
            self.draw_number(x, y, i, color=color, bg_color=bg_color, size=size)
        return self

    def draw_blur(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        radius: int = 10,
    ) -> "AnnotationEngine":
        """绘制模糊效果。

        Args:
            x1: 区域左上角 X 坐标。
            y1: 区域左上角 Y 坐标。
            x2: 区域右下角 X 坐标。
            y2: 区域右下角 Y 坐标。
            radius: 模糊半径，默认为 10。

        Returns:
            self，支持链式调用。
        """
        from PIL import Image, ImageFilter

        # 确保坐标在图片范围内
        img_width, img_height = self.image.size
        x1 = max(0, min(x1, img_width))
        y1 = max(0, min(y1, img_height))
        x2 = max(0, min(x2, img_width))
        y2 = max(0, min(y2, img_height))

        if x1 >= x2 or y1 >= y2:
            return self

        # 裁剪目标区域
        region = self.image.crop((x1, y1, x2, y2))

        # 应用高斯模糊
        blurred_region = region.filter(ImageFilter.GaussianBlur(radius=radius))

        # 将模糊区域粘贴回原图
        self.image.paste(blurred_region, (x1, y1))

        return self

    def _load_font(self, font_size: int):
        """加载字体文件。

        尝试加载系统字体，如果失败则使用 Pillow 默认字体。

        Args:
            font_size: 字体大小。

        Returns:
            PIL ImageFont 对象。
        """
        from PIL import ImageFont

        # 尝试加载常见系统字体
        font_paths = [
            # Linux
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
            # macOS
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFNSText.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            # Windows
            "C:\\Windows\\Fonts\\msyh.ttc",
            "C:\\Windows\\Fonts\\simhei.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
        ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, font_size)
                except (IOError, OSError):
                    continue

        # 使用 Pillow 默认字体
        try:
            return ImageFont.load_default(size=font_size)
        except TypeError:
            # 旧版 Pillow 不支持 size 参数
            return ImageFont.load_default()

    def save(self, output_path: Optional[str] = None, format: str = "PNG") -> str:
        """保存标注后的图片。

        Args:
            output_path: 输出文件路径。如果为 None，在原文件名后添加 '_annotated'。
            format: 输出格式，默认为 'PNG'。

        Returns:
            保存后的文件绝对路径。

        Raises:
            AnnotateError: 当保存失败时。
        """
        if output_path is None:
            base, ext = os.path.splitext(self.image_path)
            output_path = f"{base}_annotated{ext}"

        output_path = os.path.abspath(output_path)

        try:
            # 如果输出格式为 JPEG，需要转换为 RGB
            if format.upper() in ("JPEG", "JPG") and self.image.mode == "RGBA":
                rgb_image = self.image.convert("RGB")
                rgb_image.save(output_path, format)
            else:
                self.image.save(output_path, format)

            print_success(f"标注图片已保存: {output_path}")
            return output_path
        except Exception as e:
            raise AnnotateError(f"保存图片失败: {e}")

    def undo(self) -> "AnnotationEngine":
        """撤销上一步操作，重新加载原始图片。

        Returns:
            self。
        """
        from PIL import Image

        self.image = Image.open(self.image_path)
        if self.image.mode != "RGBA":
            self.image = self.image.convert("RGBA")
        return self

    def get_size(self) -> Tuple[int, int]:
        """获取当前图片尺寸。

        Returns:
            图片宽度和高度的元组 (width, height)。
        """
        return self.image.size
