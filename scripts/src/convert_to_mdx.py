import shutil, asyncio
from bs4 import BeautifulSoup
from pathlib import Path
from markdownify import markdownify

from src.scrape import try_fetch_route
from utils.globals import HTML_DIR, MD_DIR, ROOT_URL, PAGES_DIR, LINKS_PATH, SKIP_URLS
from utils.fn import extract_links

LINKS: list[str] | None = None


def main():
    asyncio.run(check_dead_links())
    if MD_DIR.is_dir():
        shutil.rmtree(MD_DIR)
    pages_to_mdx()
    shutil.copytree(MD_DIR, PAGES_DIR, dirs_exist_ok=True)


async def check_dead_links():
    global LINKS
    LINKS = {l: (l in SKIP_URLS) for l in LINKS_PATH.read_text().splitlines()}
    links = [l for l in LINKS if l.startswith("http") and not l.startswith(ROOT_URL)]
    await asyncio.gather(*map(check_dead_link, links))


async def check_dead_link(link: str):
    result = await try_fetch_route(link)
    LINKS[link] = result is None


def pages_to_mdx():
    paths = [path for path in HTML_DIR.rglob("*.html")]
    docs = [p.read_text("utf-8") for p in paths]
    docs = [filter_links(html) for html in docs]
    for path, html in zip(paths, docs):
        html_to_mdx(html, path)


def filter_links(html: str):
    links = [*LINKS.keys()]
    links = list(filter(lambda l: l and l in html, links))
    html = remove_relative_links(links, html)
    html = remove_plone_links(links, html)
    html = update_relative_anchors(links, html)
    html = remove_dead_links(html)
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


def remove_dead_links(html: str):
    links = [link for link, dead in LINKS.items() if dead]
    return extract_links(links, html) if links else html


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
