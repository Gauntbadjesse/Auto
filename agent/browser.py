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
        return await self.look()

    async def read_text(self, selector: str = "body") -> str:
        el = self.page.locator(selector).first
        text = await el.inner_text()
        return text[:8000]

    async def look(self) -> str:
        """Like a human scanning the page: numbered list of visible, clickable/typeable
        elements with their labels. click()/type() refer to elements by this number."""
        elements = await self.page.evaluate(_SNAPSHOT_JS)
        if not elements:
            return "(no interactive elements visible)"
        lines = []
        for el in elements:
            desc = f'[{el["id"]}] {el["tag"]}'
            if el["type"]:
                desc += f'[{el["type"]}]'
            if el["text"]:
                desc += f' "{el["text"]}"'
            lines.append(desc)
        return "\n".join(lines)

    async def click(self, element_id: int) -> str:
        locator = self.page.locator(f'[data-agent-id="{element_id}"]')
        if await locator.count() == 0:
            return f"No such element [{element_id}] - call look() again, the page may have changed"
        await locator.first.click()
        await self.page.wait_for_load_state("domcontentloaded")
        if not _host_allowed(self.page.url):
            await self.page.go_back()
            raise DomainNotAllowed(f"Click navigated outside {config.ALLOWED_DOMAIN}")
        return await self.look()

    async def type(self, element_id: int, value: str) -> str:
        locator = self.page.locator(f'[data-agent-id="{element_id}"]')
        if await locator.count() == 0:
            return f"No such element [{element_id}] - call look() again, the page may have changed"
        await locator.first.fill(value)
        return f"Typed into [{element_id}]"

    async def login(self) -> str:
        if not (config.SITE_USERNAME and config.SITE_PASSWORD):
            return "No SITE_USERNAME/SITE_PASSWORD configured"
        return "Credentials available; use look() to find the username/password fields, then type()/click()"


_SNAPSHOT_JS = """
() => {
  const isVisible = (el) => {
    const r = el.getBoundingClientRect();
    const style = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
  };
  const els = Array.from(document.querySelectorAll(
    'a, button, input, textarea, select, [role="button"], [onclick]'
  )).filter(isVisible);
  return els.map((el, i) => {
    el.setAttribute('data-agent-id', String(i));
    const text = (
      el.innerText || el.value || el.getAttribute('aria-label') ||
      el.getAttribute('placeholder') || el.getAttribute('title') || ''
    ).trim().replace(/\\s+/g, ' ').slice(0, 80);
    return { id: i, tag: el.tagName.toLowerCase(), type: el.getAttribute('type') || '', text };
  });
}
"""
