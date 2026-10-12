"""Bundle solver, documentation and computed files for offline reproduction."""
from pathlib import Path
import zipfile

BASE = Path(__file__).resolve().parent


def main():
    target = BASE/'FEM_3D_Resultados.zip'
    entries = [p for p in BASE.rglob('*') if p.is_file() and p != target
               and '__pycache__' not in p.parts and p.suffix != '.pyc']
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for file in sorted(entries):
            archive.write(file, Path('fem')/file.relative_to(BASE))
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(entries)
    print(f'FEM_3D_Resultados.zip: {len(entries)} files, {target.stat().st_size} bytes, CRC checked')


if __name__ == '__main__':
    main()
