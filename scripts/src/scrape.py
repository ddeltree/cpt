import httpx, asyncio, csv
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Set
from httpx import ConnectError
from ssl import SSLCertVerificationError

from utils.RateLimitedClient import RateLimitedClient
from utils.globals import HTML_DIR, DEAD_LINKS_PATH, ROOT_URL, REDIRECTS_CSV_PATH
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


async def get_head_info(route: str):
    head = await CLIENT.head(route, follow_redirects=True)
    is_html = "text/html" in head.headers.get("content-type")
    redirect = str(head.url)
    redirect = redirect if redirect != route else None
    if redirect:
        print(warn("[redirect]"), redirect)
    return (is_html, redirect, head)


async def fetch_route(route: str):
    print(route)
    is_html, redirect, response = await get_head_info(route)
    html = (await CLIENT.get(route)).text if is_html else None
    if redirect and not redirect.startswith(ROOT_URL):
        html = None
    else:
        response.raise_for_status()
    return route, redirect, html


def should_skip(url: str, e: Exception | None = None):
    if e:
        print(err("[ERRO]"), url)
    return url in SKIP_URLS or any(map(lambda x: x in str(e), SKIP_URLS))


async def try_fetch_route(route: str):
    result = None
    try:
        if not should_skip(route):
            result = await fetch_route(route)
    except SSLCertVerificationError:
        pass
    except ConnectError:
        pass
    except Exception as e:
        print(err("[ERRO]"), route)
        print(err(e))
        raise e
    return result


async def fetch_next_html(url: str):
    if not url.startswith(ROOT_URL):
        raise Exception(f"{url} não é rota")
    done_routes.add(url)
    next_routes.discard(url)
    return await try_fetch_route(url)


async def fetch_html_batch():
    return filter(bool, await asyncio.gather(*map(fetch_next_html, next_routes)))


def find_page_links(html: str):
    soup = BeautifulSoup(html, "html.parser")
    for link in soup.find_all("a"):
        attrs = link.get_attribute_list("href")
        href: str = (attrs[:1] or [""])[0] or ""
        if not href.startswith("/") and not href.startswith("http"):
            continue
        href = href if href.startswith("http") else ROOT_URL + href
        if href not in done_routes and href.startswith(ROOT_URL):
            next_routes.add(href)


def remove_dead_links(html: str):
    for url in SKIP_URLS:
        html = html.replace(url, "#")
    return html


def redirects_writerow(route, redirect):
    if not redirect:
        raise Exception(f"Inesperado: sem html e sem redirect\n{route}")
    with REDIRECTS_CSV_PATH.open("a") as f:
        file = csv.writer(f)
        file.writerow([route, redirect])


async def process_next_batch():
    for route, redirect, html in await fetch_html_batch():
        if not html:
            redirects_writerow(route, redirect)
            continue
        html = remove_dead_links(html)
        if not get_filename_from_url(route).exists():
            write_html(route, html)
        find_page_links(html)


async def async_main():
    while next_routes:
        await process_next_batch()


def main():
    asyncio.run(async_main())


# rotas da url raiz do curso
next_routes = {ROOT_URL}
done_routes: Set[str] = set()
CLIENT = RateLimitedClient(interval=0, count=7, timeout=60, follow_redirects=True)
SKIP_URLS = DEAD_LINKS_PATH.read_text().splitlines()
