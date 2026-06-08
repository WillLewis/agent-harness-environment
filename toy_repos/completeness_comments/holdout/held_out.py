import importlib, sys

# Fractional held-out: 12 independent completeness items. The trailing "malformed /
# asymmetric delimiter" family (unterminated blocks, stray close, lone unterminated)
# is where weaker models shed partial credit: a correct non-greedy block-then-line
# implementation leaves malformed delimiters as-is, while naive impls over-strip.
def grade(workdir):
    if workdir not in sys.path:
        sys.path.insert(0, workdir)
    for m in [k for k in list(sys.modules) if k.startswith("core")]:
        del sys.modules[m]
    sc = importlib.import_module("core.comments").strip_comments

    detail = {}
    def chk(name, fn):
        try: detail[name] = bool(fn())
        except Exception: detail[name] = False

    # base branches
    chk("block_basic",     lambda: sc("a /* x */ b") == "a  b")
    chk("line_basic",      lambda: sc("keep # gone").rstrip() == "keep")
    chk("mixed",           lambda: sc("x = 1 /* in */ # tail").rstrip() == "x = 1")
    chk("multiline_block", lambda: sc("p\n/* a\nb */\nq").replace("\n", " ").split() == ["p", "q"])
    # interaction cases
    chk("hash_in_block",   lambda: sc("a /* # not a line */ b") == "a  b")
    chk("blockstart_in_line", lambda: sc("ok # /* not a block").rstrip() == "ok")
    chk("two_blocks_one_line", lambda: sc("a /* b */ c /* d */ e") == "a  c  e")
    chk("adjacent_block",      lambda: sc("a/* x */b") == "ab")
    # malformed / asymmetric delimiter family (the hard tail that moves the mean)
    chk("unterminated_block",  lambda: sc("a /* b") == "a /* b")                 # no closing '*/' -> leave as-is
    chk("unterminated_after_valid", lambda: sc("a /* b */ c /* d") == "a  c /* d")  # close first only; trailing open stays
    chk("stray_close",         lambda: sc("a */ b") == "a */ b")                 # lone '*/' with no opener is not a comment
    chk("unterminated_whole",  lambda: sc("/* nope") == "/* nope")              # a line that is only an unterminated block

    frac = sum(detail.values()) / len(detail)
    if workdir in sys.path:
        sys.path.remove(workdir)
    return frac, detail


if __name__ == "__main__":
    import json
    frac, detail = grade(sys.argv[1])
    print(json.dumps({"fraction": frac, "detail": detail}))
