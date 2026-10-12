"""Stage only public project files for GitHub Pages, then check local HTML links.

Uses Python's standard library. The destination must be empty or not yet exist;
this command never deletes existing files or changes the source projects.
Example: python checks/preparar_pages.py --output /tmp/nucleo-pages
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
from urllib.parse import unquote, urlsplit


PUBLIC_DIRECTORIES = (
    "bancada_v3",
    "nucleo_integral_v2",
    "nucleo_toroidal",
    "references",
    "artifacts",
)
PUBLIC_ROOT_FILES = (
    "index.html",
    "README.md",
    "CONTRIBUTING.md",
    "auditoria_cientifica.md",
    "PROXIMOS_PASSOS.md",
)
SKIP_DIRECTORIES = {"__pycache__", "node_modules", "venv", "env"}
PUBLIC_EXTENSIONS = {
    ".html", ".css", ".js", ".json", ".csv", ".md", ".txt",
    ".pdf", ".docx", ".png", ".svg", ".obj", ".mtl", ".stl",
    ".scad", ".py", ".zip", ".vtu", ".npz",
}
PRIVATE_NAMES = {
    "credentials.json", "credential.json", "secrets.json", "secret.json",
    "id_rsa", "id_ed25519", "token.txt", "password.txt",
}


class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name not in {"href", "src"} or not value:
                continue
            parsed = urlsplit(value)
            if not parsed.scheme and not parsed.netloc and parsed.path:
                self.links.append(unquote(parsed.path))


def public_files(root: Path):
    for name in PUBLIC_ROOT_FILES:
        path = root / name
        if path.exists():
            if path.is_symlink() or not path.is_file():
                raise ValueError(f"Public root entry must be a regular file: {name}")
            yield path
        elif name == "index.html":
            raise ValueError("Missing root index.html; cannot publish an empty entry page")
    for name in PUBLIC_DIRECTORIES:
        directory = root / name
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError(f"Missing or linked public directory: {name}")
        for path in sorted(directory.rglob("*")):
            relative = path.relative_to(directory)
            if any(part.startswith(".") or part in SKIP_DIRECTORIES
                   for part in relative.parts):
                continue
            if path.is_symlink():
                raise ValueError(f"Symbolic links cannot be staged: {path.relative_to(root)}")
            if not path.is_file():
                continue
            if path.name.lower() in PRIVATE_NAMES:
                raise ValueError(f"Private filename in public project: {path.relative_to(root)}")
            if path.suffix.lower() not in PUBLIC_EXTENSIONS:
                raise ValueError(f"Unapproved public file type: {path.relative_to(root)}")
            yield path


def validate_links(destination: Path):
    checked = 0
    errors = []
    for html in sorted(destination.rglob("*.html")):
        parser = LocalLinks()
        parser.feed(html.read_text(encoding="utf-8-sig"))
        for link in parser.links:
            checked += 1
            if link.startswith("/"):
                errors.append(f"Use a relative link for project Pages: {html.relative_to(destination)} -> {link}")
                continue
            target = (html.parent / link).resolve()
            if not target.is_relative_to(destination):
                errors.append(f"Link escapes site: {html.relative_to(destination)} -> {link}")
                continue
            if target.is_dir():
                target /= "index.html"
            if not target.is_file():
                errors.append(f"Missing target: {html.relative_to(destination)} -> {link}")
    if errors:
        raise ValueError("\n".join(errors))
    return checked


def stage(root: Path, destination: Path):
    root = root.resolve()
    destination = destination.resolve()
    if destination == root or root.is_relative_to(destination):
        raise ValueError("Destination must not be the repository or an ancestor")
    if any(destination.is_relative_to(root / directory) for directory in PUBLIC_DIRECTORIES):
        raise ValueError("Destination must be outside public source directories")
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError("Destination must be absent or empty; existing files are never deleted")
    files = list(public_files(root))
    destination.mkdir(parents=True, exist_ok=True)
    for source in files:
        target = destination / source.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    (destination / ".nojekyll").write_text("", encoding="utf-8")
    links = validate_links(destination)
    return {
        "destination": str(destination),
        "files": len(files) + 1,
        "local_html_links_checked": links,
        "site_bytes": sum(path.stat().st_size for path in destination.rglob("*") if path.is_file()),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = stage(args.root, args.output)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Pages preparation failed: {exc}\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
