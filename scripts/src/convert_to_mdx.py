import re, shutil
from re import Match
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from markdownify import markdownify
from utils.globals import HTML_DIR, MD_DIR, ROOT_URL, PAGES_DIR


def main():
    if MD_DIR.is_dir():
        shutil.rmtree(MD_DIR)
    pages_to_mdx()
    shutil.copytree(MD_DIR, PAGES_DIR, dirs_exist_ok=True)


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
