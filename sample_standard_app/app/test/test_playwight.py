
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_async_playwright_browser

if __name__ == '__main__':
    from langchain_community.document_loaders import AsyncHtmlLoader

    urls = ["https://www.espn.com", "https://lilianweng.github.io/posts/2023-06-23-agent/"]
    loader = AsyncHtmlLoader(urls)
    docs = loader.load()