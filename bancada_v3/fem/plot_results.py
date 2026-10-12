"""Scientific two-panel field/error plot from computed FEM data; Matplotlib Agg."""
from pathlib import Path
import csv
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

BASE = Path(__file__).with_name('outputs')


def main():
    plt.rcParams.update({'font.size': 11, 'font.family': 'DejaVu Sans',
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'svg.fonttype': 'none', 'svg.hashsalt': 'nucleo-fem-v3'})
    fig, (field, error) = plt.subplots(2, 1, figsize=(10, 7.6), sharex=True,
                                      gridspec_kw={'height_ratios': [2, 1]}, layout='constrained')
    report = json.loads((BASE/'resultados.json').read_text(encoding='utf-8'))
    for i, (case, label, color) in enumerate([
            ('coarse_box040', 'Grossa · semilado 0,4 m', '#b45309'),
            ('fine_box040', 'Fina · semilado 0,4 m', '#2563eb'),
            ('fine_box060', 'Fina · semilado 0,6 m', '#15803d')]):
        with (BASE/f'{case}_eixo.csv').open(newline='', encoding='utf-8') as stream:
            rows = list(csv.DictReader(stream))
        z = np.array([float(r['z_local_m'])*1000 for r in rows])
        b = np.array([float(r['Bz_recovered_T'])*1e6 for r in rows])
        ref = np.array([float(r['Bz_pack_integral_T'])*1e6 for r in rows])
        if i == 0:
            field.plot(z, ref, color='#111827', lw=2.4, label='Referência: integral do pacote')
        field.plot(z, b, color=color, lw=1.8, label=f'FEM {label}')
        error.plot(z, 100*(b/ref-1), color=color, lw=1.8, label=label)
    field.set_ylabel('Campo axial $B_z$ (μT)')
    field.set_title('FEM 3D magnetostático: campo axial e erro frente à referência', loc='left', weight='bold')
    field.legend(loc='lower center', frameon=True, fontsize=9)
    field.grid(alpha=.22)
    field.set_ylim(0, 73)
    error.axhline(0, color='#111827', lw=.8)
    error.set_xlabel('Posição axial local z (mm); origem no meio da bancada')
    error.set_ylabel('Erro relativo assinado (%)')
    error.grid(alpha=.22)
    error.set_xlim(-120, 120)
    error.set_xticks(np.arange(-120, 121, 30))
    final = report['cases'][-1]
    text = (f'2 × 50 espiras · raio 100 mm · corrente CC 0,150 A em cada bobina\n'
            f'Malha fina maior: erro central {100*final["center_relative_error"]:.2f}% · '
            f'RMS no eixo {100*final["axis_rms_relative_error"]:.2f}% · '
            f'maior erro no eixo {100*final["axis_max_relative_error"]:.2f}%\n'
            'Campo FEM recuperado por média nodal de volume. Valores calculados; não são medições.')
    fig.suptitle(text, fontsize=10, y=1.065, ha='left', x=.08)
    fig.savefig(BASE/'campo_eixo_comparacao.png', dpi=170, bbox_inches='tight')
    fig.savefig(BASE/'campo_eixo_comparacao.svg', bbox_inches='tight', metadata={'Date': None})
    plt.close(fig)
    print('Scientific plots generated: campo_eixo_comparacao.png and .svg')


if __name__ == '__main__':
    main()
