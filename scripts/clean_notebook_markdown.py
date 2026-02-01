"""Remove emoji characters from markdown cells in notebooks.
- Scans `notebooks/*.ipynb`.
- Removes Unicode emoji characters and common emoji glyphs like ✅, ✔️.
- Preserves markdown structure and cell metadata.
- Writes notebooks back if modified and reports changes.
"""
import nbformat
import glob
import re
import os

NOTEBOOK_DIR = "notebooks"

emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002700-\U000027BF"  # dingbats
    "\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE,
)

# Also remove common heavy-check glyphs and other isolated symbols not covered
extra_symbols = re.compile(r"[✅✔️🎉🔥🔴🟢🔔👉🙂😊👍✳️✨⚠️]")


def clean_text(text: str) -> str:
    if not text:
        return text
    new = emoji_pattern.sub("", text)
    new = extra_symbols.sub("", new)
    # Normalize multiple blank lines
    new = re.sub(r"\n{3,}", "\n\n", new)
    # Trim trailing spaces on lines
    new = "\n".join([ln.rstrip() for ln in new.splitlines()])
    return new


def process_notebook(path: str):
    nb = nbformat.read(path, as_version=4)
    modified = False
    changed_cells = []
    for i, cell in enumerate(nb.cells):
        if cell.get("cell_type") != "markdown":
            continue
        src = cell.get("source", "")
        # nbformat may store source as list or string; convert to string
        if isinstance(src, list):
            src_str = "".join(src)
        else:
            src_str = src
        cleaned = clean_text(src_str)
        if cleaned != src_str:
            cell["source"] = cleaned
            modified = True
            changed_cells.append(i+1)  # use 1-based cell numbers for reporting
    if modified:
        nbformat.write(nb, path)
    return modified, changed_cells


def main():
    nb_paths = glob.glob(os.path.join(NOTEBOOK_DIR, "*.ipynb"))
    modified_files = []
    for p in nb_paths:
        mod, cells = process_notebook(p)
        if mod:
            modified_files.append((p, cells))
    if modified_files:
        print("Modified notebooks:")
        for p, cells in modified_files:
            print(f" - {p}: cleaned markdown cells at indices {cells}")
    else:
        print("No markdown emoji found in notebooks.")

if __name__ == "__main__":
    main()
