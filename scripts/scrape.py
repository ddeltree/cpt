import httpx
from bs4 import BeautifulSoup
from pathlib import Path
import re

ROOT_URL = "https://arapiraca.ufal.br/graduacao/ciencia-da-computacao"
HTML_DIR = Path("html").absolute()


def get_filename_from_url(url: str):
    name = url.replace(ROOT_URL, "")
    name = name[1:] if name.startswith("/") else name
    return HTML_DIR / name / "index.html"


def touch_deep(path: Path):
    directory = path.parent if path.suffix == ".html" else path
    directory.mkdir(parents=True, exist_ok=True)
    path.touch()


def write_html(url, html):
    file = get_filename_from_url(url)
    touch_deep(file)
    file.write_text(html, "utf-8")


next_urls = {ROOT_URL}
done_urls = set()

while next_urls:
    url = next_urls.pop()
    done_urls.add(url)
    print(url)

    req = httpx.get(
        url,
    )
    html = req.text
    if not get_filename_from_url(url).exists():
        write_html(url, html)
    soup = BeautifulSoup(
        html,
        "html.parser",
    )
    for link in soup.find_all("a"):
        attrs = link.get_attribute_list("href")
        href: str = (attrs[:1] or [""])[0] or ""
        if not href.startswith("/") and not href.startswith("http"):
            continue
        href = href if href.startswith("http") else ROOT_URL + href
        if href not in done_urls and href.startswith(ROOT_URL):
            next_urls.add(href)
