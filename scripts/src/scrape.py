import httpx, asyncio
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Set
from httpx import ConnectError
from ssl import SSLCertVerificationError

from utils.RateLimitedClient import RateLimitedClient
from utils.HostRedirectError import HostRedirectError
from utils.globals import HTML_DIR, DEAD_LINKS_PATH, ROOT_URL
from utils.fn import err, warn


def get_filename_from_url(url: str):
    name = url.replace(ROOT_URL, "")
    name = name[1:] if name.startswith("/") else name
    return HTML_DIR / name / "index.html"


def touch_deep(path: Path):
    directory = path.parent if path.suffix == ".html" else path
    directory.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)


def write_html(url, html):
    file = get_filename_from_url(url)
    touch_deep(file)
    file.write_text(html, "utf-8")


def is_html(r: httpx.Response):
    return "text/html" in r.headers.get("content-type")


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


def remove_dead_links(html: str | None):
    if not html:
        return html
    for url in SKIP_URLS:
        html = html.replace(url, "#")
    return html


async def process_next_batch():
    docs = await fetch_html_batch()
    for url, html in docs:
        html = remove_dead_links(html)
        if not get_filename_from_url(url).exists():
            write_html(url, html)
        find_page_links(html)


async def async_main():
    while next_urls:
        await process_next_batch()


def main():
    asyncio.run(async_main())


next_urls = {ROOT_URL}
done_urls: Set[str] = set()
CLIENT = RateLimitedClient(interval=0, count=7, timeout=60, follow_redirects=True)
SKIP_URLS = DEAD_LINKS_PATH.read_text().splitlines()
