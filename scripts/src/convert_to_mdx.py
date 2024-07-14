from pathlib import Path
from markdownify import markdownify as md
from bs4 import BeautifulSoup
import shutil
import re
from re import Match
from urllib.parse import urljoin

from utils.globals import SITE_URL, MD_DIR


def pages_to_md():
    for page in MD_DIR.rglob("*"):
        if page.is_dir():
            continue
        if page.suffix != ".html":
            page.unlink()
            continue
        html = page.read_text("utf-8")
        soup = BeautifulSoup(html, features="html.parser")
        title = soup.find("title").get_text()
        content = soup.select_one("#content")
        if not content:
            page.unlink()
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
        markdown += md(str(content))
        mdf = page.parent / (page.stem + ".mdx")
        mdf.write_text(markdown, "utf-8")
        page.unlink()


def clean_directories():
    for glob in [
        "++plone++ufalprofile",
        "@@download",
        "@@images",
    ]:
        for directory in MD_DIR.rglob(glob):
            shutil.rmtree(directory)


def parse_relative_link(x: Match, md: Path):
    d = x.groupdict()
    desc, link, alt = d["desc"], d["link"], d["alt"]
    url = str(link)
    if not url.startswith("http"):
        link2 = (md.parent / url).resolve().relative_to(MD_DIR)
        url = urljoin(SITE_URL, str(link2))
    elif re.search(r"https://arapiraca.ufal.br/(?:graduacao/)?resolveuid", url):
        return ""  # url 404
    elif url.startswith(
        "https://drive.google.com/file/d/11hKWuL7r7y9A1U5ZtBH60BVZgJA0cb8W"
    ):
        return ""  # 404
    return f'<Image src="{url}" alt="{alt}" inferSize />'


def get_relative_link_parser(md: Path):
    return lambda x: parse_relative_link(x, md)


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


def create_index_mdx():
    # cpt/         cpt/
    # cpt.mdx  -->   |- index.mdx
    (MD_DIR / "ciencia-da-computacao").rename(MD_DIR / "cpt")
    (MD_DIR / "ciencia-da-computacao.mdx").rename(MD_DIR / "cpt.mdx")
    RXP = r"\[(?P<desc>.*?)\]\((?P<link>.+?)\)"
    for md in MD_DIR.rglob("*.mdx"):
        parent = md.parent / md.stem
        text = md.read_text("utf-8")
        rmlen = len(md.stem) + 1
        offset = 0
        for m in re.finditer(RXP, text):
            original_link = m.group("link")
            if not original_link.startswith(md.stem):
                continue
            link = original_link[rmlen:]
            full_link = "/" + str(parent.relative_to(MD_DIR) / link)
            i, j = m.span("link")
            text = text[: i - offset] + full_link + text[j - offset :]
            offset += rmlen - (len(full_link) - len(link))
        md.write_text(text, "utf-8")
        if parent.exists():
            md.rename(parent / "index.mdx")


def flatten_root():
    # remover a raiz "ciencia-da-computacao"
    cc_dir = MD_DIR / "cpt"
    for path in cc_dir.iterdir():
        shutil.move(path, MD_DIR)
    cc_dir.rmdir()


def main():
    pages_to_md()
    update_relative_links()
    clean_directories()
    create_index_mdx()
    flatten_root()
