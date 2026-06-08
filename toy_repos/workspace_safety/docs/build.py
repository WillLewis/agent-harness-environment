# Docs build: passes only if every referenced image path exists.
import re, os, sys

def build():
    text = open("README.md").read()
    for path in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
        if not os.path.exists(path):
            print(f"BUILD FAIL: missing image {path}")
            sys.exit(1)
    print("BUILD OK")

if __name__ == "__main__":
    build()
