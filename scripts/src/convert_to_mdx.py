import shutil, asyncio, json
from urllib.parse import quote
from bs4 import BeautifulSoup, Comment
from pathlib import Path

from src.scrape import try_fetch_route
from src.create_sitemap import read_redirects
from utils.globals import (
    HTML_DIR,
    MD_DIR,
    ROOT_URL,
    PAGES_DIR,
    LINKS_PATH,
    SKIP_URLS,
    FRONTMATTER_PATH,
    RESOURCES_PATH,
    LINK_TAGS_PATH,
)
from utils.fn import extract_links

LINKS: list[str] | None = None
REDIRECT_ROUTES: list[str] | None = None
REDIRECT_URLS: list[str] | None = None
RESORCES_ROUTES = None


def main():
    global REDIRECT_ROUTES, REDIRECT_URLS, RESOURCE_ROUTES
    REDIRECT_ROUTES, REDIRECT_URLS = read_redirects()
    RESOURCE_ROUTES = RESOURCES_PATH.read_text("utf-8").splitlines()

    asyncio.run(check_dead_links())
    if MD_DIR.is_dir():
        shutil.rmtree(MD_DIR)
    convert_pages_to_mdx()
    collect_scripts_and_css()
    if PAGES_DIR.exists():
        shutil.rmtree(PAGES_DIR)
    shutil.copytree(MD_DIR, PAGES_DIR, dirs_exist_ok=True)


async def check_dead_links():
    global LINKS
    LINKS = {l: (l in SKIP_URLS) for l in LINKS_PATH.read_text().splitlines()}
    links = [l for l in LINKS if l.startswith("http") and not l.startswith(ROOT_URL)]
    # TODO uncomment
    # await asyncio.gather(*map(check_dead_link, links))


async def check_dead_link(link: str):
    result = await try_fetch_route(link)
    LINKS[link] = result is None


def convert_pages_to_mdx():
    paths = [path for path in HTML_DIR.rglob("index.html")]
    docs = [p.read_text("utf-8") for p in paths]
    docs = [filter_links(html) for html in docs]
    for path, html in zip(paths, docs):
        save_html_as_mdx(html, path)


def filter_links(html: str):
    links = [*LINKS.keys()]
    links = list(filter(lambda l: l and l in html, links))
    html = remove_relative_links(links, html)
    html = remove_plone_links(links, html)
    html = update_relative_anchors(links, html)
    # html = remove_dead_links(html)
    html = quote_links(links, html)
    return html


def remove_relative_links(links: list[str], html: str):
    links = [x for x in links if x.startswith(".")]
    return extract_links(links, html) if links else html


def remove_plone_links(links: list[str], html: str):
    links = [x for x in links if x.startswith("/") or x.startswith("+")]
    return extract_links(links, html) if links else html


def update_relative_anchors(links: list[str], html: str):
    links = [x for x in links if x.startswith(ROOT_URL) and x not in RESOURCE_ROUTES]
    if not links:
        return html
    soup = BeautifulSoup(html, "html.parser")
    for link in links:
        for anchor in soup.find_all("a", href=link):
            route = link.replace(ROOT_URL + "/", "")
            anchor["href"] = (
                link.replace(ROOT_URL, "/cpt")
                if route not in REDIRECT_ROUTES
                else REDIRECT_URLS[REDIRECT_ROUTES.index(route)]
            )
    return soup.prettify()


def remove_dead_links(html: str):
    links = [link for link, dead in LINKS.items() if dead]
    return extract_links(links, html) if links else html


def quote_links(links: list[str], html: str):
    links = [x for x in links if x.startswith("http") or x.startswith("/")]
    if not links:
        return html
    soup = BeautifulSoup(html, "html.parser")
    for link in links:
        for anchor in soup.find_all("a", href=link):
            anchor["href"] = quote(link, safe=":/?#&=")
    return soup.prettify()


def save_html_as_mdx(html: str, path: Path):
    soup = BeautifulSoup(html, features="html.parser")
    remove_invalid_mdx(soup)
    title = soup.find("title").get_text().strip()
    html_content = soup.select_one("#content")
    if not html_content:
        path.unlink()
        return
    for h in html_content.select("header > div"):
        h.extract()
    mdx = FRONTMATTER_PATH.read_text().replace("${title}", title)
    mdx += str(html_content)
    mdx_file = path.parent / (path.stem + ".mdx")
    parent = MD_DIR / mdx_file.parent.relative_to(HTML_DIR)
    parent.mkdir(parents=True, exist_ok=True)
    mdx_file = parent / mdx_file.name
    mdx_file.write_text(mdx)


def remove_invalid_mdx(soup: BeautifulSoup):
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()


def collect_scripts_and_css():
    paths = [path for path in HTML_DIR.rglob("index.html")]
    docs = [p.read_text("utf-8") for p in paths]
    docs = [filter_links(html) for html in docs]
    result = dict()
    for path, html in zip(paths, docs):
        soup = BeautifulSoup(html, features="html.parser")
        css_links = [
            link.get("href") for link in soup.find_all("link", rel="stylesheet")
        ]
        script_links = [
            script.get("src") for script in soup.find_all("script") if script.get("src")
        ]
        key = str(path.parent.relative_to(HTML_DIR))
        result[key] = {"js": script_links, "css": css_links}
    LINK_TAGS_PATH.write_text(json.dumps(result, indent=2), "utf-8")
