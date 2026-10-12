"""Atualiza checksums V3 e empacota a bancada com suas dependencias V1/V2.

Nao captura instrumentos. Os bytes dos documentos/modelos existentes sao
preservados. O ZIP de distribuicao nao pode conter uma copia de si proprio.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from preparar_pages import public_files

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'artifacts/Nucleo_Bancada_V3.zip')
    args = parser.parse_args()
    target = args.output.resolve()
    base = ROOT / 'bancada_v3'
    if target.is_relative_to(base):
        parser.error('O ZIP deve ficar fora de bancada_v3 para evitar autorreferencia')
    manifest = base / 'SHA256SUMS.txt'
    files = sorted(p for p in base.rglob('*') if p.is_file() and p != manifest
                   and '__pycache__' not in p.parts and p.suffix not in ('.pyc', '.pyo'))
    manifest.write_text(''.join(f'{digest(p)}  {p.relative_to(base).as_posix()}\n' for p in files), encoding='utf-8')
    # Includes V2: the analyzers import its model; CAD and configuration must
    # remain in the same relative layout. V1/reference assets preserve context.
    entries = set(public_files(ROOT))
    entries.update(p for p in (ROOT / 'checks').glob('*.py') if p.is_file())
    entries.update(p for p in (ROOT / '.github/workflows').glob('*.yml') if p.is_file())
    entries.update(ROOT / name for name in ('.gitignore', '.gitattributes', 'LICENSE') if (ROOT / name).is_file())
    entries = sorted(p for p in entries if p.resolve() != target)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in entries:
            info = zipfile.ZipInfo(path.relative_to(ROOT).as_posix(), (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=6)
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None or len(archive.namelist()) != len(entries):
            raise ValueError('Falha de integridade do ZIP')
        for path in files + [manifest]:
            if archive.read(path.relative_to(ROOT).as_posix()) != path.read_bytes():
                raise ValueError('Bytes diferentes no pacote: ' + str(path))
    print(json.dumps({'archive': str(target), 'files': len(entries), 'bytes': target.stat().st_size,
                      'sha256': digest(target), 'v3_checksums': len(files),
                      'includes_model_dependencies': True, 'crc_and_v3_bytes_verified': True}))


if __name__ == '__main__':
    main()
