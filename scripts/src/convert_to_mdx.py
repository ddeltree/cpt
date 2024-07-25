import shutil, asyncio
from bs4 import BeautifulSoup
from pathlib import Path
from markdownify import markdownify
from httpx import ConnectError
from ssl import SSLCertVerificationError

from src.scrape import get_head_info
from utils.globals import HTML_DIR, MD_DIR, ROOT_URL, PAGES_DIR, LINKS_PATH, SKIP_URLS
from utils.fn import extract_links, warn

LINKS: list[str] | None = None


def main():
    global LINKS
    LINKS = LINKS_PATH.read_text().splitlines()
    asyncio.run(async_main())


async def async_main():
    if MD_DIR.is_dir():
        shutil.rmtree(MD_DIR)
    await pages_to_mdx()
    shutil.copytree(MD_DIR, PAGES_DIR, dirs_exist_ok=True)


async def pages_to_mdx():
    paths = [path for path in HTML_DIR.rglob("*.html")]
    docs = [p.read_text("utf-8") for p in paths]
    docs = await gather_filtered_docs([*docs])
    for path, html in zip(paths, docs):
        html_to_mdx(html, path)


async def gather_filtered_docs(docs: list[str]):
    return await asyncio.gather(*map(filter_links, docs))


async def filter_links(html: str):
    links = [*LINKS]
    links = list(filter(lambda l: l and l in html, links))
    html = remove_relative_links(links, html)
    html = remove_plone_links(links, html)
    html = update_relative_anchors(links, html)
    html = await remove_dead_links(links, html)
    return html


def remove_relative_links(links: list[str], html: str):
    links = [x for x in links if x.startswith(".")]
    return extract_links(links, html) if links else html


def remove_plone_links(links: list[str], html: str):
    links = [x for x in links if x.startswith("/")]
    return extract_links(links, html) if links else html


def update_relative_anchors(links: list[str], html: str):
    links = [x for x in links if x.startswith(ROOT_URL)]
    if not links:
        return html
    soup = BeautifulSoup(html, "html.parser")
    for link in links:
        for anchor in soup.find_all("a", href=link):
            anchor["href"] = link.replace(ROOT_URL, "/cpt")
            anchor = soup.find_next("a", href=link)
    return soup.prettify()


async def remove_dead_links(links: list[str], html: str):
    # TODO buscar todos os links em `LINKS` uma só vez (no momento tá repetindo por url)
    dead_links = [
        link
        for link in links
        if link.startswith("http")
        and (not link.startswith(ROOT_URL) or link in SKIP_URLS)
    ]
    for link in [*dead_links]:
        print(warn(html[len(html) // 2 : len(html) // 2 + 10]), link)
        try:
            is_html, redirect, response = await get_head_info(link)
        except SSLCertVerificationError:
            pass
        except ConnectError:
            pass
        try:
            response.raise_for_status()
            dead_links.remove(link)
        except:
            pass
    return extract_links(dead_links, html)


def html_to_mdx(html: str, path: Path):
    soup = BeautifulSoup(html, features="html.parser")
    title = soup.find("title").get_text()
    content = soup.select_one("#content")
    if not content:
        path.unlink()
        return
    for header in content.select("header>div"):
        header.clear()
    markdown = "\n".join(
        [
            "---",
            "layout: '@/layouts/MdLayout.astro'",
            f"title: '{title}'",
            "---",
            "import { Image } from 'astro:assets';\n",
        ]
    )
    markdown += markdownify(str(content))
    mdx = path.parent / (path.stem + ".mdx")
    parent = MD_DIR / mdx.parent.relative_to(HTML_DIR)
    parent.mkdir(parents=True, exist_ok=True)
    mdx = parent / mdx.name
    mdx.write_text(markdown, "utf-8")
