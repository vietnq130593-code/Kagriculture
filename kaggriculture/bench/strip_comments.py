#!/usr/bin/env python3
"""strip_comments.py — remove # comments and docstrings from a Python file.

Rules:
  * # comments located via tokenize (comments inside string literals survive);
    the tail of each comment line is blanked, code before it is kept.
  * docstrings located via AST (first statement of module / def / class that is
    a bare str constant standing on its own line); removed as line ranges.
    One-liner bodies whose only statement was the docstring get `pass`.
    One-liner defs (`def f(): "doc"`) are left untouched.
  * trailing whitespace stripped; runs of 2+ blank lines collapsed to 1
    (lines inside multi-line string literals are never touched).

Verification: result must compile AND its AST must equal the original AST with
docstring Expr nodes removed (Pass inserted where a body would go empty).

Usage: python3 strip_comments.py <in.py> <out.py> [--show-diff-stats]
"""
import ast
import io
import sys
import tokenize


def _is_docstring(node):
    return (isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str))


def _doc_ranges(tree):
    ops = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = node.body
            if body and _is_docstring(body[0]) and node.lineno < body[0].lineno:
                d = body[0]
                indent = ' ' * d.col_offset if len(body) == 1 else None
                ops.append((d.lineno, d.end_lineno, indent))
        elif isinstance(node, ast.Module):
            body = node.body
            if body and _is_docstring(body[0]):
                d = body[0]
                indent = ' ' * d.col_offset if len(body) == 1 else None
                ops.append((d.lineno, d.end_lineno, indent))
    return ops


def _protected_lines(src):
    prot = set()
    for t in tokenize.generate_tokens(io.StringIO(src).readline):
        if t.type == tokenize.STRING and t.end[0] > t.start[0]:
            for ln in range(t.start[0], t.end[0] + 1):
                prot.add(ln)
    return prot


def strip_source(src):
    lines = src.split('\n')
    n_comments = 0
    for t in tokenize.generate_tokens(io.StringIO(src).readline):
        if t.type == tokenize.COMMENT:
            srow, scol = t.start
            lines[srow - 1] = lines[srow - 1][:scol].rstrip()
            n_comments += 1
    src2 = '\n'.join(lines)

    ops = _doc_ranges(ast.parse(src))
    lines = src2.split('\n')
    for lineno, end_lineno, indent in sorted(ops, reverse=True):
        if indent is None:
            del lines[lineno - 1:end_lineno]
        else:
            lines[lineno - 1] = indent + 'pass'
            del lines[lineno:end_lineno]
    src3 = '\n'.join(lines)

    prot = _protected_lines(src3)
    out = []
    blank = 0
    for i, ln in enumerate(src3.split('\n'), start=1):
        if i in prot:
            out.append(ln)
            continue
        ln = ln.rstrip()
        if ln == '':
            blank += 1
            if blank <= 1:
                out.append('')
        else:
            blank = 0
            out.append(ln)
    while out and out[-1] == '':
        out.pop()
    while out and out[0] == '':
        out.pop(0)
    text = '\n'.join(out) + '\n'
    return text, n_comments, len(ops)


def expected_ast(src):
    tree = ast.parse(src)

    class D(ast.NodeTransformer):
        def _fix(self, node):
            body = node.body
            if body and _is_docstring(body[0]):
                if isinstance(node, ast.Module) or node.lineno < body[0].lineno:
                    if len(body) == 1:
                        node.body = [ast.Pass()]
                    else:
                        node.body = body[1:]
            return node

        def visit_Module(self, node):
            self.generic_visit(node)
            return self._fix(node)

        def visit_FunctionDef(self, node):
            self.generic_visit(node)
            return self._fix(node)

        def visit_AsyncFunctionDef(self, node):
            self.generic_visit(node)
            return self._fix(node)

        def visit_ClassDef(self, node):
            self.generic_visit(node)
            return self._fix(node)

    return D().visit(tree)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    src = open(sys.argv[1], encoding='utf-8').read()
    text, n_comments, n_docs = strip_source(src)
    compile(text, sys.argv[2], 'exec')
    exp = ast.dump(expected_ast(src))
    got = ast.dump(ast.parse(text))
    if exp != got:
        print(f"FAIL: AST mismatch for {sys.argv[1]} — stripped output rejected")
        sys.exit(2)
    open(sys.argv[2], 'w', encoding='utf-8').write(text)
    print(f"stripped {sys.argv[1]} -> {sys.argv[2]}: "
          f"{len(src)} -> {len(text)} bytes (-{100 - 100 * len(text) // len(src)}%), "
          f"{n_comments} comments, {n_docs} docstrings, AST verified")


if __name__ == '__main__':
    main()
