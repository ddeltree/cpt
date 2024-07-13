import httpx, asyncio
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Set
from httpx import AsyncClient, ConnectError
from ssl import SSLCertVerificationError


class HostRedirectError(Exception):
    pass


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


CLIENT = RateLimitedClient(interval=0, count=7, timeout=60, follow_redirects=True)
ROOT_URL = "https://arapiraca.ufal.br/graduacao/ciencia-da-computacao"
HTML_DIR = Path("html").absolute()
SKIP_URLS = Path("dead_links.txt").read_text().splitlines()


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


def err(msg):
    return f"\033[31m{msg}\033[0m"


def warn(msg):
    return f"\033[33m{msg}\033[0m"


def should_skip(url: str, e: Exception | None = None):
    if e:
        print(err("[ERRO]"), url)
    return url in SKIP_URLS or any(map(lambda x: x in str(e), SKIP_URLS))


async def fetch_url(url: str):
    r = await CLIENT.get(url)
    print(url)
    if url != str(r.url):
        url = str(r.url)
        print(warn("[redirect]"), r.url)
        if not str(r.url).startswith(ROOT_URL):
            raise HostRedirectError()
    r.raise_for_status()
    return (url, r.text) if is_html(r) else None


async def try_fetch_url(url: str):
    result = None
    try:
        if not should_skip(url):
            result = await fetch_url(url)
    except SSLCertVerificationError:
        pass
    except HostRedirectError:
        pass
    except ConnectError:
        pass
    except Exception as e:
        print(err("[ERRO]"), url)
        print(err(e))
        raise e
    return result


async def fetch_next_html(url: str):
    done_urls.add(url)
    next_urls.discard(url)
    return await try_fetch_url(url)


async def fetch_html_batch():
    return filter(bool, await asyncio.gather(*map(fetch_next_html, next_urls)))


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
    docs = await fetch_html_batch()
    for url, html in docs:
        if not get_filename_from_url(url).exists():
            write_html(url, html)
        find_page_links(html)


async def main():
    while next_urls:
        await process_next_batch()


next_urls = {
    "https://arapiraca.ufal.br/graduacao/ciencia-da-computacao/documentos/tcc/modelos/modelo-tcc-tradicional-doc-sibi-ufal"
}
done_urls: Set[str] = set()
asyncio.run(main())
