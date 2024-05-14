from pathlib import Path
from markdownify import markdownify as md
from bs4 import BeautifulSoup
import shutil
import re
from re import Match
from urllib.parse import urljoin


MD_DIR = Path("md").absolute()
if MD_DIR.exists():
    shutil.rmtree(MD_DIR)


SITE_URL = "https://arapiraca.ufal.br/graduacao/"
PROJECT_DIR = Path.home() / "httrack-websites/ufal/"
SITE_NAME = "arapiraca.ufal.br/graduacao"
SITE_DIR = PROJECT_DIR / SITE_NAME
shutil.copytree(SITE_DIR, MD_DIR)


def pages_to_md():
    for page in MD_DIR.rglob("*"):
        if page.is_dir():
            continue
        if page.suffix != ".html":
            page.unlink()
            continue
        html = page.read_text("utf-8")
        soup = BeautifulSoup(html, features="html.parser")
        content = soup.select_one("#content")
        if not content:
            page.unlink()
            continue
        for header in content.select("header>div"):
            header.clear()
        markdown = "---\nlayout: '@/layouts/MdLayout.astro'\n---\n\nimport { Image } from 'astro:assets';\n\n"
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
    return f'<Image src="{url}" alt="{alt}" inferSize />\n'


def get_relative_link_parser(md: Path):
    return lambda x: parse_relative_link(x, md)


def update_relative_links():
    XP = r"!\[(?P<desc>.*?)\]\((?P<link>.+?)(?:[ ]\"(?P<alt>.+?)\")?\)"
    LINK = r"<(?P<link>.+?)>"  # Dá erro no formato MDX
    HTML = r"\[(?P<desc>.*?)\]\((?P<link>.+?)\.html(?:[ ]\"(?P<alt>.+?)\")?\)"
    for md in MD_DIR.rglob("*.mdx"):
        text = md.read_text("utf-8")
        if re.search(LINK, text):
            text = re.sub(LINK, lambda x: x.group("link"), text)
        if re.search(XP, text):
            parser = get_relative_link_parser(md)
            text = re.sub(XP, parser, text)
        if re.search(HTML, text):
            text = re.sub(
                HTML, lambda x: f'[{x.group("desc")}]({x.group("link")})', text
            )
        text = text.replace("](ciencia-da-computacao/", "](")
        md.write_text(text, "utf-8")


def flatten_dirs():
    index_md = MD_DIR / "ciencia-da-computacao.mdx"
    index_md.rename(MD_DIR / "index.mdx")
    cc_dir = MD_DIR / "ciencia-da-computacao"
    for path in cc_dir.iterdir():
        shutil.move(path, MD_DIR)
    cc_dir.rmdir()


pages_to_md()
update_relative_links()
clean_directories()
flatten_dirs()
