import ast
import io
import tokenize

SRC = "/home/z/my-project/kaggressure/v6.py"
SRC = "/home/z/my-project/kaggriculture/v6.py"
DST = "/home/z/my-project/kaggriculture/cell4_v6.py"
DROP_FUNCS = {"_arena_diag", "_gt_s"}

src = open(SRC).read()
lines = src.splitlines(keepends=True)
tree = ast.parse(src)

delete = set()


def _delete_range(node):
    start = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
    end = node.end_lineno
    for ln in range(start, end + 1):
        delete.add(ln)
    nxt = end + 1
    if nxt <= len(lines) and lines[nxt - 1].strip() == "":
        pass
    return start, end


for node in list(tree.body):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name in DROP_FUNCS:
        _delete_range(node)

docstrings = []


def collect_doc(body, owner):
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
            and isinstance(body[0].value.value, str):
        docstrings.append((body[0], owner))


collect_doc(tree.body, "<module>")
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        collect_doc(node.body, node.name)
        if len(node.body) == 1 and docstrings and docstrings[-1][0] is node.body[0]:
            raise SystemExit(f"docstring-only body: {node.name}")

for ds, owner in docstrings:
    if ds.lineno in delete or (ds.lineno - 1) in delete:
        continue
    for ln in range(ds.lineno, ds.end_lineno + 1):
        text = lines[ln - 1]
        stripped = text.strip()
        if ln == ds.lineno and not stripped.startswith('"""'):
            raise SystemExit(f"docstring not whole-line at {ln}: {text!r}")
        delete.add(ln)

comments = []
for tok in tokenize.generate_tokens(io.StringIO(src).readline):
    if tok.type == tokenize.COMMENT:
        comments.append((tok.start[0], tok.start[1], tok.end[1]))

for ln, c0, c1 in comments:
    if ln in delete:
        continue
    text = lines[ln - 1]
    before = text[:c0]
    if before.strip() == "":
        delete.add(ln)
    else:
        lines[ln - 1] = before.rstrip() + "\n"

out = []
for i, text in enumerate(lines, start=1):
    if i in delete:
        continue
    if text.strip() == "":
        if out and out[-1].strip() == "" and len(out) >= 1:
            if len(out) >= 2 and out[-2].strip() == "":
                continue
            out.append("\n")
        else:
            out.append("\n")
    else:
        out.append(text if text.endswith("\n") else text + "\n")

code = "".join(out)
if not code.endswith("\n"):
    code += "\n"
open(DST, "w").write(code)
print(f"wrote {DST}: {len(lines)} -> {len(out)} lines ({len(delete)} deleted, {len(comments)} comments, {len(docstrings)} docstrings)")
