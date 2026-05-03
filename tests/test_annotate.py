"""
标注引擎单元测试
"""

import os
import tempfile
import unittest

from PIL import Image

from snapcap.annotate import AnnotationEngine, AnnotateError


class TestAnnotationEngine(unittest.TestCase):
    """AnnotationEngine 测试类。"""

    def setUp(self):
        """测试前准备：创建测试图片。"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test.png")
        # 创建一个 800x600 的测试图片
        img = Image.new("RGB", (800, 600), color=(255, 255, 255))
        img.save(self.test_image_path, "PNG")

    def tearDown(self):
        """测试后清理。"""
        if os.path.exists(self.temp_dir):
            for f in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, f))
            os.rmdir(self.temp_dir)

    def test_init(self):
        """测试初始化。"""
        engine = AnnotationEngine(self.test_image_path)
        self.assertEqual(engine.image.size, (800, 600))

    def test_init_file_not_found(self):
        """测试文件不存在时的异常。"""
        with self.assertRaises(AnnotateError):
            AnnotationEngine("/nonexistent/image.png")

    def test_draw_rect(self):
        """测试矩形框标注。"""
        engine = AnnotationEngine(self.test_image_path)
        result = engine.draw_rect(10, 10, 200, 200, color="#FF0000", width=3)
        self.assertIsInstance(result, AnnotationEngine)

        # 保存并验证文件存在
        output_path = os.path.join(self.temp_dir, "rect_test.png")
        saved_path = engine.save(output_path)
        self.assertTrue(os.path.exists(saved_path))

    def test_draw_arrow(self):
        """测试箭头标注。"""
        engine = AnnotationEngine(self.test_image_path)
        result = engine.draw_arrow(10, 10, 200, 200, color="#FF0000", width=2)
        self.assertIsInstance(result, AnnotationEngine)

        output_path = os.path.join(self.temp_dir, "arrow_test.png")
        saved_path = engine.save(output_path)
        self.assertTrue(os.path.exists(saved_path))

    def test_draw_text(self):
        """测试文字标注。"""
        engine = AnnotationEngine(self.test_image_path)
        result = engine.draw_text(
            50, 50, "Hello SnapCap",
            color="#FFFFFF",
            font_size=24,
            bg_color="#000000",
        )
        self.assertIsInstance(result, AnnotationEngine)

        output_path = os.path.join(self.temp_dir, "text_test.png")
        saved_path = engine.save(output_path)
        self.assertTrue(os.path.exists(saved_path))

    def test_draw_text_no_bg(self):
        """测试无背景文字标注。"""
        engine = AnnotationEngine(self.test_image_path)
        result = engine.draw_text(
            50, 50, "No Background",
            color="#FF0000",
            bg_color=None,
        )
        self.assertIsInstance(result, AnnotationEngine)

    def test_draw_mosaic(self):
        """测试马赛克效果。"""
        engine = AnnotationEngine(self.test_image_path)
        result = engine.draw_mosaic(100, 100, 300, 300, block_size=10)
        self.assertIsInstance(result, AnnotationEngine)

        output_path = os.path.join(self.temp_dir, "mosaic_test.png")
        saved_path = engine.save(output_path)
        self.assertTrue(os.path.exists(saved_path))

    def test_draw_mosaic_out_of_bounds(self):
        """测试超出图片范围的马赛克（应被裁剪）。"""
        engine = AnnotationEngine(self.test_image_path)
        result = engine.draw_mosaic(-100, -100, 900, 900, block_size=10)
        self.assertIsInstance(result, AnnotationEngine)

    def test_draw_highlight(self):
        """测试高亮标注。"""
        engine = AnnotationEngine(self.test_image_path)
        result = engine.draw_highlight(100, 100, 300, 300, color="#FFFF00", opacity=0.3)
        self.assertIsInstance(result, AnnotationEngine)

        output_path = os.path.join(self.temp_dir, "highlight_test.png")
        saved_path = engine.save(output_path)
        self.assertTrue(os.path.exists(saved_path))

    def test_draw_blur(self):
        """测试模糊效果。"""
        engine = AnnotationEngine(self.test_image_path)
        result = engine.draw_blur(100, 100, 300, 300, radius=10)
        self.assertIsInstance(result, AnnotationEngine)

        output_path = os.path.join(self.temp_dir, "blur_test.png")
        saved_path = engine.save(output_path)
        self.assertTrue(os.path.exists(saved_path))

    def test_draw_number(self):
        """测试序号标注。"""
        engine = AnnotationEngine(self.test_image_path)
        result = engine.draw_number(100, 100, 1, color="#FF0000", bg_color="#FFFFFF", size=20)
        self.assertIsInstance(result, AnnotationEngine)

        output_path = os.path.join(self.temp_dir, "number_test.png")
        saved_path = engine.save(output_path)
        self.assertTrue(os.path.exists(saved_path))

    def test_draw_numbers_auto(self):
        """测试自动序号标注。"""
        engine = AnnotationEngine(self.test_image_path)
        points = [(100, 100), (200, 200), (300, 300)]
        result = engine.draw_numbers_auto(points, start_number=1)
        self.assertIsInstance(result, AnnotationEngine)

    def test_chain_operations(self):
        """测试链式操作。"""
        engine = AnnotationEngine(self.test_image_path)
        result = (
            engine
            .draw_rect(10, 10, 200, 200)
            .draw_arrow(200, 200, 400, 100)
            .draw_text(50, 50, "Test")
            .draw_mosaic(300, 300, 500, 500)
            .draw_highlight(100, 300, 250, 400)
            .draw_number(600, 500, 1)
        )
        self.assertIsInstance(result, AnnotationEngine)

        output_path = os.path.join(self.temp_dir, "chain_test.png")
        saved_path = engine.save(output_path)
        self.assertTrue(os.path.exists(saved_path))

    def test_save_default_path(self):
        """测试默认输出路径。"""
        engine = AnnotationEngine(self.test_image_path)
        engine.draw_rect(10, 10, 200, 200)
        saved_path = engine.save()
        self.assertTrue("_annotated" in saved_path)
        self.assertTrue(os.path.exists(saved_path))

    def test_save_custom_path(self):
        """测试自定义输出路径。"""
        engine = AnnotationEngine(self.test_image_path)
        engine.draw_rect(10, 10, 200, 200)
        output_path = os.path.join(self.temp_dir, "custom_output.png")
        saved_path = engine.save(output_path=output_path)
        self.assertEqual(saved_path, os.path.abspath(output_path))

    def test_undo(self):
        """测试撤销操作。"""
        engine = AnnotationEngine(self.test_image_path)
        engine.draw_rect(10, 10, 200, 200)
        result = engine.undo()
        self.assertIsInstance(result, AnnotationEngine)

    def test_get_size(self):
        """测试获取图片尺寸。"""
        engine = AnnotationEngine(self.test_image_path)
        size = engine.get_size()
        self.assertEqual(size, (800, 600))

    def test_loads_rgba(self):
        """测试加载非RGBA图片时自动转换。"""
        engine = AnnotationEngine(self.test_image_path)
        self.assertEqual(engine.image.mode, "RGBA")


if __name__ == "__main__":
    unittest.main()
