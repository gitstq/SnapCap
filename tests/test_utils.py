"""
工具函数单元测试
"""

import hashlib
import os
import platform
import tempfile
import unittest

from snapcap.utils import (
    Colors,
    calculate_file_hash,
    colored,
    convert_image_format,
    ensure_directory,
    format_file_size,
    generate_timestamp,
    generate_unique_filename,
    get_file_size,
    get_system_info,
    is_gui_available,
    print_error,
    print_info,
    print_success,
    print_warning,
    truncate_text,
)


class TestColors(unittest.TestCase):
    """Colors 常量测试类。"""

    def test_reset_code(self):
        """测试重置颜色码。"""
        self.assertEqual(Colors.RESET, "\033[0m")

    def test_red_code(self):
        """测试红色码。"""
        self.assertEqual(Colors.RED, "\033[31m")

    def test_bold_code(self):
        """测试粗体码。"""
        self.assertEqual(Colors.BOLD, "\033[1m")


class TestColored(unittest.TestCase):
    """colored 函数测试类。"""

    def test_colored_text(self):
        """测试文本着色。"""
        result = colored("hello", Colors.RED)
        self.assertTrue(result.startswith(Colors.RED))
        self.assertTrue(result.endswith(Colors.RESET))
        self.assertIn("hello", result)

    def test_colored_empty_text(self):
        """测试空文本着色。"""
        result = colored("", Colors.RED)
        self.assertEqual(result, Colors.RED + Colors.RESET)


class TestPrintFunctions(unittest.TestCase):
    """打印函数测试类。"""

    def test_print_success(self, *args):
        """测试成功信息打印。"""
        # 只要不抛异常即可
        print_success("test message")

    def test_print_error(self, *args):
        """测试错误信息打印。"""
        print_error("test error")

    def test_print_warning(self, *args):
        """测试警告信息打印。"""
        print_warning("test warning")

    def test_print_info(self, *args):
        """测试信息打印。"""
        print_info("test info")


class TestTimestamp(unittest.TestCase):
    """时间戳生成测试类。"""

    def test_generate_timestamp(self):
        """测试时间戳格式。"""
        ts = generate_timestamp()
        self.assertEqual(len(ts), 15)  # YYYYMMDD_HHMMSS
        self.assertEqual(ts[8], "_")

    def test_generate_unique_filename(self):
        """测试唯一文件名生成。"""
        filename = generate_unique_filename("screenshot", ".png")
        self.assertTrue(filename.startswith("screenshot_"))
        self.assertTrue(filename.endswith(".png"))
        self.assertEqual(len(filename), len("screenshot_") + 15 + len(".png"))

    def test_generate_unique_filename_custom(self):
        """测试自定义前缀和扩展名。"""
        filename = generate_unique_filename("capture", ".jpg")
        self.assertTrue(filename.startswith("capture_"))
        self.assertTrue(filename.endswith(".jpg"))


class TestFileSize(unittest.TestCase):
    """文件大小格式化测试类。"""

    def test_format_bytes(self):
        """测试字节格式化。"""
        self.assertEqual(format_file_size(500), "500.0 B")

    def test_format_kilobytes(self):
        """测试KB格式化。"""
        self.assertEqual(format_file_size(1024), "1.0 KB")

    def test_format_megabytes(self):
        """测试MB格式化。"""
        self.assertEqual(format_file_size(1024 * 1024), "1.0 MB")

    def test_format_gigabytes(self):
        """测试GB格式化。"""
        self.assertEqual(format_file_size(1024 * 1024 * 1024), "1.0 GB")

    def test_format_negative(self):
        """测试负值。"""
        self.assertEqual(format_file_size(-1), "0 B")

    def test_format_zero(self):
        """测试零值。"""
        self.assertEqual(format_file_size(0), "0.0 B")

    def test_get_file_size(self, *args):
        """测试获取文件大小。"""
        temp_dir = tempfile.mkdtemp()
        try:
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, "w") as f:
                f.write("x" * 1024)

            size = get_file_size(test_file)
            self.assertEqual(size, "1.0 KB")
        finally:
            os.remove(test_file)
            os.rmdir(temp_dir)

    def test_get_file_size_not_exists(self, *args):
        """测试获取不存在文件的大小。"""
        size = get_file_size("/nonexistent/file.txt")
        self.assertEqual(size, "N/A")


class TestFileHash(unittest.TestCase):
    """文件哈希计算测试类。"""

    def test_calculate_md5(self):
        """测试 MD5 哈希计算。"""
        temp_dir = tempfile.mkdtemp()
        try:
            test_file = os.path.join(temp_dir, "test.txt")
            content = b"hello world"
            with open(test_file, "wb") as f:
                f.write(content)

            expected = hashlib.md5(content).hexdigest()
            result = calculate_file_hash(test_file, "md5")
            self.assertEqual(result, expected)
        finally:
            os.remove(test_file)
            os.rmdir(temp_dir)

    def test_calculate_sha256(self):
        """测试 SHA256 哈希计算。"""
        temp_dir = tempfile.mkdtemp()
        try:
            test_file = os.path.join(temp_dir, "test.txt")
            content = b"hello world"
            with open(test_file, "wb") as f:
                f.write(content)

            expected = hashlib.sha256(content).hexdigest()
            result = calculate_file_hash(test_file, "sha256")
            self.assertEqual(result, expected)
        finally:
            os.remove(test_file)
            os.rmdir(temp_dir)

    def test_file_not_found(self):
        """测试文件不存在。"""
        with self.assertRaises(FileNotFoundError):
            calculate_file_hash("/nonexistent/file.txt")

    def test_invalid_algorithm(self):
        """测试无效的哈希算法。"""
        temp_dir = tempfile.mkdtemp()
        try:
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test")

            with self.assertRaises(ValueError):
                calculate_file_hash(test_file, "invalid")
        finally:
            os.remove(test_file)
            os.rmdir(temp_dir)


class TestConvertImageFormat(unittest.TestCase):
    """图片格式转换测试类。"""

    def test_convert_png_to_jpeg(self):
        """测试 PNG 转 JPEG。"""
        temp_dir = tempfile.mkdtemp()
        try:
            from PIL import Image

            input_path = os.path.join(temp_dir, "input.png")
            output_path = os.path.join(temp_dir, "output.jpg")

            img = Image.new("RGB", (100, 100), color=(255, 0, 0))
            img.save(input_path, "PNG")

            result = convert_image_format(input_path, output_path)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(output_path))
        finally:
            for f in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, f))
            os.rmdir(temp_dir)

    def test_convert_nonexistent_file(self):
        """测试转换不存在的文件。"""
        result = convert_image_format("/nonexistent/input.png", "/tmp/output.jpg")
        self.assertFalse(result)


class TestEnsureDirectory(unittest.TestCase):
    """ensure_directory 测试类。"""

    def test_ensure_existing_dir(self):
        """测试已存在的目录。"""
        temp_dir = tempfile.mkdtemp()
        try:
            filepath = os.path.join(temp_dir, "test.txt")
            result = ensure_directory(filepath)
            self.assertEqual(result, temp_dir)
        finally:
            os.rmdir(temp_dir)

    def test_ensure_new_dir(self):
        """测试创建新目录。"""
        temp_dir = tempfile.mkdtemp()
        try:
            new_dir = os.path.join(temp_dir, "subdir", "nested")
            filepath = os.path.join(new_dir, "test.txt")
            result = ensure_directory(filepath)
            self.assertTrue(os.path.exists(new_dir))
        finally:
            import shutil
            shutil.rmtree(temp_dir)


class TestGetSystemInfo(unittest.TestCase):
    """get_system_info 测试类。"""

    def test_system_info_keys(self):
        """测试系统信息包含必要的键。"""
        info = get_system_info()
        self.assertIn("os", info)
        self.assertIn("python_version", info)
        self.assertIn("machine", info)


class TestIsGuiAvailable(unittest.TestCase):
    """is_gui_available 测试类。"""

    def test_returns_bool(self):
        """测试返回布尔值。"""
        result = is_gui_available()
        self.assertIsInstance(result, bool)


class TestTruncateText(unittest.TestCase):
    """truncate_text 测试类。"""

    def test_short_text(self):
        """测试短文本不截断。"""
        result = truncate_text("hello", max_length=10)
        self.assertEqual(result, "hello")

    def test_long_text(self):
        """测试长文本截断。"""
        result = truncate_text("a" * 100, max_length=10)
        self.assertEqual(len(result), 10)
        self.assertTrue(result.endswith("..."))

    def test_exact_length(self):
        """测试恰好等于最大长度。"""
        text = "hello"
        result = truncate_text(text, max_length=5)
        self.assertEqual(result, "hello")


if __name__ == "__main__":
    unittest.main()
