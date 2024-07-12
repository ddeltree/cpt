import httpx, asyncio
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Set
from httpx import AsyncClient


class RateLimitedClient(AsyncClient):
    # https://github.com/encode/httpx/issues/815#issuecomment-1625374321
    _bg_tasks: Set[asyncio.Task] = set()

    def __init__(self, interval: float = 1, count=1, **kwargs):
        self.interval = interval
        self.semaphore = asyncio.Semaphore(count)
        super().__init__(**kwargs)

    def _schedule_semaphore_release(self):
        wait = asyncio.create_task(asyncio.sleep(self.interval))
        RateLimitedClient._bg_tasks.add(wait)

        def wait_cb(task):
            self.semaphore.release()
            RateLimitedClient._bg_tasks.discard(task)

        wait.add_done_callback(wait_cb)

    async def send(self, *args, **kwargs):
        await self.semaphore.acquire()
        send = asyncio.create_task(super().send(*args, **kwargs))
        self._schedule_semaphore_release()
        return await send


CLIENT = RateLimitedClient(interval=1, count=2, timeout=60, follow_redirects=True)
ROOT_URL = "https://arapiraca.ufal.br/graduacao/ciencia-da-computacao"
HTML_DIR = Path("html").absolute()


def get_filename_from_url(url: str):
    name = url.replace(ROOT_URL, "")
    name = name[1:] if name.startswith("/") else name
    return HTML_DIR / name / "index.html"


def touch_deep(path: Path):
    directory = path.parent if path.suffix == ".html" else path
    directory.mkdir(parents=True, exist_ok=True)
    path.touch()


def write_html(url, html):
    file = get_filename_from_url(url)
    touch_deep(file)
    file.write_text(html, "utf-8")


def is_html(r: httpx.Response):
    return "text/html" in r.headers.get("content-type")


async def fetch_url(url: str):
    try:
        r = await CLIENT.get(url)
        return r.text if is_html(r) else None
    except:
        print("\033[31m" "[ERRO]" "\033[0m", url)


async def fetch_next_html(url: str):
    done_urls.add(url)
    next_urls.discard(url)
    html = await fetch_url(url)
    if html:
        print(url)
    return url, html


async def fetch_html_batch():
    return await asyncio.gather(*map(fetch_next_html, next_urls))


def find_page_links(html: str):
    soup = BeautifulSoup(html, "html.parser")
    for link in soup.find_all("a"):
        attrs = link.get_attribute_list("href")
        href: str = (attrs[:1] or [""])[0] or ""
        if not href.startswith("/") and not href.startswith("http"):
            continue
        href = href if href.startswith("http") else ROOT_URL + href
        if href not in done_urls and href.startswith(ROOT_URL):
            next_urls.add(href)


async def process_next_batch():
    for url, html in await fetch_html_batch():
        if not html:
            continue
        if not get_filename_from_url(url).exists():
            write_html(url, html)
        find_page_links(html)


async def main():
    while next_urls:
        await process_next_batch()


next_urls = {ROOT_URL}
done_urls: Set[str] = set()
asyncio.run(main())
