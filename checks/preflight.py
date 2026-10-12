"""Read-only publication checks; Python 3.12 stdlib, Windows/Linux/macOS.

This checks digital artifact integrity, not experimental hardware operation.
Run from the repository with: python checks/preflight.py
"""
from __future__ import annotations

import argparse
import csv
import hashlib
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import struct
import sys
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree
import zipfile


class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in {"href", "src"} and value:
                parsed = urlsplit(value)
                if not parsed.scheme and not parsed.netloc and parsed.path:
                    self.links.append(unquote(parsed.path))


class PublicationChecks:
    def __init__(self, root):
        self.root = root.resolve()
        self.checked = 0
        self.errors = []

    def check(self, condition, message):
        self.checked += 1
        if not condition:
            self.errors.append(message)

    def name(self, path):
        return path.relative_to(self.root).as_posix()

    def json_file(self, path):
        def reject_constant(value):
            raise ValueError("non-finite JSON constant")
        try:
            value = json.loads(path.read_text(encoding="utf-8-sig"),
                               parse_constant=reject_constant)
        except (ValueError, OSError, UnicodeError) as exc:
            self.check(False, f"invalid JSON: {self.name(path)} ({type(exc).__name__})")
            return None
        self.check(True, self.name(path))
        return value

    def manifest(self, project):
        manifest = project / "SHA256SUMS.txt"
        self.check(manifest.is_file(), f"missing checksum manifest: {self.name(manifest)}")
        if not manifest.is_file():
            return
        recorded = set()
        for number, line in enumerate(manifest.read_text(encoding="utf-8-sig").splitlines(), 1):
            if not line.strip() or line.startswith("#"):
                continue
            match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
            self.check(match is not None, f"invalid checksum line {number}: {self.name(manifest)}")
            if match is None:
                continue
            expected, name = match.groups()
            target = project / name
            valid_path = not Path(name).is_absolute() and ".." not in Path(name).parts
            self.check(valid_path, f"unsafe manifest path: {self.name(manifest)} line {number}")
            if not valid_path:
                continue
            self.check(name not in recorded, f"duplicate checksum path: {self.name(manifest)} line {number}")
            recorded.add(name)
            self.check(target.is_file(), f"missing checksum artifact: {self.name(target)}")
            if target.is_file():
                actual = hashlib.sha256(target.read_bytes()).hexdigest()
                self.check(actual == expected, f"checksum mismatch: {self.name(target)}")
        actual_files = {file.relative_to(project).as_posix()
                        for file in project.rglob("*")
                        if file.is_file() and file.name != "SHA256SUMS.txt"
                        and "__pycache__" not in file.parts}
        self.check(recorded == actual_files,
                   f"checksum coverage mismatch: {self.name(project)} "
                   f"(missing {len(actual_files - recorded)}, obsolete {len(recorded - actual_files)})")

    def links(self, html):
        parser = LocalLinks()
        parser.feed(html.read_text(encoding="utf-8-sig"))
        for link in parser.links:
            target = self.root / link.lstrip("/") if link.startswith("/") else html.parent / link
            self.check(target.is_file(), f"missing HTML target: {self.name(html)} -> {link}")

    def scene(self, project):
        path = project / "cad" / "scene.json"
        scene = self.json_file(path)
        if scene is None:
            return
        parts = scene.get("parts", [])
        self.check(scene.get("units") == "mm", "CAD scene must declare millimeters")
        self.check(isinstance(parts, list) and len(parts) > 0, "empty CAD scene")
        identifiers = [part.get("id") for part in parts]
        self.check(len(identifiers) == len(set(identifiers)), "duplicate CAD part identifiers")
        for part in parts:
            name = part.get("id", "unnamed")
            vertices, faces = part.get("vertices", []), part.get("faces", [])
            valid_vertices = (bool(vertices) and len(vertices) % 3 == 0
                              and all(isinstance(value, (int, float)) and math.isfinite(value)
                                      for value in vertices))
            valid_faces = (bool(faces) and len(faces) % 3 == 0
                           and all(isinstance(value, int) and not isinstance(value, bool)
                                   and 0 <= value < len(vertices) // 3 for value in faces))
            self.check(valid_vertices and valid_faces, f"invalid indexed CAD geometry: {name}")
        path = project / "cad" / "validacao_mesh.json"
        meshes = self.json_file(path)
        if isinstance(meshes, dict):
            for name, mesh in meshes.items():
                valid = (mesh.get("boundary_edges") == 0
                         and mesh.get("nonmanifold_edges") == 0
                         and mesh.get("consistent_orientation") is True
                         and mesh.get("volume_mm3", 0) > 0)
                self.check(valid, f"stored mesh validation failed: {name}")

    def formats(self, files):
        for path in files:
            suffix = path.suffix.lower()
            if suffix == ".json":
                self.json_file(path)
            elif suffix == ".html":
                self.links(path)
            elif suffix == ".svg":
                try:
                    ElementTree.parse(path)
                    self.check(True, self.name(path))
                except (ElementTree.ParseError, OSError):
                    self.check(False, f"invalid SVG XML: {self.name(path)}")
            elif suffix == ".stl":
                raw = path.read_bytes()
                valid = len(raw) >= 84
                triangles = struct.unpack_from("<I", raw, 80)[0] if valid else 0
                self.check(valid and triangles > 0 and len(raw) == 84 + 50 * triangles,
                           f"invalid binary STL length: {self.name(path)}")
            elif suffix == ".pdf":
                raw = path.read_bytes()
                self.check(raw.startswith(b"%PDF-") and b"%%EOF" in raw[-2048:],
                           f"invalid PDF boundary markers: {self.name(path)}")
            elif suffix == ".docx":
                try:
                    with zipfile.ZipFile(path) as archive:
                        valid = "word/document.xml" in archive.namelist() and archive.testzip() is None
                    self.check(valid, f"invalid DOCX container: {self.name(path)}")
                except (zipfile.BadZipFile, OSError):
                    self.check(False, f"invalid DOCX container: {self.name(path)}")

    def publication_files(self, files):
        patterns = [
            re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
            re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
            re.compile(r"AKIA[0-9A-Z]{16}"),
            re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        ]
        text_extensions = {".py", ".js", ".html", ".css", ".md", ".txt", ".yml", ".yaml", ".json", ".csv", ".svg"}
        for path in files:
            relative = self.name(path)
            self.check(path.stat().st_size < 100 * 1024 * 1024,
                       f"file reaches GitHub's 100 MiB limit: {relative}")
            self.check("__pycache__" not in path.parts and path.suffix.lower() not in {".pyc", ".pyo"},
                       f"Python cache must not be published: {relative}")
            self.check(path.name != ".env" and not path.name.startswith(".env."),
                       f"environment file must not be published: {relative}")
            if path.suffix.lower() in text_extensions:
                try:
                    text = path.read_text(encoding="utf-8-sig")
                except UnicodeError:
                    self.check(False, f"text file is not UTF-8: {relative}")
                    continue
                self.check(not any(pattern.search(text) for pattern in patterns),
                           f"credential pattern found (value omitted): {relative}")

    def bom(self, project):
        path = project / "lista_completa_pecas.csv"
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream, delimiter=";"))
        self.check(bool(rows), "empty V2 bill of materials")
        for row in rows:
            target = row.get("arquivo", "")
            self.check(not target or (project / "cad" / target).is_file(),
                       f"missing bill-of-materials CAD artifact: {target}")

    def run(self):
        for name in ("README.md", ".gitignore", ".gitattributes"):
            self.check((self.root / name).is_file(), f"missing repository file: {name}")
        v2 = self.root / "nucleo_integral_v2"
        self.check(v2.is_dir(), "missing V2 project directory")
        if not v2.is_dir():
            return
        files = sorted(path for path in self.root.rglob("*")
                       if path.is_file() and ".git" not in path.relative_to(self.root).parts)
        self.publication_files(files)
        self.formats(files)
        self.scene(v2)
        self.bom(v2)
        self.manifest(v2)
        v1 = self.root / "nucleo_toroidal"
        if v1.is_dir():
            self.manifest(v1)
        v3 = self.root / "bancada_v3"
        if v3.is_dir():
            self.manifest(v3)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    checks = PublicationChecks(args.root)
    try:
        checks.run()
    except (OSError, KeyError, TypeError, ValueError) as exc:
        checks.check(False, f"preflight could not finish: {type(exc).__name__}: {exc}")
    print(json.dumps({"passed": not checks.errors, "checks": checks.checked,
                      "failures": len(checks.errors),
                      "scope": "Digital artifact integrity; no physical experiment."}, ensure_ascii=False))
    for error in checks.errors:
        print(error, file=sys.stderr)
    return 1 if checks.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
