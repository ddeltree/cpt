import httpx, asyncio, csv, shutil
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Set
from httpx import ConnectError
from ssl import SSLCertVerificationError

from utils.globals import (
    HTML_DIR,
    ROOT_URL,
    REDIRECTS_CSV_PATH,
    LINKS_PATH,
    SKIP_URLS,
    UTILS_DIR,
)
from utils.exceptions import NotFoundError, LinkedinDeniedError
from utils.fn import err, warn, ok, extract_links


def main():
    REDIRECTS_CSV_PATH.unlink(missing_ok=True)
    asyncio.run(async_main())
    LINKS_PATH.write_text("\n".join(all_links))
    shutil.copy(LINKS_PATH, UTILS_DIR)


async def async_main():
    while next_routes:
        await process_next_batch()


async def process_next_batch():
    batch = list(await fetch_html_batch())

    redirects = filter(lambda x: not x[2] and x[1], batch)
    redirects_writerows(redirects)

    resources = filter(lambda x: not x[2] and not x[1], batch)
    for route, _, _ in resources:
        print(ok("[RECURSO]"), route)

    documents = filter(lambda x: x[2], batch)
    save_html_batch(documents)


async def fetch_html_batch():
    return filter(bool, await asyncio.gather(*map(fetch_next_html, next_routes)))


async def fetch_next_html(url: str):
    if not url.startswith(ROOT_URL):
        raise Exception(f"{url} não é rota")
    done_routes.add(url)
    next_routes.discard(url)
    return await try_fetch_route(url)


async def try_fetch_route(route: str):
    result = None
    try:
        if not should_skip(route):
            result = await fetch_route(route)
    except SSLCertVerificationError:
        pass
    except ConnectError:
        pass
    except NotFoundError:
        pass
    except LinkedinDeniedError:
        pass
    except Exception as e:
        print(err("[ERRO]"), route)
        print(err(e))
        raise e
    return result


def should_skip(url: str, e: Exception | None = None):
    if e:
        print(err("[ERRO]"), url)
    return url in SKIP_URLS or any(map(lambda x: x in str(e), SKIP_URLS))


async def fetch_route(route: str):
    is_html, redirect, response = await get_head_info(route)
    if not is_html or redirect and not redirect.startswith(ROOT_URL):
        html = None
    else:
        if response.status_code == 404:
            raise NotFoundError()
        elif response.status_code in (999, 429) and "linkedin" in route:
            raise LinkedinDeniedError()
        response.raise_for_status()
        html = (await CLIENT.get(route)).text
    return route, redirect, html


async def get_head_info(route: str):
    head = await CLIENT.head(route, follow_redirects=True)
    is_html = "text/html" in (head.headers.get("content-type") or [])
    redirect = str(head.url)
    redirect = redirect if redirect != route else None
    return (is_html, redirect, head)


def redirects_writerows(redirects):
    with REDIRECTS_CSV_PATH.open("a") as f:
        for route, redirect, _ in redirects:
            print(route)
            print(warn("[redirect]"), redirect)
            file = csv.writer(f)
            file.writerow([route, redirect])


def save_html_batch(documents):
    for route, _, html in documents:
        print(route)
        html = remove_dead_links(html)
        if not get_filename_from_url(route).exists():
            write_html(route, html)
        find_page_links(html)


def remove_dead_links(html: str):
    # for url in SKIP_URLS:
    #     html = html.replace(url, "#")
    return extract_links(SKIP_URLS, html)


def write_html(url, html):
    file = get_filename_from_url(url)
    touch_deep(file)
    file.write_text(html, "utf-8")


def get_filename_from_url(url: str):
    name = url.replace(ROOT_URL, "")
    name = name[1:] if name.startswith("/") else name
    return HTML_DIR / name / "index.html"


def touch_deep(path: Path):
    directory = path.parent if path.suffix == ".html" else path
    directory.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)


def find_page_links(html: str):
    soup = BeautifulSoup(html, "html.parser")
    for link in soup.find_all("a"):
        attrs = link.get_attribute_list("href")
        href: str = (attrs[:1] or [""])[0] or ""
        all_links.add(href)
        if not href.startswith("/") and not href.startswith("http"):
            continue
        href = href if href.startswith("http") else ROOT_URL + href
        if href not in done_routes and href.startswith(ROOT_URL):
            next_routes.add(href)
    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            if src not in all_links:
                print(ok("[IMG]"), src)
            all_links.add(src)


# rotas da url raiz do curso
all_links: Set[str] = set()
next_routes = {ROOT_URL}
done_routes: Set[str] = set()
CLIENT = httpx.AsyncClient(follow_redirects=True, timeout=60)
