from bs4 import BeautifulSoup


def err(msg):
    return f"\033[31m{msg}\033[0m"


def ok(msg):
    return f"\033[32m{msg}\033[0m"


def warn(msg):
    return f"\033[33m{msg}\033[0m"


def extract_links(links: list[str], html: str):
    if not links:
        return
    soup = BeautifulSoup(html, "html.parser")
    for link in links:
        for img in soup.find_all("img", src=link):
            img.extract()
        for anchor in soup.find_all("a", href=link):
            anchor.extract()
    return soup.prettify()
