"""
图床上传模块单元测试
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock, mock_open
from urllib.error import URLError

from snapcap.uploader import (
    FileIOUploader,
    ImgBBUploader,
    CustomUploader,
    UploadError,
    format_upload_result,
    upload_image,
)


class TestFileIOUploader(unittest.TestCase):
    """FileIOUploader 测试类。"""

    def setUp(self):
        """测试前准备。"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.png")
        with open(self.test_file, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

    def tearDown(self):
        """测试后清理。"""
        if os.path.exists(self.temp_dir):
            for f in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, f))
            os.rmdir(self.temp_dir)

    def test_init(self):
        """测试初始化。"""
        uploader = FileIOUploader(self.test_file)
        self.assertEqual(uploader.filepath, os.path.abspath(self.test_file))

    def test_init_file_not_found(self):
        """测试文件不存在。"""
        with self.assertRaises(FileNotFoundError):
            FileIOUploader("/nonexistent/file.png")

    @patch("snapcap.uploader.urlopen")
    def test_upload_success(self, mock_urlopen):
        """测试上传成功。"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "success": True,
            "link": "https://file.io/abc123",
            "key": "abc123",
            "expiry": "14d",
        }).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        uploader = FileIOUploader(self.test_file)
        result = uploader.upload()

        self.assertEqual(result["url"], "https://file.io/abc123")
        self.assertEqual(result["provider"], "file.io")
        self.assertEqual(result["key"], "abc123")

    @patch("snapcap.uploader.urlopen")
    def test_upload_failure(self, mock_urlopen):
        """测试上传失败。"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "success": False,
            "error": "Upload failed",
        }).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        uploader = FileIOUploader(self.test_file)
        with self.assertRaises(UploadError):
            uploader.upload()

    @patch("snapcap.uploader.urlopen", side_effect=URLError("Network error"))
    def test_upload_network_error(self, mock_urlopen):
        """测试网络错误。"""
        uploader = FileIOUploader(self.test_file)
        with self.assertRaises(UploadError):
            uploader.upload()


class TestImgBBUploader(unittest.TestCase):
    """ImgBBUploader 测试类。"""

    def setUp(self):
        """测试前准备。"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.png")
        with open(self.test_file, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

    def tearDown(self):
        """测试后清理。"""
        if os.path.exists(self.temp_dir):
            for f in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, f))
            os.rmdir(self.temp_dir)

    def test_init_no_api_key(self):
        """测试无 API Key 初始化。"""
        with self.assertRaises(ValueError):
            ImgBBUploader(self.test_file, api_key="")

    def test_init_with_api_key(self):
        """测试有 API Key 初始化。"""
        uploader = ImgBBUploader(self.test_file, api_key="test_key")
        self.assertEqual(uploader.api_key, "test_key")

    @patch("snapcap.uploader.urlopen")
    def test_upload_success(self, mock_urlopen):
        """测试上传成功。"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "success": True,
            "data": {
                "url": "https://i.ibb.co/test/image.png",
                "display_url": "https://i.ibb.co/test/image.png",
                "thumb": {"url": "https://i.ibb.co/test/thumb.png"},
                "delete_url": "https://ibb.co/delete/token",
            },
        }).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        uploader = ImgBBUploader(self.test_file, api_key="test_key")
        result = uploader.upload()

        self.assertEqual(result["url"], "https://i.ibb.co/test/image.png")
        self.assertEqual(result["provider"], "imgbb")
        self.assertEqual(result["thumb_url"], "https://i.ibb.co/test/thumb.png")


class TestCustomUploader(unittest.TestCase):
    """CustomUploader 测试类。"""

    def setUp(self):
        """测试前准备。"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.png")
        with open(self.test_file, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

    def tearDown(self):
        """测试后清理。"""
        if os.path.exists(self.temp_dir):
            for f in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, f))
            os.rmdir(self.temp_dir)

    def test_init(self):
        """测试初始化。"""
        uploader = CustomUploader(
            self.test_file,
            endpoint="https://example.com/upload",
        )
        self.assertEqual(uploader.endpoint, "https://example.com/upload")

    @patch("snapcap.uploader.urlopen")
    def test_upload_success(self, mock_urlopen):
        """测试上传成功。"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "data": {"url": "https://example.com/image.png"},
        }).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        uploader = CustomUploader(
            self.test_file,
            endpoint="https://example.com/upload",
        )
        result = uploader.upload()

        self.assertEqual(result["url"], "https://example.com/image.png")
        self.assertEqual(result["provider"], "custom")

    @patch("snapcap.uploader.urlopen")
    def test_upload_no_url_in_response(self, mock_urlopen):
        """测试响应中没有 URL。"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "error": "something went wrong",
        }).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        uploader = CustomUploader(
            self.test_file,
            endpoint="https://example.com/upload",
        )
        with self.assertRaises(UploadError):
            uploader.upload()


class TestFormatUploadResult(unittest.TestCase):
    """format_upload_result 测试类。"""

    def test_format_url(self):
        """测试 URL 格式。"""
        result = {"url": "https://example.com/image.png", "provider": "fileio"}
        formatted = format_upload_result(result, "url")
        self.assertEqual(formatted, "https://example.com/image.png")

    def test_format_markdown(self):
        """测试 Markdown 格式。"""
        result = {"url": "https://example.com/image.png", "provider": "fileio"}
        formatted = format_upload_result(result, "markdown")
        self.assertEqual(formatted, "![image](https://example.com/image.png)")

    def test_format_html(self):
        """测试 HTML 格式。"""
        result = {"url": "https://example.com/image.png", "provider": "fileio"}
        formatted = format_upload_result(result, "html")
        self.assertEqual(formatted, '<img src="https://example.com/image.png" alt="uploaded image" />')

    def test_format_json(self):
        """测试 JSON 格式。"""
        result = {"url": "https://example.com/image.png", "provider": "fileio"}
        formatted = format_upload_result(result, "json")
        parsed = json.loads(formatted)
        self.assertEqual(parsed["url"], "https://example.com/image.png")


class TestUploadImage(unittest.TestCase):
    """upload_image 工厂函数测试类。"""

    def setUp(self):
        """测试前准备。"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.png")
        with open(self.test_file, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

    def tearDown(self):
        """测试后清理。"""
        if os.path.exists(self.temp_dir):
            for f in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, f))
            os.rmdir(self.temp_dir)

    def test_invalid_provider(self):
        """测试无效的提供商。"""
        with self.assertRaises(ValueError):
            upload_image(self.test_file, provider="invalid")

    def test_custom_no_endpoint(self):
        """测试自定义上传无端点。"""
        with self.assertRaises(ValueError):
            upload_image(self.test_file, provider="custom")

    @patch("snapcap.uploader.urlopen")
    def test_upload_fileio(self, mock_urlopen):
        """测试 fileio 上传。"""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "success": True,
            "link": "https://file.io/test",
            "key": "test",
            "expiry": "14d",
        }).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = upload_image(self.test_file, provider="fileio")
        self.assertEqual(result["url"], "https://file.io/test")


if __name__ == "__main__":
    unittest.main()
