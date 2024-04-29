from pathlib import Path


def to_str(
    directory: Path,
    subdir: Path,
    padding: int,
):
    return "\t" * padding + str(subdir.relative_to(directory)) + "\n"


text = ""
directories = [(Path("md"), Path("md").iterdir())]

while directories:
    ((directory, iterator)) = directories[-1]
    subdir = next((iterator), None)
    while subdir:
        if subdir.is_dir():
            text += to_str(directory, subdir, len(directories) - 1)
            directories.append((subdir, subdir.iterdir()))
            break
        subdir = next((iterator), None)
    else:
        directories.pop()

Path("map.txt").write_text(text, "utf-8")
