from pathlib import Path
import yaml


class Subdirectories(type(Path())):
    def __init__(self, parent: Path):
        self.ref = parent
        self.state = parent.iterdir()

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.state)


def iter_directories():
    iter_tree(
        MD,
        to_iter=lambda x: Subdirectories(x),
        should_stack=lambda x: x.is_dir(),
        on_pop=lambda x: add_entry([y.ref for y in x]),
    )


def iter_tree(
    root, to_iter=lambda x: iter(x), should_stack=lambda: False, on_pop=lambda: ...
):
    stack = [to_iter(root)]
    while stack:
        node = stack[-1]
        child = next(node, None)
        if child and should_stack(child):
            stack.append(to_iter(child))
        elif not child:
            on_pop(stack)
            stack.pop()


def add_entry(dir_stack):
    ref = YAML
    for directory in dir_stack:
        key = str(directory.relative_to(MD).name)
        if not key:
            continue
        ref[key] = ref.get(key, dict())
        ref = ref[key]


YAML = dict()
MD = Path("md")

iter_directories()


Path("sitemap.yaml").write_text(yaml.dump(YAML), "utf-8")
