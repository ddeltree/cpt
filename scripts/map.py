from typing import Tuple
from pathlib import Path
import yaml


paths = map(
    lambda p: p[3:-4] if p.endswith(".mdx") else p[3:],
    sorted(
        filter(
            lambda x: "index.mdx" not in x and x != "md",
            (str(x) for x in Path("md").rglob("*")),
        )
    ),
)


yml: dict[str, dict] = dict()
for path in paths:
    ref = yml
    keys = path.split("/")
    for key in keys:
        value = ref.get(key, dict())
        ref[key] = value
        ref = ref[key]


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
        if child != None and should_stack(child):
            stack.append(to_iter(child))
        elif not child:
            on_pop(stack)
            stack.pop()


def make_iterator(entry: Tuple[str | None, dict, dict | None] | dict):
    path, parent, _ = entry if not isinstance(entry, dict) else (None, entry, None)
    for key, value in parent.items():
        new_path = f"{path}/{key}" if path else key
        yield (new_path, value, parent)


def should_stack(child: Tuple[str, dict, dict]):
    path, value, parent = child
    if len(value.keys()) == 0:
        parent[path.split("/")[-1]] = path
    return True


iter_tree(
    root=yml,
    to_iter=make_iterator,
    should_stack=should_stack,
    on_pop=lambda x: ...,
)

Path("sitemap.yaml").write_text(yaml.dump(yml))
