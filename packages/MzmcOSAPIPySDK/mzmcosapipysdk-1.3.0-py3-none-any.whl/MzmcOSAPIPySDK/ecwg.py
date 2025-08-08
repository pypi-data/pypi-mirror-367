from typing import Dict, Any

try:
    from .request import Get
except Exception:
    from request import Get


class EaverseAPIClient:
    """
    EaverseAPI SDK 客户端

    提供对MzmcAPI的访问接口,支持资源链接获取功能
    """

    def __init__(self, base_url: str = "https://mzmc-api.eaverse.top"):
        """
        初始化客户端

        Args:
            base_url: API基础地址，默认使用官方地址
        """
        self.base_url = base_url
        self.headers = {"User-Agent": "MzmcAPISDK/1.0"}

    def get_launcher_link(self) -> Dict[str, Any]:
        """
        获取启动器下载链接
        """
        url = "/api/v2/link/launcher"
        with Get(base_url=self.base_url, endpoint=url) as api:
            return api.get(header=self.headers)


if __name__ == "__main__":
    client = EaverseAPIClient()

