from charset_normalizer import from_bytes
import html2text
from newspaper import Article, fulltext

from pycorelibs.network.http_utils import HTTPMethod, fetch_url, is_url


class HTMLContent(Article):
    def __init__(self, url, **kwargs):
        self.markdown = None
        super().__init__(url, **kwargs)
        if not is_url(url):
            raise ValueError(f"URL is not correct:\n{url}")
        
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            )
        }
        self.fetch_html(url=url,headers=headers)               

        self.parse()

        if len(self.html) != 0 and len(self.text) == 0:
            # 尝试使用 fulltext 提取
            try:
                extracted_text = fulltext(self.html)
                if extracted_text:
                    self.text = extracted_text.strip()
            except Exception as e:
                print("[WARN] fulltext extraction failed:", e)

            
        if len(self.text or "") == 0:
            self.text = self.safe_html2md(self.html, pure_text=True)
        if len(self.markdown or "") == 0:
            self.markdown = self.safe_html2md(self.html, pure_text=False)
            
                
    @staticmethod
    def safe_html2md(html: str, pure_text: bool = False) -> str:
        """
        将 HTML 转换为 Markdown 或纯文本，具备容错和可控性。
        :param html: HTML 内容
        :param pure_text: True 返回纯文本，False 返回 Markdown
        :return: 转换后的字符串
        """
        
        h = html2text.HTML2Text()
        h.body_width = 0
        h.ignore_links = pure_text
        h.ignore_images = pure_text
        h.skip_internal_links = False
        h.unicode_snob = True
        h.ignore_emphasis = pure_text
        h.ignore_tables = pure_text
        h.protect_links = True
        h.single_line_break = False

        try:
            md_text = h.handle(html)
        except Exception as e:
            print("[WARN] html2text handle failed:", e)
            md_text = html

        return md_text.strip()

    def fetch_html(
        self,
        url: str,
        headers: dict = None,
        proxies: dict = None,
    ) -> None:
        """自动识别编码获取 URL HTML

        Args:
            url (str): URL
            headers (dict, optional): 请求头. Defaults to None.
            proxies (dict, optional): 代理. Defaults to None.

        Raises:
            ConnectionError: 请求发生异常
        """  
        if headers is None:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
                )
            }
    
        result = fetch_url(
            url=url,
            method=HTTPMethod.GET,
            headers=headers,
            # proxies={"http": "http://127.0.0.1:8888"},
            max_retries=2,
        )
        if result["success"]:
            # 自动编码识别
            content = result["content"]
            if isinstance(content, bytes):
                detection = from_bytes(content).best()
                if detection:
                    html_text = detection.str
                else:
                    html_text = content.decode("utf-8", errors="ignore")
            else:
                html_text = content

            self.set_html(html_text)
        else:
            raise ConnectionError(f"[ERROR] Failed to fetch HTML:\n{result['error']}")
                

