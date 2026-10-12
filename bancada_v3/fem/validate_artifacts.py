"""Check saved numeric artifacts against the exported mesh/field, without re-solving."""
from pathlib import Path
import argparse
import csv
import json
import math
import zipfile

BASE = Path(__file__).with_name('outputs')


def main(mesh_check=False):
    report = json.loads((BASE/'resultados.json').read_text(encoding='utf-8'))
    assert report['failed'] == 0 and report['passed'] == len(report['checks']) == 23
    assert all(row['passed'] for row in report['checks'])
    assert len(report['cases']) == 3 and len(report['manufactured']) == 2
    for case in report['cases']:
        with (BASE/f'{case["name"]}_eixo.csv').open(newline='', encoding='utf-8') as stream:
            rows = list(csv.DictReader(stream))
        assert len(rows) == 49
        center = rows[24]
        assert math.isclose(float(center['Bz_recovered_T']), case['center_Bz_T'], rel_tol=1e-13)
        for row in rows:
            assert all(math.isfinite(float(value)) for value in row.values())
        with (BASE/f'{case["name"]}_fora_eixo.csv').open(newline='', encoding='utf-8') as stream:
            assert len(list(csv.DictReader(stream))) == 15
    with zipfile.ZipFile(BASE/'fine_box060_mesh.npz') as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == {'points_m.npy', 'tetrahedra.npy', 'winding_region.npy'}
    text = (BASE/'fine_box060.vtu').read_text(encoding='utf-8')
    finest = report['cases'][-1]
    assert f'NumberOfPoints="{finest["nodes"]}"' in text
    assert f'NumberOfCells="{finest["tetrahedra"]}"' in text
    assert 'B_raw_T' in text and 'B_recovered_T' in text and 'A_T_m' in text
    assert (BASE/'campo_eixo.svg').is_file()
    if mesh_check:
        import numpy as np
        import meshio
        mesh = meshio.read(BASE/'fine_box060.vtu')
        with np.load(BASE/'fine_box060_mesh.npz', allow_pickle=False) as packed:
            assert np.array_equal(mesh.points, packed['points_m'])
            assert np.array_equal(mesh.cells_dict['tetra'], packed['tetrahedra'])
            assert np.array_equal(mesh.cell_data_dict['winding_region']['tetra'], packed['winding_region'])
        cells = mesh.cells_dict['tetra']
        xyz = mesh.points[cells]
        design = np.concatenate([np.ones((len(cells), 4, 1)), xyz], axis=2)
        gradients = np.transpose(np.linalg.inv(design)[:, 1:, :], (0, 2, 1))
        derivatives = np.einsum('eic,eij->ecj', mesh.point_data['A_T_m'][cells], gradients)
        curl = np.column_stack([derivatives[:,2,1]-derivatives[:,1,2],
                                derivatives[:,0,2]-derivatives[:,2,0],
                                derivatives[:,1,0]-derivatives[:,0,1]])
        assert np.allclose(curl, mesh.cell_data_dict['B_raw_T']['tetra'], rtol=1e-12, atol=1e-17)
        assert np.all(np.isfinite(mesh.point_data['B_recovered_T']))
        print('Full mesh readback: VTU matches NPZ; exported B_raw equals curl of exported A.')
    print('FEM saved artifacts: 23 numerical checks passed; 3 axis CSV, 3 off-axis CSV, NPZ and VTU coherent.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mesh', action='store_true', help='read back all arrays; requires numpy and meshio')
    main(parser.parse_args().mesh)
