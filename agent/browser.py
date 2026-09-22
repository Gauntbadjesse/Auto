from urllib.parse import urlparse
from playwright.async_api import async_playwright

from . import config


class DomainNotAllowed(Exception):
    pass


def _host_allowed(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host == config.ALLOWED_DOMAIN or host.endswith("." + config.ALLOWED_DOMAIN)


class SiteBrowser:
    """Playwright wrapper that refuses to navigate outside ALLOWED_DOMAIN."""

    def __init__(self):
        self._pw = None
        self.browser = None
        self.page = None

    async def start(self):
        self._pw = await async_playwright().start()
        self.browser = await self._pw.chromium.launch(headless=not config.BROWSER_HEADED)
        self.page = await self.browser.new_page()
        # Hard-block any navigation (including redirects/clicks) leaving the allowed domain.
        await self.page.route("**/*", self._guard_route)

    async def _guard_route(self, route, request):
        if request.resource_type == "document" and not _host_allowed(request.url):
            await route.abort()
            return
        await route.continue_()

    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self._pw:
            await self._pw.stop()

    async def goto(self, url: str) -> str:
        if not _host_allowed(url):
            raise DomainNotAllowed(f"Refusing to navigate outside {config.ALLOWED_DOMAIN}: {url}")
        await self.page.goto(url, wait_until="domcontentloaded")
        return await self.read_text()

    async def read_text(self, selector: str = "body") -> str:
        el = self.page.locator(selector).first
        text = await el.inner_text()
        return text[:8000]

    async def click(self, selector: str) -> str:
        await self.page.locator(selector).first.click()
        await self.page.wait_for_load_state("domcontentloaded")
        if not _host_allowed(self.page.url):
            await self.page.go_back()
            raise DomainNotAllowed(f"Click navigated outside {config.ALLOWED_DOMAIN}")
        return await self.read_text()

    async def fill(self, selector: str, value: str) -> str:
        await self.page.locator(selector).first.fill(value)
        return f"Filled {selector!r}"

    async def login(self) -> str:
        if not (config.SITE_USERNAME and config.SITE_PASSWORD):
            return "No SITE_USERNAME/SITE_PASSWORD configured"
        return "Credentials available; use fill()/click() on the login form fields"
