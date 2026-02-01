"""Convert ASCII/text DataFrame outputs in markdown cells to proper Markdown tables.
Heuristics:
- Find contiguous blocks of 2+ lines where each line contains multiple columns separated by 2+ spaces.
- Split columns by 2+ spaces and build a Markdown table.
- Handle code-block fenced sections as well.
- Preserve other markdown content.
- Report modified notebooks and cell indices (1-based).
"""
import nbformat
import glob
import os
import re

NOTEBOOK_DIR = "notebooks"

# pattern to detect lines that look like table rows separated by 2+ spaces
row_pattern = re.compile(r"^\s*\S+(?:\s{2,}\S+)+\s*$")

multi_space_split = re.compile(r"\s{2,}")


def convert_block(lines):
    # lines: list of text lines that are table-like
    rows = [multi_space_split.split(ln.strip()) for ln in lines]
    # ensure consistent column count
    col_counts = [len(r) for r in rows]
    max_cols = max(col_counts)
    # pad rows with empty strings if needed
    for r in rows:
        if len(r) < max_cols:
            r.extend([""] * (max_cols - len(r)))
    # build markdown table
    header = rows[0]
    body = rows[1:]
    md = []
    md.append("| " + " | ".join(h.strip() for h in header) + " |")
    md.append("| " + " | ".join(["---"] * max_cols) + " |")
    for r in body:
        md.append("| " + " | ".join(c.strip() for c in r) + " |")
    return "\n".join(md)


def process_markdown_source(src):
    # src is a single string (cell source)
    lines = src.splitlines()
    out_lines = []
    i = 0
    changed = False
    while i < len(lines):
        ln = lines[i]
        # detect fenced code block start
        if ln.strip().startswith("```"):
            # copy until closing fence
            out_lines.append(ln)
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                out_lines.append(lines[i])
                i += 1
            if i < len(lines):
                out_lines.append(lines[i])
                i += 1
            continue
        # try to detect a table-like block of 2+ lines
        if row_pattern.match(ln):
            j = i
            block = []
            while j < len(lines) and row_pattern.match(lines[j]):
                block.append(lines[j])
                j += 1
            if len(block) >= 2:
                md_table = convert_block(block)
                out_lines.append(md_table)
                changed = True
                i = j
                continue
            else:
                out_lines.append(ln)
                i += 1
                continue
        else:
            out_lines.append(ln)
            i += 1
    return ("\n".join(out_lines), changed)


def process_notebook(path):
    nb = nbformat.read(path, as_version=4)
    modified = False
    changed_cells = []
    for idx, cell in enumerate(nb.cells):
        if cell.get("cell_type") != "markdown":
            continue
        src = cell.get("source", "")
        if isinstance(src, list):
            src_str = "".join(src)
        else:
            src_str = src
        new_src, changed = process_markdown_source(src_str)
        if changed and new_src.strip() != src_str.strip():
            cell["source"] = new_src
            modified = True
            changed_cells.append(idx+1)
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
            print(f" - {p}: converted text tables at cell indices {cells}")
    else:
        print("No text tables converted.")

if __name__ == "__main__":
    main()
