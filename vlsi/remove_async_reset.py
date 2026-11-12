#!/usr/bin/env python3
"""
remove_async_reset.py

Convert asynchronous resets to synchronous resets in Verilog/SystemVerilog by
removing the reset edge (posedge/negedge) from flip-flop sensitivity lists.

    always_ff @(posedge clk_i or negedge rst_ni)   ->   always_ff @(posedge clk_i)

The reset branch inside the block (if (~rst_ni) ...) is left untouched, so the
reset becomes synchronous.

Register macros are handled too, e.g. (PULP common_cells style):

    `define FF(__q, __d, __reset_value, __clk = `REG_DFLT_CLK, __arst_n = `REG_DFLT_RST) \
      always_ff @(posedge (__clk) or negedge (__arst_n)) begin                          \
      ...

The reset edge is removed inside the `define body. Because a comment inside a
macro is not argument-substituted, the Design Compiler directive

    // synopsys sync_set_reset "rst_ni"

is placed in each module that *calls* a converted macro, using the actual reset
argument of the call (or the macro's default value, resolved through object-like
`defines such as `define REG_DFLT_RST rst_ni). Pass the header that defines the
macros together with the RTL files that use them, so call sites can be resolved.

Comments and strings are ignored when searching, so commented-out code is not
modified.
"""

import argparse
import bisect
import re
import sys
from pathlib import Path

DEFAULT_RESET_PATTERN = r"(?i).*(rst|reset).*"

_ALWAYS_RE = re.compile(r"\balways(?:_ff)?\s*@\s*\(")
_OR_RE = re.compile(r"(?<![\w$])or(?![\w$])")
_EVENT_RE = re.compile(
    r"^\s*(posedge|negedge)\s+\(?\s*([A-Za-z_][\w$.]*)\s*(\[[^\]]*\])?\s*\)?\s*$"
)
_MODULE_RE = re.compile(r"\b(?:macro)?module\b")
_ENDMODULE_RE = re.compile(r"\bendmodule\b")
_DEFINE_RE = re.compile(r"`define\s+([A-Za-z_]\w*)")
_CALL_RE = re.compile(r"`([A-Za-z_]\w*)\s*\(")
_INDENT_RE = re.compile(r"[ \t]*")
_IDENT_RE = re.compile(r"[A-Za-z_][\w$]*")
_DIRECTIVES = {"define", "undef", "ifdef", "ifndef", "elsif", "else", "endif",
               "include", "timescale", "default_nettype", "resetall"}


# --------------------------------------------------------------------------- #
# Low-level helpers
# --------------------------------------------------------------------------- #
_MASK_RE = re.compile(r'//[^\n]*|/\*.*?(?:\*/|\Z)|"(?:\\.|[^"\\\n])*"?', re.S)


def _mask_comments_and_strings(text):
    """Blank out comments and string contents, keeping length and newlines."""
    def blank(m):
        t = m.group(0)
        if t.startswith('"'):
            inner = re.sub(r"[^\n]", " ", t[1:-1]) if len(t) > 1 else ""
            return '"' + inner + t[-1] if len(t) > 1 else t
        return re.sub(r"[^\n]", " ", t)
    return _MASK_RE.sub(blank, text)


def _find_close_paren(masked, open_idx):
    depth = 0
    for k in range(open_idx, len(masked)):
        if masked[k] == "(":
            depth += 1
        elif masked[k] == ")":
            depth -= 1
            if depth == 0:
                return k
    return -1


def _split_top_level(masked, allow_or=False):
    """Split on top-level ',' (and 'or' if allow_or). Returns (spans, used_or)."""
    spans, start, depth, i, used_or = [], 0, 0, 0, False
    while i < len(masked):
        ch = masked[i]
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif depth == 0:
            if ch == ",":
                spans.append((start, i))
                start = i + 1
            elif allow_or:
                m = _OR_RE.match(masked, i)
                if m:
                    spans.append((start, i))
                    used_or = True
                    start = i = m.end()
                    continue
        i += 1
    spans.append((start, len(masked)))
    return spans, used_or


class _LineIndex:
    """Fast offset -> line number lookup."""
    def __init__(self, code):
        self.nl = [m.start() for m in re.finditer("\n", code)]

    def __call__(self, pos):
        return bisect.bisect_left(self.nl, pos) + 1


def _apply_edits(code, edits):
    """Apply non-overlapping (start, end, text) edits in one pass."""
    out, last = [], 0
    for start, end, text in sorted(edits, key=lambda e: (e[0], e[1])):
        out.append(code[last:start])
        out.append(text)
        last = end
    out.append(code[last:])
    return "".join(out)


def _line_start_and_indent(code, pos):
    ls = code.rfind("\n", 0, pos) + 1
    return ls, _INDENT_RE.match(code, ls).group(0)


def _make_is_reset(reset_names, reset_pattern):
    names = set(reset_names) if reset_names else None
    pattern = re.compile(reset_pattern)
    return (lambda s: s in names) if names is not None else (lambda s: bool(pattern.fullmatch(s)))


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #
def _parse_defines(code, masked):
    """Return list of dicts for every `define: name, span, formals, defaults, body."""
    defs = []
    for m in _DEFINE_RE.finditer(masked):
        cur = m.start()
        while True:
            nl = code.find("\n", cur)
            if nl == -1:
                end = len(code)
                break
            if code[cur:nl].rstrip().endswith("\\"):
                cur = nl + 1
                continue
            end = nl
            break

        formals, defaults, body_start = None, None, m.end()
        if m.end() < len(masked) and masked[m.end()] == "(":
            close = _find_close_paren(masked, m.end())
            if close != -1 and close < end:
                formals, defaults = [], []
                inner_m = masked[m.end() + 1:close]
                inner_c = code[m.end() + 1:close]
                for a, b in _split_top_level(inner_m)[0]:
                    part = inner_c[a:b].replace("\\\n", " ").strip()
                    if not part:
                        continue
                    name, _, dflt = part.partition("=")
                    formals.append(name.strip())
                    defaults.append(dflt.strip() or None)
                body_start = close + 1

        body = re.sub(r"\\\s*\n", " ", code[body_start:end]).strip()
        defs.append({"name": m.group(1), "start": m.start(), "end": end,
                     "formals": formals, "defaults": defaults, "body": body})
    return defs


def _find_reset_blocks(code, masked, is_reset):
    """Find every edge-triggered always block whose sensitivity list has a reset."""
    hits = []
    for m in _ALWAYS_RE.finditer(masked):
        open_idx = m.end() - 1
        close_idx = _find_close_paren(masked, open_idx)
        if close_idx < 0:
            continue
        inner_start = open_idx + 1
        inner_masked = masked[inner_start:close_idx]
        spans, used_or = _split_top_level(inner_masked, allow_or=True)

        kept, removed = [], []
        for a, b in spans:
            ev = _EVENT_RE.match(inner_masked[a:b])
            original = code[inner_start + a:inner_start + b].strip()
            if ev and is_reset(ev.group(2)):
                removed.append((original, ev.group(2)))
            else:
                kept.append(original)

        if not removed or not kept:
            continue
        hits.append({"pos": m.start(), "inner_start": inner_start, "close": close_idx,
                     "new_inner": (" or " if used_or else ", ").join(kept),
                     "removed": removed})
    return hits


def scan_macros(code, reset_names=None, reset_pattern=DEFAULT_RESET_PATTERN):
    """
    Collect macro information from a file (typically a header like registers.svh).

    Returns {"func": {name: info}, "obj": {name: value}} where info describes a
    function-like macro containing an async-reset flip-flop:
        {"formals": [...], "defaults": [...], "resets": [("formal", idx) | ("literal", name)]}
    """
    is_reset = _make_is_reset(reset_names, reset_pattern)
    masked = _mask_comments_and_strings(code)
    defs = _parse_defines(code, masked)
    hits = _find_reset_blocks(code, masked, is_reset)

    db = {"func": {}, "obj": {}}
    for d in defs:
        if d["formals"] is None:
            db["obj"][d["name"]] = d["body"]
            continue
        resets = []
        for h in hits:
            if d["start"] <= h["pos"] < d["end"]:
                for _, sig in h["removed"]:
                    ref = (("formal", d["formals"].index(sig)) if sig in d["formals"]
                           else ("literal", sig))
                    if ref not in resets:
                        resets.append(ref)
        if resets:
            db["func"][d["name"]] = {"formals": d["formals"], "defaults": d["defaults"],
                                     "resets": resets}
    return db


def _merge_db(*dbs):
    out = {"func": {}, "obj": {}}
    for db in dbs:
        if db:
            out["func"].update(db["func"])
            out["obj"].update(db["obj"])
    return out


def _resolve_signal(text, obj_defines):
    """Resolve an actual/default argument to a plain identifier, or None."""
    for _ in range(10):
        text = text.strip()
        while text.startswith("(") and text.endswith(")"):
            text = text[1:-1].strip()
        if text.startswith("`") and text[1:] in obj_defines:
            text = obj_defines[text[1:]]
            continue
        break
    return text if _IDENT_RE.fullmatch(text) else None


# --------------------------------------------------------------------------- #
# Main conversion
# --------------------------------------------------------------------------- #
def remove_async_reset(code, reset_names=None, reset_pattern=DEFAULT_RESET_PATTERN,
                       add_directive=True, macro_db=None):
    """
    Remove reset edges from flip-flop sensitivity lists, in plain always blocks
    and inside `define register macros.

    Args:
        code:          Verilog/SystemVerilog source text.
        reset_names:   Exact reset signal names. For macros, use the formal
                       argument names too (e.g. ["rst_ni", "__arst_n"]).
                       If given, reset_pattern is ignored.
        reset_pattern: Regex (full match) recognising reset names.
        add_directive: Insert '// synopsys sync_set_reset "..."' once per module.
        macro_db:      Output of scan_macros() for macros defined in OTHER files
                       (e.g. an included registers.svh). Macros in this file are
                       scanned automatically.

    Returns:
        (new_code, changes, warnings)
    """
    is_reset = _make_is_reset(reset_names, reset_pattern)
    masked = _mask_comments_and_strings(code)
    defs = _parse_defines(code, masked)
    db = _merge_db(macro_db, scan_macros(code, reset_names, reset_pattern))

    def in_define(pos):
        return next((d for d in defs if d["start"] <= pos < d["end"]), None)

    _line_of = _LineIndex(code)
    module_starts = [m.start() for m in _MODULE_RE.finditer(masked)]
    module_ends = [m.end() for m in _ENDMODULE_RE.finditer(masked)]

    def module_of(pos):
        k = bisect.bisect_right(module_starts, pos) - 1
        if k < 0:
            return None
        s = module_starts[k]
        j = bisect.bisect_right(module_ends, s)
        e = module_ends[j] if j < len(module_ends) else len(code)
        return (s, e) if pos < e else None

    edits, changes, warnings = [], [], []
    plan = {}  # module span -> {"pos", "indent", "sigs"}

    def want_directive(pos, sigs):
        mod = module_of(pos)
        if mod is None:
            return
        ls, indent = _line_start_and_indent(code, pos)
        p = plan.setdefault(mod, {"pos": ls, "indent": indent, "sigs": []})
        if ls < p["pos"]:
            p["pos"], p["indent"] = ls, indent
        for s in sigs:
            if s not in p["sigs"]:
                p["sigs"].append(s)

    # 1) always blocks (plain and inside macro bodies)
    for h in _find_reset_blocks(code, masked, is_reset):
        edits.append((h["inner_start"], h["close"], h["new_inner"]))
        d = in_define(h["pos"])
        changes.append({"line": _line_of(h["pos"]),
                        "kind": f"macro `{d['name']}" if d else "always",
                        "removed": [r[0] for r in h["removed"]],
                        "signals": [r[1] for r in h["removed"]],
                        "new_sensitivity": h["new_inner"]})
        if d is None and add_directive:
            want_directive(h["pos"], [sig for _, sig in h["removed"]])

    # 2) calls of converted register macros -> directive with the actual reset
    for m in _CALL_RE.finditer(masked):
        name = m.group(1)
        if name in _DIRECTIVES or name not in db["func"]:
            continue
        if in_define(m.start()):
            warnings.append(f"line {_line_of(m.start())}: `{name} used inside another "
                            f"macro; add the sync_set_reset directive by hand where that "
                            f"macro is called")
            continue
        info = db["func"][name]
        open_idx = m.end() - 1
        close = _find_close_paren(masked, open_idx)
        if close < 0:
            continue
        spans = _split_top_level(masked[open_idx + 1:close])[0]
        args = [code[open_idx + 1 + a:open_idx + 1 + b].strip() for a, b in spans]

        sigs = []
        for kind, val in info["resets"]:
            if kind == "literal":
                sigs.append(val)
                continue
            actual = args[val] if val < len(args) and args[val] else info["defaults"][val]
            sig = _resolve_signal(actual, db["obj"]) if actual else None
            if sig:
                sigs.append(sig)
            else:
                warnings.append(f"line {_line_of(m.start())}: could not resolve reset "
                                f"argument '{actual}' of `{name}'; add the directive by hand")
        if sigs:
            changes.append({"line": _line_of(m.start()), "kind": f"call `{name}",
                            "removed": [], "new_sensitivity": None, "reset": sigs})
            if add_directive:
                want_directive(m.start(), sigs)

    # 3) one directive per module, skipping signals that already have one
    for (ms, me), p in plan.items():
        existing = " ".join(re.findall(r"sync_set_reset\s*\"([^\"]*)\"", code[ms:me]))
        new_sigs = [s for s in p["sigs"]
                    if not re.search(rf"(?<![\w$]){re.escape(s)}(?![\w$])", existing)]
        if new_sigs:
            edits.append((p["pos"], p["pos"],
                          f'{p["indent"]}// synopsys sync_set_reset "{", ".join(new_sigs)}"\n'))

    return _apply_edits(code, edits), changes, warnings


# --------------------------------------------------------------------------- #
# Command line
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", type=Path,
                    help="Verilog/SystemVerilog files (include the macro header, e.g. registers.svh)")
    ap.add_argument("-r", "--reset", action="append", dest="resets",
                    help="Exact reset signal / macro formal name (repeatable). Overrides --pattern.")
    ap.add_argument("-p", "--pattern", default=DEFAULT_RESET_PATTERN,
                    help=f"Regex for reset names (default: {DEFAULT_RESET_PATTERN!r})")
    ap.add_argument("--no-directive", action="store_true",
                    help="Do not insert the sync_set_reset directive")
    out = ap.add_mutually_exclusive_group()
    out.add_argument("-i", "--in-place", action="store_true",
                     help="Overwrite files (a .bak copy is kept)")
    out.add_argument("-o", "--output", type=Path,
                     help="Output file (only with a single input file)")
    ap.add_argument("-n", "--dry-run", action="store_true",
                    help="Only report what would change")
    args = ap.parse_args()

    if args.output and len(args.files) > 1:
        ap.error("-o/--output works with a single input file; use -i for several")

    sources = {f: f.read_text() for f in args.files}

    # Pass 1: collect register macros from all files (headers included).
    db = _merge_db(*(scan_macros(s, args.resets, args.pattern) for s in sources.values()))
    if db["func"]:
        print("register macros with async reset: "
              + ", ".join(f"`{n}" for n in sorted(db["func"])), file=sys.stderr)

    # Pass 2: convert every file.
    for f, src in sources.items():
        new, changes, warnings = remove_async_reset(src, args.resets, args.pattern,
                                                    not args.no_directive, db)
        for c in changes:
            if c["kind"].startswith("call"):
                print(f"{f}:{c['line']}: {c['kind']} -> sync_set_reset "
                      f"{', '.join(c['reset'])}", file=sys.stderr)
            else:
                print(f"{f}:{c['line']}: [{c['kind']}] removed {', '.join(c['removed'])} "
                      f"-> @({c['new_sensitivity']})", file=sys.stderr)
        for w in warnings:
            print(f"{f}: WARNING {w}", file=sys.stderr)
        if not changes:
            print(f"{f}: no asynchronous reset found", file=sys.stderr)
        if args.dry_run:
            continue
        if args.in_place:
            if new != src:
                f.with_suffix(f.suffix + ".bak").write_text(src)
                f.write_text(new)
        elif args.output:
            args.output.write_text(new)
        else:
            sys.stdout.write(new)


if __name__ == "__main__":
    main()
