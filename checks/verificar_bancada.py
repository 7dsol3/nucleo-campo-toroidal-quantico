"""Executa verificacoes digitais V3; nunca conecta instrumentos nem energiza a bancada."""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    checks = []
    with tempfile.TemporaryDirectory(prefix='nucleo-v3-tests-') as temporary:
        commands = [
            ('dimensionamento', ['bancada_v3/eletronica/calculos.py', '--output', str(Path(temporary) / 'dimensionamento.json')]),
            ('filtro', ['bancada_v3/aquisicao/filtro.py']),
            ('fem_artefatos', ['bancada_v3/fem/validate_artifacts.py']),
            ('medicoes', ['bancada_v3/medicoes/testes.py', '--json-output', str(Path(temporary) / 'medicoes.json')]),
            ('medicoes_cc', ['bancada_v3/medicoes/testes_cc.py']),
            ('captura', ['-m', 'unittest', 'discover', '-s', 'bancada_v3/aquisicao', '-p', 'test_*.py']),
            ('controle', ['-m', 'unittest', 'discover', '-s', 'bancada_v3/controle', '-p', 'test_*.py']),
        ]
        for name, command in commands:
            process = subprocess.run([sys.executable, '-X', 'utf8', '-B', *command], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=180)
            record = {'name': name, 'passed': process.returncode == 0}
            found = re.search(r'Ran (\d+) tests?', process.stdout + process.stderr)
            if found:
                record['unit_tests'] = int(found.group(1))
            checks.append(record)
            print(json.dumps(record))
            if process.returncode:
                print((process.stdout + process.stderr)[-6000:], file=sys.stderr)
        # CPython validates syntax only: machine/ADC/DAC and real-time behavior
        # are deliberately not represented as hardware tests.
        ast.parse((ROOT / 'bancada_v3/controle/main.py').read_text(encoding='utf-8-sig'))
        checks.append({'name': 'firmware_syntax_only', 'passed': True})
    result = {
        'origin': 'SOFTWARE_VERIFICATION_NOT_EXPERIMENTAL',
        'all_passed': all(check['passed'] for check in checks),
        'checks': checks,
        'physical_capture_performed': False,
        'firmware_hardware_tested': False,
        'scope': 'Dimensionamento, artefatos FEM calculados e testes sinteticos de algoritmos. Nao valida montagem, calibracao ou hardware.',
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'all_passed': result['all_passed'], 'groups': len(checks)}))
    return 0 if result['all_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
