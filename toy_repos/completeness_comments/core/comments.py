# Remove `#` line comments. (Block comments not yet supported.)
def strip_comments(src):
    out = []
    for line in src.splitlines():
        idx = line.find("#")
        out.append(line if idx == -1 else line[:idx])
    return "\n".join(out)
