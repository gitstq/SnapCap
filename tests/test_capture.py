"""
截图引擎单元测试
"""

import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from snapcap.capture import CaptureEngine, CaptureError


class TestCaptureEngine(unittest.TestCase):
    """CaptureEngine 测试类。"""

    def setUp(self):
        """测试前准备：创建临时目录和历史文件。"""
        self.temp_dir = tempfile.mkdtemp()
        self.history_file = os.path.join(self.temp_dir, "history.json")
        self.engine = CaptureEngine(history_path=self.history_file)

    def tearDown(self):
        """测试后清理：删除临时文件。"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_init(self):
        """测试初始化。"""
        self.assertIsInstance(self.engine.history, list)
        self.assertEqual(self.engine.history_path, self.history_file)

    def test_load_empty_history(self):
        """测试加载空历史记录。"""
        self.assertEqual(len(self.engine.history), 0)

    def test_add_to_history(self):
        """测试添加历史记录。"""
        # 创建一个临时图片文件
        test_file = os.path.join(self.temp_dir, "test.png")
        with open(test_file, "w") as f:
            f.write("fake image data")

        entry = self.engine._add_to_history(test_file, "fullscreen")

        self.assertEqual(len(self.engine.history), 1)
        self.assertEqual(entry["mode"], "fullscreen")
        self.assertIn("timestamp", entry)
        self.assertIn("filepath", entry)
        self.assertIn("size", entry)

    def test_save_and_load_history(self):
        """测试历史记录的保存和加载。"""
        test_file = os.path.join(self.temp_dir, "test.png")
        with open(test_file, "w") as f:
            f.write("fake image data")

        self.engine._add_to_history(test_file, "window")

        # 重新加载
        engine2 = CaptureEngine(history_path=self.history_file)
        self.assertEqual(len(engine2.history), 1)
        self.assertEqual(engine2.history[0]["mode"], "window")

    def test_max_history_entries(self):
        """测试历史记录数量限制。"""
        test_file = os.path.join(self.temp_dir, "test.png")
        with open(test_file, "w") as f:
            f.write("fake image data")

        # 添加超过限制的记录
        for i in range(110):
            self.engine._add_to_history(test_file, "fullscreen")

        # 应该只保留最近的 100 条
        self.assertLessEqual(len(self.engine.history), 100)

    def test_clear_history(self):
        """测试清空历史记录。"""
        test_file = os.path.join(self.temp_dir, "test.png")
        with open(test_file, "w") as f:
            f.write("fake image data")

        self.engine._add_to_history(test_file, "fullscreen")
        self.assertEqual(len(self.engine.history), 1)

        self.engine.clear_history()
        self.assertEqual(len(self.engine.history), 0)

    def test_get_history(self):
        """测试获取历史记录。"""
        test_file = os.path.join(self.temp_dir, "test.png")
        with open(test_file, "w") as f:
            f.write("fake image data")

        for i in range(5):
            self.engine._add_to_history(test_file, f"mode_{i}")

        history = self.engine.get_history(limit=3)
        self.assertEqual(len(history), 3)

    def test_capture_fullscreen_no_gui(self):
        """测试无GUI环境下的全屏截图（应失败或使用PIL回退）。"""
        output_dir = os.path.join(self.temp_dir, "screenshots")
        os.makedirs(output_dir, exist_ok=True)

        # 使用 mock 来避免实际截图
        with patch.object(self.engine, '_capture_linux_fullscreen', return_value=False), \
             patch.object(self.engine, '_capture_macos_fullscreen', return_value=False), \
             patch.object(self.engine, '_capture_windows_fullscreen', return_value=False), \
             patch.object(self.engine, '_capture_pil_fullscreen', return_value=False):
            with self.assertRaises(CaptureError):
                self.engine.capture_fullscreen(output_dir=output_dir)

    def test_capture_region_invalid_coords(self):
        """测试无效区域坐标。"""
        output_dir = os.path.join(self.temp_dir, "screenshots")
        os.makedirs(output_dir, exist_ok=True)

        with self.assertRaises(CaptureError):
            self.engine.capture_region(
                output_dir=output_dir,
                region=(500, 500, 100, 100),  # x1 > x2
            )

    def test_prompt_region_cancel(self):
        """测试取消区域选择。"""
        with patch('builtins.input', return_value='q'):
            result = self.engine._prompt_region()
            self.assertIsNone(result)

    def test_prompt_region_invalid_input(self):
        """测试无效的区域输入。"""
        with patch('builtins.input', return_value='invalid'):
            result = self.engine._prompt_region()
            self.assertIsNone(result)

    def test_prompt_region_valid_input(self):
        """测试有效的区域输入。"""
        with patch('builtins.input', return_value='100 100 500 400'):
            result = self.engine._prompt_region()
            self.assertEqual(result, (100, 100, 500, 400))


if __name__ == "__main__":
    unittest.main()
