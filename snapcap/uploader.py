"""
图床上传模块

支持将图片上传到多种图床服务，包括 file.io、imgbb 和自定义 API。
上传后返回直链 URL，支持 Markdown 格式链接输出。
"""

import json
import os
import sys
from typing import Any, Dict, Optional
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from .utils import print_error, print_info, print_success, print_warning


class UploadError(Exception):
    """上传操作异常。"""

    pass


class Uploader:
    """图床上传器基类。

    定义上传器的通用接口。

    Attributes:
        filepath: 要上传的图片文件路径。
    """

    def __init__(self, filepath: str) -> None:
        """初始化上传器。

        Args:
            filepath: 要上传的图片文件路径。

        Raises:
            FileNotFoundError: 当文件不存在时。
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")
        self.filepath = os.path.abspath(filepath)

    def upload(self) -> Dict[str, str]:
        """上传文件到图床。

        Returns:
            包含上传结果的字典，至少包含 'url' 键。

        Raises:
            UploadError: 当上传失败时。
        """
        raise NotImplementedError("子类必须实现 upload 方法")

    def _read_file(self) -> bytes:
        """读取文件内容。

        Returns:
            文件的二进制内容。
        """
        with open(self.filepath, "rb") as f:
            return f.read()


class FileIOUploader(Uploader):
    """file.io 图床上传器。

    使用 file.io 免费临时文件托管服务上传文件。
    注意：file.io 的文件会在一定时间后过期。
    """

    API_URL = "https://file.io"

    def upload(self) -> Dict[str, str]:
        """上传文件到 file.io。

        Returns:
            包含 'url'、'key'、'expiry' 的字典。

        Raises:
            UploadError: 当上传失败时。
        """
        import mimetypes

        file_data = self._read_file()
        filename = os.path.basename(self.filepath)
        mime_type = mimetypes.guess_type(self.filepath)[0] or "image/png"

        boundary = "----SnapCapBoundary7MA4YWxkTrZu0gW"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f"Content-Type: {mime_type}\r\n\r\n"
        ).encode("utf-8")
        body += file_data
        body += f"\r\n--{boundary}--\r\n".encode("utf-8")

        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        }

        try:
            request = Request(self.API_URL, data=body, headers=headers, method="POST")
            with urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))

            if result.get("success", False):
                return {
                    "url": result["link"],
                    "key": result.get("key", ""),
                    "expiry": result.get("expiry", "unknown"),
                    "provider": "file.io",
                }
            else:
                raise UploadError(f"file.io 上传失败: {result.get('error', '未知错误')}")

        except (URLError, HTTPError) as e:
            raise UploadError(f"file.io 上传网络错误: {e}")
        except json.JSONDecodeError as e:
            raise UploadError(f"file.io 响应解析失败: {e}")


class ImgBBUploader(Uploader):
    """ImgBB 图床上传器。

    使用 ImgBB 免费图片托管服务上传文件。
    需要提供 API Key，可在 https://api.imgbb.com/ 免费获取。
    """

    API_URL = "https://api.imgbb.com/1/upload"

    def __init__(self, filepath: str, api_key: str) -> None:
        """初始化 ImgBB 上传器。

        Args:
            filepath: 图片文件路径。
            api_key: ImgBB API Key。

        Raises:
            ValueError: 当 API Key 为空时。
        """
        super().__init__(filepath)
        if not api_key:
            raise ValueError("ImgBB 上传需要 API Key，请在 https://api.imgbb.com/ 获取")
        self.api_key = api_key

    def upload(self) -> Dict[str, str]:
        """上传文件到 ImgBB。

        Returns:
            包含 'url'、'thumb_url'、'delete_url'、'display_url' 的字典。

        Raises:
            UploadError: 当上传失败时。
        """
        import base64
        import mimetypes

        file_data = self._read_file()
        filename = os.path.basename(self.filepath)
        mime_type = mimetypes.guess_type(self.filepath)[0] or "image/png"

        boundary = "----SnapCapBoundary7MA4YWxkTrZu0gW"

        # API Key 字段
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="key"\r\n\r\n'
            f"{self.api_key}\r\n"
        ).encode("utf-8")

        # Base64 编码的图片数据
        encoded_data = base64.b64encode(file_data).decode("utf-8")
        body += (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="image"\r\n\r\n'
            f"{encoded_data}\r\n"
        ).encode("utf-8")

        # 文件名
        body += (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="name"\r\n\r\n'
            f"{filename}\r\n"
        ).encode("utf-8")

        body += f"--{boundary}--\r\n".encode("utf-8")

        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        }

        try:
            request = Request(self.API_URL, data=body, headers=headers, method="POST")
            with urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))

            if result.get("success", False):
                data = result["data"]
                return {
                    "url": data["url"],
                    "display_url": data.get("display_url", data["url"]),
                    "thumb_url": data.get("thumb", {}).get("url", ""),
                    "delete_url": data.get("delete_url", ""),
                    "provider": "imgbb",
                }
            else:
                raise UploadError(f"ImgBB 上传失败: {result.get('error', {}).get('message', '未知错误')}")

        except (URLError, HTTPError) as e:
            raise UploadError(f"ImgBB 上传网络错误: {e}")
        except json.JSONDecodeError as e:
            raise UploadError(f"ImgBB 响应解析失败: {e}")


class CustomUploader(Uploader):
    """自定义 API 图床上传器。

    支持用户自定义上传端点，可配置请求头和响应解析。
    """

    def __init__(
        self,
        filepath: str,
        endpoint: str,
        field_name: str = "file",
        headers: Optional[Dict[str, str]] = None,
        response_url_path: str = "data.url",
    ) -> None:
        """初始化自定义上传器。

        Args:
            filepath: 图片文件路径。
            endpoint: 自定义 API 端点 URL。
            field_name: 文件字段名，默认为 'file'。
            headers: 自定义请求头。
            response_url_path: 响应中 URL 的 JSON 路径，用点号分隔，默认为 'data.url'。
        """
        super().__init__(filepath)
        self.endpoint = endpoint
        self.field_name = field_name
        self.headers = headers or {}
        self.response_url_path = response_url_path

    def upload(self) -> Dict[str, str]:
        """上传文件到自定义 API。

        Returns:
            包含 'url' 和 'provider' 的字典。

        Raises:
            UploadError: 当上传失败时。
        """
        import mimetypes

        file_data = self._read_file()
        filename = os.path.basename(self.filepath)
        mime_type = mimetypes.guess_type(self.filepath)[0] or "image/png"

        boundary = "----SnapCapBoundary7MA4YWxkTrZu0gW"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{self.field_name}"; filename="{filename}"\r\n'
            f"Content-Type: {mime_type}\r\n\r\n"
        ).encode("utf-8")
        body += file_data
        body += f"\r\n--{boundary}--\r\n".encode("utf-8")

        req_headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            **self.headers,
        }

        try:
            request = Request(self.endpoint, data=body, headers=req_headers, method="POST")
            with urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))

            # 从响应中提取 URL
            url = self._extract_url(result)
            if url:
                return {
                    "url": url,
                    "raw_response": json.dumps(result, ensure_ascii=False),
                    "provider": "custom",
                }
            else:
                raise UploadError(f"无法从响应中提取 URL (路径: {self.response_url_path})")

        except (URLError, HTTPError) as e:
            raise UploadError(f"自定义 API 上传网络错误: {e}")
        except json.JSONDecodeError as e:
            raise UploadError(f"自定义 API 响应解析失败: {e}")

    def _extract_url(self, data: Any) -> Optional[str]:
        """从 JSON 响应中按照指定路径提取 URL。

        Args:
            data: JSON 响应数据。

        Returns:
            提取到的 URL 字符串，失败返回 None。
        """
        keys = self.response_url_path.split(".")
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        if isinstance(current, str) and current:
            return current
        return None


def upload_image(
    filepath: str,
    provider: str = "fileio",
    api_key: str = "",
    endpoint: str = "",
    field_name: str = "file",
    headers: Optional[Dict[str, str]] = None,
    response_url_path: str = "data.url",
) -> Dict[str, str]:
    """上传图片到指定图床。

    工厂函数，根据提供商名称创建对应的上传器并执行上传。

    Args:
        filepath: 图片文件路径。
        provider: 图床提供商名称，支持 'fileio'、'imgbb'、'custom'。
        api_key: API 密钥（imgbb 需要）。
        endpoint: 自定义 API 端点（custom 需要）。
        field_name: 自定义文件字段名。
        headers: 自定义请求头。
        response_url_path: 自定义响应 URL 路径。

    Returns:
        包含上传结果的字典。

    Raises:
        UploadError: 当上传失败时。
        ValueError: 当提供商名称无效时。
    """
    provider = provider.lower()

    if provider == "fileio":
        uploader: Uploader = FileIOUploader(filepath)
    elif provider == "imgbb":
        uploader = ImgBBUploader(filepath, api_key=api_key)
    elif provider == "custom":
        if not endpoint:
            raise ValueError("自定义上传需要指定 --endpoint 参数")
        uploader = CustomUploader(
            filepath,
            endpoint=endpoint,
            field_name=field_name,
            headers=headers,
            response_url_path=response_url_path,
        )
    else:
        raise ValueError(f"不支持的图床提供商: {provider}，支持: fileio, imgbb, custom")

    print_info(f"正在上传到 {provider}...")
    result = uploader.upload()
    return result


def format_upload_result(result: Dict[str, str], output_format: str = "url") -> str:
    """格式化上传结果输出。

    Args:
        result: 上传结果字典。
        output_format: 输出格式，支持 'url'、'markdown'、'html'、'json'。

    Returns:
        格式化后的字符串。
    """
    url = result.get("url", "")
    provider = result.get("provider", "unknown")

    if output_format == "url":
        return url
    elif output_format == "markdown":
        return f"![image]({url})"
    elif output_format == "html":
        return f'<img src="{url}" alt="uploaded image" />'
    elif output_format == "json":
        return json.dumps(result, indent=2, ensure_ascii=False)
    else:
        return url
