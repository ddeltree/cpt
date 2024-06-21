from pathlib import Path
import yaml


class TPath(type(Path())):
    def __init__(self, path: Path):
        self.state = path.iterdir() if path.is_dir() else None

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.state) if self.state else None


def iter_directories():
    iter_tree(
        MD,
        to_iter=lambda x: TPath(x),
        should_stack=lambda x: x.is_dir(),
        on_pop=lambda x: add_entry([y for y in x]),
    )


def iter_files():
    iter_tree(MD, to_iter=lambda x: TPath(x), should_stack=should_stack)


def should_stack(file: Path):
    if file.is_file():
        file = file.parent if file.stem == "index" else file.parent / file.stem
        file = file.relative_to(MD)
        add_file_entry(file)
    if not file.is_dir():
        return False
    length = len([*file.iterdir()])
    if length == 0:
        add_entry(([x for x in file.parents])[::-1][1:] + [file], str(file))
    return True


def add_file_entry(file: Path):
    # TODO refatorar add_entry() para ser uma função universal
    if str(file) == ".":
        return
    ref = YAML
    keys = str(file).split("/")
    for i, key in enumerate(keys):
        ref[key] = ref.get(key, dict() if i != len(keys) - 1 else str(file))
        ref = ref[key]


def iter_tree(
    root,
    to_iter=lambda x: iter(x),
    should_stack=lambda x: False,
    on_pop=lambda x: ...,
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


def add_entry(dir_stack, value=None):
    ref = YAML
    for i in range(len(dir_stack) - 1):
        key = str(dir_stack[i].relative_to(MD).name)
        if not key:
            continue
        ref[key] = ref.get(key, dict())
        ref = ref[key]
    key = str(dir_stack[-1].relative_to(MD).name)
    ref[key] = ref.get(key, dict()) if not value else value


YAML = dict()
MD = Path("md")

iter_directories()
iter_files()

Path("sitemap.yaml").write_text(yaml.dump(YAML), "utf-8")
