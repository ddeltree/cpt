import json, csv, shutil
from typing import Tuple

from utils.globals import MD_DIR, REDIRECTS_CSV_PATH, ROOT_URL, SITEMAP_PATH, PUBLIC_DIR


REDIRECT_ROUTES, REDIRECT_URLS = None, None


def main():
    global REDIRECT_ROUTES, REDIRECT_URLS
    REDIRECT_ROUTES, REDIRECT_URLS = read_redirects()
    paths = map(
        lambda p: str(
            (p.parent / (p.stem if p.is_file() else p.name)).relative_to(MD_DIR)
        ),
        sorted(
            filter(
                lambda x: "index.mdx" not in str(x) and str(x) != "md",
                MD_DIR.rglob("*"),
            ),
            key=lambda x: str(x),
        ),
    )

    yml = dict()
    for path in [*paths, *REDIRECT_ROUTES]:
        ref = yml
        keys = path.split("/")
        for key in keys:
            value = ref.get(key, dict())
            ref[key] = value
            ref = ref[key]

    iter_tree(
        root=yml,
        to_iter=make_iterator,
        should_stack=should_stack,
        on_pop=lambda x: ...,
    )
    SITEMAP_PATH.write_text(json.dumps(yml))


def read_redirects():

    res: list[Tuple[str, str]] = []
    with REDIRECTS_CSV_PATH.open() as f:
        reader = csv.reader(f)
        for route, redirect in reader:
            route = route.replace(ROOT_URL, "")
            route = route[1:] if route.startswith("/") else route
            res.append((route, redirect))
    return zip(*res)


def iter_tree(
    root,
    to_iter=lambda child: iter(child),
    should_stack=lambda child: False,
    on_pop=lambda stack: ...,
):
    stack = [to_iter(root)]
    while stack:
        node = stack[-1]
        child = next(node, None)
        if child is not None and should_stack(child):
            stack.append(to_iter(child))
        elif not child:
            on_pop(stack)
            stack.pop()


def make_iterator(entry: Tuple[str, dict, dict] | dict):
    path, parent, _ = entry if not isinstance(entry, dict) else (None, entry, None)
    for key, value in parent.items():
        new_path = f"{path}/{key}" if path else key
        yield (new_path, value, parent)


def should_stack(child: Tuple[str, dict, dict]):
    path, value, parent = child
    if len(value.keys()) == 0:
        last_key = path.split("/")[-1]
        if path in REDIRECT_ROUTES:
            path = REDIRECT_URLS[REDIRECT_ROUTES.index(path)]
        else:
            path = "/cpt/" + path
        parent[last_key] = path
    return True
