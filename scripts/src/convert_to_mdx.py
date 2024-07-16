import re
from re import Match
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from markdownify import markdownify
from utils.globals import HTML_DIR, MD_DIR, SITE_URL


def main():
    pages_to_mdx()
    update_relative_links()


def pages_to_mdx():
    for path in HTML_DIR.rglob("*.html"):
        html = path.read_text("utf-8")
        soup = BeautifulSoup(html, features="html.parser")
        title = soup.find("title").get_text()
        content = soup.select_one("#content")
        if not content:
            path.unlink()
            continue
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


def update_relative_links():
    IMG = r"!\[(?P<desc>.*?)\]\((?P<link>.+?)(?:[ ]\"(?P<alt>.+?)\")?\)"
    LINK = r"<(?P<link>.+?)>"  # Dá erro no formato MDX
    HTML_LINK = r"\[(?P<desc>.*?)\]\((?P<link>.+?)\.html(?:[ ]\"(?P<alt>.+?)\")?\)"
    for md in MD_DIR.rglob("*.mdx"):
        text = md.read_text("utf-8")
        if re.search(LINK, text):
            text = re.sub(LINK, lambda x: x.group("link"), text)
        if re.search(IMG, text):
            parser = get_relative_link_parser(md)
            text = re.sub(IMG, parser, text)
        if re.search(HTML_LINK, text):
            text = re.sub(
                HTML_LINK, lambda x: f'[{x.group("desc")}]({x.group("link")})', text
            )
        text = text.replace("](ciencia-da-computacao/", "](/cpt/")
        md.write_text(text, "utf-8")


def get_relative_link_parser(md: Path):
    return lambda x: parse_relative_link(x, md)


def parse_relative_link(x: Match, md: Path):
    d = x.groupdict()
    desc, link, alt = d["desc"], d["link"], d["alt"]
    url = str(link)
    if not url.startswith("http") and "../../resolveuid" not in url:
        link2 = (md.parent / url).resolve().relative_to(MD_DIR.absolute())
        url = urljoin(SITE_URL, str(link2))
    elif re.search(r"https://arapiraca.ufal.br/(?:graduacao/)?resolveuid", url):
        return ""  # url 404
    return f'<Image src="{url}" alt="{alt}" inferSize />'
