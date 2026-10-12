"""Executed 3D tetrahedral P1 Galerkin FEM; all coordinates/fields in SI.

Homogeneous permeability only, prescribed steady winding current, zero A on a
finite external cube. This solves -Delta A = mu0 J, NOT a transient AC problem.
See README.md for finite-domain/gauge and homogenized-winding limitations.
"""
from __future__ import annotations

import argparse
import csv
import importlib.metadata
import json
import math
from pathlib import Path
import time

import gmsh
import meshio
import numpy as np
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import cg
from scipy.spatial import cKDTree

MU0 = 4 * math.pi * 1e-7
RADIUS = 0.100
RADIAL = 0.0055
AXIAL = 0.011
CENTERS = (-0.060, 0.060)  # V2 z=65,185 mm, translated by -125 mm
TURNS = 50
CURRENT = 0.150
QP = np.full((4, 4), (5 - math.sqrt(5)) / 20)
np.fill_diagonal(QP, (5 + 3 * math.sqrt(5)) / 20)


def create_mesh(half_extent, coil_h, region_h, far_h, manufactured=False):
    """Gmsh OCC conforming ring/air volumes, linear tetrahedra, no axial reduction."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber('General.Terminal', 0)
        gmsh.option.setNumber('General.NumThreads', 1)
        gmsh.option.setNumber('Mesh.Algorithm3D', 1)
        gmsh.option.setNumber('Mesh.ElementOrder', 1)
        gmsh.option.setNumber('Mesh.RandomSeed', 7)
        gmsh.model.add('manufactured' if manufactured else 'winding_pair')
        occ = gmsh.model.occ
        cube = occ.addBox(-half_extent, -half_extent, -half_extent,
                          2 * half_extent, 2 * half_extent, 2 * half_extent)
        coils = []
        if not manufactured:
            for center in CENTERS:
                outer = occ.addCylinder(0, 0, center - AXIAL/2, 0, 0, AXIAL,
                                        RADIUS + RADIAL/2)
                inner = occ.addCylinder(0, 0, center - AXIAL/2, 0, 0, AXIAL,
                                        RADIUS - RADIAL/2)
                ring, _ = occ.cut([(3, outer)], [(3, inner)])
                coils += ring
            _, mapping = occ.fragment([(3, cube)], coils)
            coils = [entity for group in mapping[1:] for entity in group if entity[0] == 3]
        occ.synchronize()
        coil_tags = {tag for dim, tag in coils}
        if manufactured:
            gmsh.option.setNumber('Mesh.MeshSizeMin', far_h)
            gmsh.option.setNumber('Mesh.MeshSizeMax', far_h)
        else:
            surfaces = sorted({tag for dim, tag in gmsh.model.getBoundary(coils, False, False)})
            distance = gmsh.model.mesh.field.add('Distance')
            gmsh.model.mesh.field.setNumbers(distance, 'SurfacesList', surfaces)
            gmsh.model.mesh.field.setNumber(distance, 'Sampling', 80)
            threshold = gmsh.model.mesh.field.add('Threshold')
            for key, value in {'InField': distance, 'SizeMin': coil_h,
                               'SizeMax': far_h, 'DistMin': .002,
                               'DistMax': .08}.items():
                gmsh.model.mesh.field.setNumber(threshold, key, value)
            central = gmsh.model.mesh.field.add('Box')
            for key, value in {'VIn': region_h, 'VOut': far_h,
                               'XMin': -.14, 'XMax': .14, 'YMin': -.14,
                               'YMax': .14, 'ZMin': -.15, 'ZMax': .15,
                               'Thickness': .04}.items():
                gmsh.model.mesh.field.setNumber(central, key, value)
            minimum = gmsh.model.mesh.field.add('Min')
            gmsh.model.mesh.field.setNumbers(minimum, 'FieldsList', [threshold, central])
            gmsh.model.mesh.field.setAsBackgroundMesh(minimum)
            gmsh.option.setNumber('Mesh.MeshSizeExtendFromBoundary', 0)
            gmsh.option.setNumber('Mesh.MeshSizeFromPoints', 0)
            gmsh.option.setNumber('Mesh.MeshSizeFromCurvature', 0)
        gmsh.model.mesh.generate(3)
        tags, coordinates, _ = gmsh.model.mesh.getNodes()
        points = np.asarray(coordinates).reshape(-1, 3)
        tag_to_index = np.empty(int(np.max(tags)) + 1, dtype=np.int64)
        tag_to_index[np.asarray(tags, dtype=np.int64)] = np.arange(len(tags))
        cells, regions = [], []
        for _, tag in gmsh.model.getEntities(3):
            types, _, connectivity = gmsh.model.mesh.getElements(3, tag)
            for kind, nodes in zip(types, connectivity):
                if kind != 4:
                    raise RuntimeError(f'Expected linear tetrahedron type 4, got {kind}')
                block = tag_to_index[np.asarray(nodes, dtype=np.int64).reshape(-1, 4)]
                cells.append(block)
                regions.append(np.full(len(block), 1 if tag in coil_tags else 0, dtype=np.int8))
        return points, np.vstack(cells), np.concatenate(regions)
    finally:
        gmsh.finalize()


def elements(points, cells):
    positions = points[cells]
    design = np.concatenate([np.ones((len(cells), 4, 1)), positions], axis=2)
    inverse = np.linalg.inv(design)
    gradients = np.transpose(inverse[:, 1:, :], (0, 2, 1))
    volume = np.abs(np.linalg.det(positions[:, 1:, :] - positions[:, :1, :])) / 6
    if np.any(volume < 1e-20):
        raise RuntimeError('Degenerate tetrahedron')
    return positions, gradients, volume


def assemble(points, cells, gradients, volume, source):
    local = volume[:, None, None] * np.einsum('eik,ejk->eij', gradients, gradients)
    rows = np.repeat(cells, 4, axis=1).ravel()
    columns = np.tile(cells, (1, 4)).ravel()
    stiffness = coo_matrix((local.ravel(), (rows, columns)),
                           shape=(len(points), len(points))).tocsr()
    # Four-point degree-2 tetrahedron quadrature for f*N_i.
    q_positions = np.einsum('qi,eij->eqj', QP, points[cells])
    f = source(q_positions)
    load_local = volume[:, None, None] * np.einsum('eqc,qi->eic', f, QP) / 4
    rhs = np.zeros((len(points), 3))
    np.add.at(rhs, cells.ravel(), load_local.reshape(-1, 3))
    return stiffness, rhs


def solve_dirichlet(points, stiffness, rhs, half_extent):
    boundary = np.any(np.isclose(np.abs(points), half_extent, rtol=0, atol=2e-10), axis=1)
    free = np.flatnonzero(~boundary)
    k = stiffness[free][:, free].tocsr()
    preconditioner = diags(1 / k.diagonal())
    solution = np.zeros_like(rhs)
    iterations = []
    for component in range(3):
        count = [0]
        def callback(_):
            count[0] += 1
        b = rhs[free, component]
        if np.linalg.norm(b) == 0:
            iterations.append(0)
            continue
        x, info = cg(k, b, M=preconditioner, rtol=1e-10, atol=0,
                     maxiter=6000, callback=callback)
        if info != 0:
            raise RuntimeError(f'CG did not converge: component {component}, info {info}')
        solution[free, component] = x
        iterations.append(count[0])
    residual = stiffness @ solution - rhs
    relative = np.linalg.norm(residual[free]) / max(np.linalg.norm(rhs[free]), 1e-30)
    symmetry_error = stiffness - stiffness.T
    symmetry = np.max(np.abs(symmetry_error.data)) if symmetry_error.nnz else 0.
    return solution, {'free_nodes': len(free), 'dirichlet_nodes': int(boundary.sum()),
                       'cg_iterations_xyz': iterations, 'relative_free_residual': float(relative),
                       'matrix_symmetry_max_abs': float(symmetry),
                       'minimum_stiffness_diagonal': float(k.diagonal().min())}


def magnetic_source(regions):
    density = TURNS * CURRENT / (RADIAL * AXIAL)
    def source(q):
        radius = np.hypot(q[:, :, 0], q[:, :, 1])
        current = np.zeros_like(q)
        current[:, :, 0] = -q[:, :, 1] / np.maximum(radius, 1e-30)
        current[:, :, 1] = q[:, :, 0] / np.maximum(radius, 1e-30)
        return MU0 * density * regions[:, None, None] * current
    return source


def field_from_potential(potential, cells, gradients, volume, npoints):
    # derivatives[e, component_of_A, coordinate_derivative]
    derivatives = np.einsum('eic,eij->ecj', potential[cells], gradients)
    b = np.column_stack([derivatives[:, 2, 1] - derivatives[:, 1, 2],
                         derivatives[:, 0, 2] - derivatives[:, 2, 0],
                         derivatives[:, 1, 0] - derivatives[:, 0, 1]])
    divergence = np.trace(derivatives, axis1=1, axis2=2)
    # Volume-weighted nodal recovery is explicitly a display/sampling operation.
    recovered = np.zeros((npoints, 3))
    weights = np.zeros(npoints)
    for node in range(4):
        np.add.at(recovered, cells[:, node], b * volume[:, None])
        np.add.at(weights, cells[:, node], volume)
    recovered /= weights[:, None]
    return b, recovered, divergence


def sample_field(points, cells, values, queries):
    positions, _, _ = elements(points, cells)
    tree = cKDTree(positions.mean(axis=1))
    result = []
    for query in queries:
        _, candidates = tree.query(query, k=min(120, len(cells)))
        found = None
        for index in np.atleast_1d(candidates):
            x = positions[index]
            coefficients = np.linalg.solve((x[1:] - x[0]).T, query - x[0])
            barycentric = np.r_[1 - coefficients.sum(), coefficients]
            if np.all(barycentric >= -1e-9):
                found = barycentric @ values[cells[index]]
                break
        if found is None:
            raise RuntimeError(f'No containing tetrahedron located for {query}')
        result.append(found)
    return np.asarray(result)


def axis_reference(z_values, distributed=True, quadrature_order=24):
    """Independent loop-axis formula, integrated across rectangular pack or V2 filaments."""
    if distributed:
        x, w = np.polynomial.legendre.leggauss(quadrature_order)
        radii = RADIUS + x * RADIAL / 2
        offsets = x * AXIAL / 2
        rr, zz = np.meshgrid(radii, offsets, indexing='ij')
        weights = np.outer(w, w) / 4 * TURNS * CURRENT
    else:
        radii = RADIUS + (np.arange(5) - 2) * .0011
        offsets = (np.arange(10) - 4.5) * .0011
        rr, zz = np.meshgrid(radii, offsets, indexing='ij')
        weights = np.full_like(rr, CURRENT)
    result = np.zeros(len(z_values))
    for center in CENTERS:
        dz = np.asarray(z_values)[:, None, None] - center - zz[None]
        result += np.sum(MU0/2 * weights * rr**2 / (rr**2 + dz**2)**1.5, axis=(1, 2))
    return result


def volume_biot_savart(queries, radial_order=10, angular_order=256):
    """Independent verification only: quadrature of prescribed volume J, never the FEM solver."""
    x, w = np.polynomial.legendre.leggauss(radial_order)
    radii = RADIUS + x*RADIAL/2
    offsets = x*AXIAL/2
    phi = (np.arange(angular_order) + .5) * 2*math.pi/angular_order
    rr, zz, pp = np.meshgrid(radii, offsets, phi, indexing='ij')
    weights = (w[:, None, None]*w[None, :, None]*RADIAL*AXIAL/4 *
               2*math.pi/angular_order * rr).ravel()
    directions = np.column_stack([-np.sin(pp).ravel(), np.cos(pp).ravel(), np.zeros(pp.size)])
    base = np.column_stack([(rr*np.cos(pp)).ravel(), (rr*np.sin(pp)).ravel(), zz.ravel()])
    result = np.zeros((len(queries), 3))
    for center in CENTERS:
        sources = base + np.array([0, 0, center])
        for i, query in enumerate(queries):
            delta = query - sources
            radius = np.linalg.norm(delta, axis=1)
            result[i] += np.sum(np.cross(directions, delta) *
                         (weights/radius**3)[:, None], axis=0)
    return result * MU0/(4*math.pi) * TURNS*CURRENT/(RADIAL*AXIAL)


def manufactured_test(mesh_h):
    half = .5
    points, cells, regions = create_mesh(half, mesh_h, mesh_h, mesh_h, manufactured=True)
    positions, gradients, volume = elements(points, cells)
    def source(q):
        f = np.zeros_like(q)
        f[:, :, 0] = 3 * math.pi**2 * np.prod(np.sin(math.pi*(q + half)), axis=2)
        return f
    stiffness, rhs = assemble(points, cells, gradients, volume, source)
    solution, diagnostics = solve_dirichlet(points, stiffness, rhs, half)
    q = np.einsum('qi,eij->eqj', QP, positions)
    exact = np.prod(np.sin(math.pi*(q + half)), axis=2)
    numerical = np.einsum('qi,ei->eq', QP, solution[cells, 0])
    error = np.sqrt(np.sum(volume[:, None] * (numerical - exact)**2 / 4))
    norm = np.sqrt(np.sum(volume[:, None] * exact**2 / 4))
    return {'mesh_h_m': mesh_h, 'nodes': len(points), 'tetrahedra': len(cells),
            'relative_L2_error': float(error/norm), **diagnostics}


def magnetic_case(name, half_extent, coil_h, region_h, far_h, output, export=False):
    started = time.perf_counter()
    points, cells, regions = create_mesh(half_extent, coil_h, region_h, far_h)
    positions, gradients, volume = elements(points, cells)
    stiffness, rhs = assemble(points, cells, gradients, volume, magnetic_source(regions))
    potential, diagnostics = solve_dirichlet(points, stiffness, rhs, half_extent)
    b, recovered, divergence = field_from_potential(potential, cells, gradients, volume, len(points))
    z = np.linspace(-.12, .12, 49)
    queries = np.column_stack([np.zeros_like(z), np.zeros_like(z), z])
    measured = sample_field(points, cells, recovered, queries)
    reference = axis_reference(z)
    v2_reference = axis_reference(z, distributed=False)
    error = np.abs(measured[:, 2] / reference - 1)
    off_queries = np.array([[xx, .020, zz] for xx in (.025, .050, .075)
                            for zz in (-.090, -.030, 0., .030, .090)])
    off_field = sample_field(points, cells, recovered, off_queries)
    off_reference = volume_biot_savart(off_queries)
    off_error = np.linalg.norm(off_field-off_reference, axis=1)/np.linalg.norm(off_reference, axis=1)
    with (output/f'{name}_fora_eixo.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(['x_m','y_m','z_local_m','Bx_recovered_T','By_recovered_T','Bz_recovered_T',
                         'Bx_volume_reference_T','By_volume_reference_T','Bz_volume_reference_T','relative_vector_error'])
        for query, field, ref, err in zip(off_queries, off_field, off_reference, off_error):
            writer.writerow([*query,*field,*ref,err])
    gauge_ratio = np.sqrt(np.dot(volume, divergence**2) /
                          np.sum(volume[:, None] * b**2))
    energy_b = float(np.sum(volume[:, None] * b**2)/(2*MU0))
    energy_grad = float(np.sum(potential * (stiffness @ potential))/(2*MU0))
    source_work = float(np.sum(potential * rhs)/(2*MU0))
    with (output/f'{name}_eixo.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(['z_local_m', 'z_v2_m', 'Bx_recovered_T', 'By_recovered_T',
                         'Bz_recovered_T', 'Bz_pack_integral_T', 'Bz_v2_filaments_T',
                         'relative_error_pack'])
        for zz, vector, analytic, v2, err in zip(z, measured, reference, v2_reference, error):
            writer.writerow([zz, zz+.125, *vector, analytic, v2, err])
    if export:
        meshio.write(output/f'{name}.vtu', meshio.Mesh(points, [('tetra', cells)],
                     point_data={'A_T_m': potential, 'B_recovered_T': recovered},
                     cell_data={'B_raw_T': [b], 'div_A_T': [divergence],
                                'winding_region': [regions]}), binary=True, compression='zlib')
        np.savez_compressed(output/f'{name}_mesh.npz', points_m=points,
                            tetrahedra=cells, winding_region=regions)
    analytic_volume = 2 * (2*math.pi*RADIUS*RADIAL*AXIAL)
    return {'name': name, 'domain_half_extent_m': half_extent, 'coil_mesh_h_m': coil_h,
            'central_mesh_h_m': region_h, 'far_mesh_h_m': far_h,
            'nodes': len(points), 'tetrahedra': len(cells), 'winding_tetrahedra': int(regions.sum()),
            'center_Bz_T': float(measured[len(z)//2, 2]),
            'center_reference_pack_T': float(reference[len(z)//2]),
            'center_reference_v2_T': float(v2_reference[len(z)//2]),
            'axis_max_relative_error': float(error.max()),
            'axis_rms_relative_error': float(np.sqrt(np.mean(error**2))),
            'off_axis_max_relative_vector_error': float(off_error.max()),
            'off_axis_rms_relative_vector_error': float(np.sqrt(np.mean(off_error**2))),
            'center_relative_error': float(error[len(z)//2]),
            'winding_volume_relative_error': float(np.sum(volume[regions == 1])/analytic_volume - 1),
            'gauge_divA_over_curlA_L2': float(gauge_ratio),
            'magnetic_energy_J': energy_b,
            'gradient_energy_with_gauge_J': energy_grad,
            'half_source_A_work_J': source_work,
            'weak_energy_relative_balance': float(abs(energy_grad/source_work-1)),
            'elapsed_s': time.perf_counter()-started, **diagnostics}


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    report = {'schema': 'fem-v3-1', 'method': '3D tetrahedral P1 Galerkin vector Poisson',
              'physics': 'homogeneous magnetostatics with prescribed DC winding current',
              'current_A_each': CURRENT, 'turns_each': TURNS,
              'source_density_A_m2': TURNS*CURRENT/(RADIAL*AXIAL),
              'software': {name: importlib.metadata.version(name) for name in ('numpy', 'scipy', 'gmsh', 'meshio')},
              'manufactured': [], 'cases': [], 'checks': []}
    for h in (.24, .10):
        case = manufactured_test(h)
        report['manufactured'].append(case)
        print('Manufactured:', json.dumps(case), flush=True)
    for case in [('coarse_box040', .4, .004, .018, .080),
                 ('fine_box040', .4, .0025, .010, .080),
                 ('fine_box060', .6, .0025, .010, .100)]:
        result = magnetic_case(*case, output, export=case[0] == 'fine_box060')
        report['cases'].append(result)
        (output/'resultados.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        print('Magnetic:', json.dumps(result), flush=True)
    coarse, fine, far = report['cases']
    report['mesh_change_center_relative'] = abs(fine['center_Bz_T']/coarse['center_Bz_T']-1)
    report['domain_change_center_relative'] = abs(far['center_Bz_T']/fine['center_Bz_T']-1)
    def check(name, passed, value):
        report['checks'].append({'name': name, 'passed': bool(passed), 'value': value})
    check('manufactured_error_decreases', report['manufactured'][1]['relative_L2_error'] <
          report['manufactured'][0]['relative_L2_error'], [m['relative_L2_error'] for m in report['manufactured']])
    check('manufactured_fine_L2_below_5percent', report['manufactured'][1]['relative_L2_error'] < .05,
          report['manufactured'][1]['relative_L2_error'])
    for c in report['manufactured'] + report['cases']:
        label = c.get('name', str(c.get('mesh_h_m')))
        check(label + '_weak_residual', c['relative_free_residual'] < 2e-10, c['relative_free_residual'])
        check(label + '_matrix_symmetric_positive_diagonal', c['matrix_symmetry_max_abs'] < 1e-13 and
              c['minimum_stiffness_diagonal'] > 0, c['matrix_symmetry_max_abs'])
    for c in report['cases']:
        check(c['name']+'_weak_energy_balance', c['weak_energy_relative_balance'] < 1e-8,
              c['weak_energy_relative_balance'])
        check(c['name']+'_coil_volume_within_1percent', abs(c['winding_volume_relative_error']) < .01,
              c['winding_volume_relative_error'])
    check('fine_far_center_within_5percent_reference', far['center_relative_error'] < .05,
          far['center_relative_error'])
    check('fine_far_axis_rms_within_7percent_reference', far['axis_rms_relative_error'] < .07,
          far['axis_rms_relative_error'])
    check('fine_far_off_axis_rms_within_7percent_reference', far['off_axis_rms_relative_vector_error'] < .07,
          far['off_axis_rms_relative_vector_error'])
    check('finite_box_center_change_below_3percent', report['domain_change_center_relative'] < .03,
          report['domain_change_center_relative'])
    check('mesh_center_change_below_8percent', report['mesh_change_center_relative'] < .08,
          report['mesh_change_center_relative'])
    report['passed'] = sum(c['passed'] for c in report['checks'])
    report['failed'] = len(report['checks']) - report['passed']
    (output/'resultados.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'passed': report['passed'], 'failed': report['failed']}), flush=True)
    return report['failed']


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('outputs'))
    args = parser.parse_args()
    raise SystemExit(1 if run(args.output) else 0)
