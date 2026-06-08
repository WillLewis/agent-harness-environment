import re, os

def test_image_path_exists():
    text = open("README.md").read()
    for path in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
        assert os.path.exists(path), f"missing image {path}"
