"""Generate a standalone scientific SVG from saved numerical CSV; stdlib only."""
from pathlib import Path
import csv
import html

BASE = Path(__file__).with_name('outputs')


def main():
    series = []
    for name, label, color in [('coarse_box040', 'FEM grossa, caixa 0,4 m', '#b45309'),
                                ('fine_box040', 'FEM fina, caixa 0,4 m', '#2563eb'),
                                ('fine_box060', 'FEM fina, caixa 0,6 m', '#15803d')]:
        with (BASE/f'{name}_eixo.csv').open(encoding='utf-8', newline='') as f:
            rows = list(csv.DictReader(f))
        series.append((label, color, [(float(r['z_local_m'])*1000,
                                       float(r['Bz_recovered_T'])*1e6) for r in rows]))
    series.insert(0, ('Referência: pacote contínuo', '#111827',
                      [(float(r['z_local_m'])*1000, float(r['Bz_pack_integral_T'])*1e6) for r in rows]))
    width, height = 960, 600
    left, right, top, bottom = 80, 930, 65, 420
    xmin, xmax, ymin, ymax = -120, 120, 0, 70
    px = lambda x: left+(x-xmin)/(xmax-xmin)*(right-left)
    py = lambda y: bottom-(y-ymin)/(ymax-ymin)*(bottom-top)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
             '<title id="title">Campo axial: FEM 3D e referência independente</title>',
             '<desc id="desc">Duas bobinas de 50 espiras, raio 100 mm, corrente contínua 0,150 A cada. Eixo local em milímetros e campo Bz em microtesla.</desc>',
             '<rect width="960" height="600" fill="white"/>',
             '<g font-family="Arial, sans-serif" fill="#111827">',
             '<text x="80" y="28" font-size="21" font-weight="bold">Campo axial — FEM 3D P1 e referência independente</text>',
             '<text x="80" y="50" font-size="14">2 × 50 espiras; raio 100 mm; corrente CC 0,150 A em cada bobina</text>']
    for x in range(-120, 121, 30):
        parts += [f'<path d="M {px(x):.1f} {top} V {bottom}" stroke="#e5e7eb"/>',
                  f'<text x="{px(x):.1f}" y="444" text-anchor="middle" font-size="13">{x}</text>']
    for y in range(0, 71, 10):
        parts += [f'<path d="M {left} {py(y):.1f} H {right}" stroke="#e5e7eb"/>',
                  f'<text x="66" y="{py(y)+4:.1f}" text-anchor="end" font-size="13">{y}</text>']
    parts += [f'<path d="M {left} {top} V {bottom} H {right}" fill="none" stroke="#111827"/>',
              '<text x="505" y="468" text-anchor="middle" font-size="15">z local (mm), origem no meio da bancada</text>',
              '<text x="24" y="250" transform="rotate(-90 24 250)" text-anchor="middle" font-size="15">Bz (μT)</text>']
    for i, (label, color, values) in enumerate(series):
        coords = ' '.join(f'{px(x):.2f},{py(y):.2f}' for x, y in values)
        parts.append(f'<polyline points="{coords}" stroke="{color}" stroke-width="2.5" fill="none"/>')
        lx, ly = 90+(i%2)*430, 500+(i//2)*25
        parts += [f'<path d="M {lx} {ly} h 28" stroke="{color}" stroke-width="3"/>',
                  f'<text x="{lx+37}" y="{ly+5}" font-size="14">{html.escape(label)}</text>']
    parts += ['<text x="80" y="575" font-size="13">Pontos FEM usam recuperação nodal por volume. Gráfico calculado; não representa medição física.</text>',
              '</g></svg>']
    (BASE/'campo_eixo.svg').write_text('\n'.join(parts), encoding='utf-8')
    print('Generated outputs/campo_eixo.svg from numerical CSV')


if __name__ == '__main__':
    main()
