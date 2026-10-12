"""Protótipo eletromagnético V2, SI, RMS, sem dependências externas.

Não é um modelo de energia do vácuo, gravitação controlada ou física quântica.
Execute: py modelo_integral.py --output outputs
"""
from __future__ import annotations

import argparse
import cmath
import copy
import csv
import json
import math
from functools import lru_cache
from pathlib import Path

MU0 = 4 * math.pi * 1e-7
G = 6.67430e-11
C_LIGHT = 299792458.0
INCH_M = 0.0254


def load_config(path=None):
    config = json.loads((Path(path) if path else Path(__file__).with_name('configuracao.json')).read_text(encoding='utf-8'))
    validate_config(config)
    return config


def positive(value, name, allow_zero=False):
    if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0 or (value == 0 and not allow_zero):
        raise ValueError(f'{name} deve ser finito e {"não negativo" if allow_zero else "positivo"}.')


def validate_config(config):
    g, c, p, t, n = (config[k] for k in ('geometry', 'circuit', 'receiver', 'toroidal', 'numerics'))
    for k in ('coil_mean_radius_m', 'wire_bare_diameter_m', 'wire_pitch_m', 'copper_resistivity_20c_ohm_m'):
        positive(g[k], f'geometry.{k}')
    positive(g['coil_leads_each_m'], 'leads', True)
    if not math.isfinite(g['temperature_c']) or copper_resistivity(g) <= 0:
        raise ValueError('Temperatura fora da aproximação linear de resistividade.')
    for k in ('radial_layers', 'turns_per_layer'):
        if g[k] != int(g[k]) or g[k] < 1:
            raise ValueError('Contagens de espiras e camadas devem ser inteiras positivas.')
    if g['wire_pitch_m'] < g['wire_bare_diameter_m']:
        raise ValueError('Passo do fio não pode ser menor que diâmetro do cobre.')
    radial = (g['radial_layers'] - 1) * g['wire_pitch_m'] / 2
    if g['coil_mean_radius_m'] <= radial + g['wire_pitch_m'] / 2:
        raise ValueError('Raio insuficiente para o enrolamento.')
    if g['coil_center_upper_m'] - g['coil_center_lower_m'] <= g['turns_per_layer'] * g['wire_pitch_m']:
        raise ValueError('Pacotes axiais se sobrepõem ou centros invertidos.')
    for k in ('frequency_hz', 'capacitor_each_f', 'series_resistor_each_ohm', 'source_max_rms_v', 'current_limit_rms_a', 'series_resistor_rating_w', 'capacitor_rating_v'):
        positive(c[k], f'circuit.{k}')
    if len(c['drives']) != 2:
        raise ValueError('São necessárias duas portas de fonte independentes.')
    for d in c['drives']:
        positive(d['voltage_rms_v'], 'drive voltage', True)
        if d['voltage_rms_v'] > c['source_max_rms_v'] or not math.isfinite(d['phase_deg']) or d['orientation'] not in (-1, 1):
            raise ValueError('Fonte excede limite ou fase/orientação inválida.')
    for k in ('radius_m', 'turns', 'load_ohm', 'load_rating_w', 'axial_length_m', 'radial_depth_m'):
        positive(p[k], f'receiver.{k}')
    if p['turns'] != int(p['turns']) or p['orientation'] not in (-1, 1):
        raise ValueError('Receptor requer espiras inteiras e orientação ±1.')
    positive(p['leads_m'], 'receiver leads', True)
    if not g['coil_center_lower_m'] < p['center_z_m'] < g['coil_center_upper_m']:
        raise ValueError('Receptor deve estar entre as bobinas neste protótipo.')
    for k in ('major_radius_m', 'minor_radius_m', 'turns', 'drive_current_rms_a'):
        positive(t[k], f'toroidal.{k}', k == 'drive_current_rms_a')
    if t['turns'] != int(t['turns']) or t['major_radius_m'] <= t['minor_radius_m']:
        raise ValueError('Toroide requer espiras inteiras e R > r.')
    if abs(t['major_radius_m'] - p['radius_m']) <= t['minor_radius_m'] + p['radial_depth_m'] / 2:
        raise ValueError('Enrolamento toroidal intercepta receptor.')
    for k, v in n.items():
        if v != int(v) or v < 8:
            raise ValueError(f'numerics.{k} deve ser inteiro >= 8.')
    ctrl = config['control_cc']
    for k in ('target_a', 'kp_ohm', 'ki_ohm_per_s', 'duration_s', 'step_s'):
        positive(ctrl[k], f'control_cc.{k}')
    if ctrl['target_a'] > c['current_limit_rms_a'] or ctrl['step_s'] >= ctrl['duration_s']:
        raise ValueError('Alvo de controle fora da faixa ou passo inválido.')


def copper_resistivity(g):
    return g['copper_resistivity_20c_ohm_m'] * (1 + g['copper_temperature_coefficient_per_c'] * (g['temperature_c'] - 20))


def winding_loops(g, center):
    """50 filamentos individuais: 5 raios × 10 centros axiais, não N coincidentes."""
    return [(g['coil_mean_radius_m'] + (j - (g['radial_layers'] - 1)/2) * g['wire_pitch_m'],
             center + (k - (g['turns_per_layer'] - 1)/2) * g['wire_pitch_m'])
            for j in range(g['radial_layers']) for k in range(g['turns_per_layer'])]


def wheeler_h(radius, axial, radial, turns):
    """Wheeler multicamada: µH = 0.8 a²N²/(6a+9b+10c), dimensões em polegadas."""
    a, b, c = radius / INCH_M, axial / INCH_M, radial / INCH_M
    return 1e-6 * 0.8 * a*a * turns*turns / (6*a + 9*b + 10*c)


@lru_cache(maxsize=32)
def angular_values(samples):
    step = 2 * math.pi / samples
    return tuple((math.cos((k + .5)*step), math.sin((k + .5)*step)) for k in range(samples))


@lru_cache(maxsize=16384)
def mutual_loop_h(r1, r2, distance, samples=512):
    """Neumann exato em geometria, quadratura periódica de dois filamentos coaxiais."""
    if distance == 0 and r1 == r2:
        raise ValueError('Autoindutância de filamento singular; use Wheeler.')
    integral = sum(c / math.sqrt((r1-r2)**2 + 2*r1*r2*(1-c) + distance*distance)
                   for c, _ in angular_values(samples)) * 2*math.pi/samples
    return MU0 * r1*r2 * .5 * integral


def distributed_mutual_h(a, b, samples):
    return sum(mutual_loop_h(round(min(r1,r2), 12), round(max(r1,r2), 12), round(abs(z1-z2), 12), samples)
               for r1, z1 in a for r2, z2 in b)


def positive_definite(matrix):
    """Cholesky numérico também rejeita estimativa de indutância não física."""
    n = len(matrix)
    lower = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1):
            residual = matrix[i][j] - sum(lower[i][k]*lower[j][k] for k in range(j))
            if i == j:
                if residual <= 0:
                    return False
                lower[i][j] = math.sqrt(residual)
            else:
                lower[i][j] = residual/lower[j][j]
    return True


def parameters(config):
    validate_config(config)
    g, c, p = (config[k] for k in ('geometry', 'circuit', 'receiver'))
    n = int(g['radial_layers']*g['turns_per_layer'])
    axial, radial = g['turns_per_layer']*g['wire_pitch_m'], g['radial_layers']*g['wire_pitch_m']
    self_l = wheeler_h(g['coil_mean_radius_m'], axial, radial, n)
    packs = [winding_loops(g, g[f'coil_center_{where}_m']) for where in ('lower','upper')]
    samples = config['numerics']['mutual_angular_samples']
    mutual = distributed_mutual_h(packs[0], packs[1], samples)
    receiver_l = wheeler_h(p['radius_m'], p['axial_length_m'], p['radial_depth_m'], p['turns'])
    m_receiver = [sum(mutual_loop_h(round(min(r,p['radius_m']),12), round(max(r,p['radius_m']),12), round(abs(z-p['center_z_m']),12), samples) for r,z in pack)*p['turns'] for pack in packs]
    area = math.pi*(g['wire_bare_diameter_m']/2)**2
    resistivity = copper_resistivity(g)
    lengths = [sum(2*math.pi*r for r,_ in pack)+g['coil_leads_each_m'] for pack in packs]
    r_cu = [resistivity*length/area for length in lengths]
    receiver_length = p['turns']*2*math.pi*p['radius_m']+p['leads_m']
    receiver_r = resistivity*receiver_length/area
    orientations = [d['orientation'] for d in c['drives']] + ([p['orientation']] if p['enabled'] else [])
    physical_l = [[self_l, mutual],[mutual,self_l]]
    if p['enabled']:
        physical_l = [[self_l,mutual,m_receiver[0]], [mutual,self_l,m_receiver[1]], [m_receiver[0],m_receiver[1],receiver_l]]
    matrix = [[physical_l[i][j]*orientations[i]*orientations[j] for j in range(len(orientations))] for i in range(len(orientations))]
    if not positive_definite(matrix):
        raise ValueError('Matriz de indutância não positiva: aproximação/geometria incompatível.')
    return {
        'turns_each':n, 'self_inductance_each_h':self_l, 'mutual_inductance_h':mutual,
        'receiver_inductance_h':receiver_l, 'mutual_to_receiver_h':m_receiver,
        'coupling_coefficient':mutual/self_l, 'inductance_matrix_h':matrix,
        'inductance_matrix_physical_h':physical_l, 'matrix_positive_definite':True,
        'orientations':orientations, 'copper_resistance_each_ohm':r_cu,
        'receiver_copper_resistance_ohm':receiver_r,
        'wire_length_each_m':lengths, 'receiver_wire_length_m':receiver_length,
        'winding_axial_length_m':axial, 'winding_radial_depth_m':radial,
        'resistance_each_ohm':[r+c['series_resistor_each_ohm'] for r in r_cu],
        'resonance_symmetric_unloaded_hz':1/(2*math.pi*math.sqrt((self_l+mutual)*c['capacitor_each_f'])),
        'resonance_antisymmetric_unloaded_hz':1/(2*math.pi*math.sqrt((self_l-mutual)*c['capacitor_each_f'])),
        'quality_symmetric_unloaded':math.sqrt((self_l+mutual)/c['capacitor_each_f'])/(r_cu[0]+c['series_resistor_each_ohm']),
        'skin_depth_m':math.sqrt(2*resistivity/(2*math.pi*c['frequency_hz']*MU0)),
        'self_inductance_method':'Wheeler multilayer estimate; measure before matching resonances',
        'mutual_method':'Neumann distributed 50 loops per drive, receiver 20 coincident mean-radius loops'
    }


def solve_complex(matrix, rhs):
    """Éliminação de Gauss com pivotamento parcial, 2 ou 3 portas."""
    a = [list(map(complex,row))+[complex(b)] for row,b in zip(matrix,rhs)]
    n = len(rhs)
    for j in range(n):
        pivot = max(range(j,n),key=lambda i:abs(a[i][j]))
        a[j],a[pivot] = a[pivot],a[j]
        if abs(a[j][j]) < 1e-18:
            raise ValueError('Sistema elétrico singular.')
        diagonal = a[j][j]
        a[j] = [x/diagonal for x in a[j]]
        for i in range(n):
            if i != j:
                multiple = a[i][j]
                a[i] = [x-multiple*y for x,y in zip(a[i],a[j])]
    return [a[i][-1] for i in range(n)]


def phasor(value):
    return {'re':value.real, 'im':value.imag, 'rms':abs(value), 'phase_deg':math.degrees(cmath.phase(value))}


def circuit_solution(config, params=None):
    p = params if params is not None else parameters(config)
    c, rx = config['circuit'],config['receiver']
    omega = 2*math.pi*c['frequency_hz']
    matrix = [[1j*omega*value for value in row] for row in p['inductance_matrix_h']]
    voltages = [d['voltage_rms_v']*cmath.exp(1j*math.radians(d['phase_deg'])) for d in c['drives']]
    for i in range(2):
        matrix[i][i] += p['resistance_each_ohm'][i] - 1j/(omega*c['capacitor_each_f'])
    if rx['enabled']:
        matrix[2][2] += p['receiver_copper_resistance_ohm']+rx['load_ohm']
        voltages.append(0j)
    currents = solve_complex(matrix, voltages)
    physical_currents = [i*s for i,s in zip(currents,p['orientations'])]
    source_p = [(v*i.conjugate()).real for v,i in zip(voltages[:2],currents[:2])]
    source_q = [(v*i.conjugate()).imag for v,i in zip(voltages[:2],currents[:2])]
    winding_p = [abs(currents[i])**2*p['copper_resistance_each_ohm'][i] for i in range(2)]
    series_p = [abs(currents[i])**2*c['series_resistor_each_ohm'] for i in range(2)]
    rx_cu = abs(currents[2])**2*p['receiver_copper_resistance_ohm'] if rx['enabled'] else 0.0
    rx_load = abs(currents[2])**2*rx['load_ohm'] if rx['enabled'] else 0.0
    losses = sum(winding_p)+sum(series_p)+rx_cu+rx_load
    magnetic_j = .5*sum((currents[i].conjugate()*p['inductance_matrix_h'][i][j]*currents[j]).real for i in range(len(currents)) for j in range(len(currents)))
    caps = [currents[i]/(1j*omega*c['capacitor_each_f']) for i in range(2)]
    warnings = []
    if max(abs(i) for i in currents[:2]) > c['current_limit_rms_a']:
        warnings.append('CURRENT_LIMIT_EXCEEDED: sinusoidal linear prediction invalid for a clipping source; no artificial clipping applied')
    if any(power>c['series_resistor_rating_w'] for power in series_p):
        warnings.append('SERIES_RESISTOR_POWER_EXCEEDED')
    if any(math.sqrt(2)*abs(v)>c['capacitor_rating_v'] for v in caps):
        warnings.append('CAPACITOR_PEAK_VOLTAGE_EXCEEDED')
    if rx_load > rx['load_rating_w']:
        warnings.append('RECEIVER_LOAD_POWER_EXCEEDED')
    if any(power < -1e-10 for power in source_p):
        warnings.append('SOURCE_ABSORBS_REAL_POWER: independent drive must accept bidirectional energy or operating point cannot be realized')
    return {
        'frequency_hz':c['frequency_hz'], 'source_voltages':[phasor(v) for v in voltages[:2]],
        'currents':[phasor(i) for i in currents], 'physical_currents':[phasor(i) for i in physical_currents],
        'capacitor_voltages':[phasor(v) for v in caps],
        'receiver_load_voltage':phasor(currents[2]*rx['load_ohm']) if rx['enabled'] else phasor(0j),
        'power':{'source_each_w':source_p,'source_reactive_each_var':source_q,'source_total_w':sum(source_p),
                 'copper_each_w':winding_p,'series_resistor_each_w':series_p,'receiver_copper_w':rx_cu,
                 'receiver_load_w':rx_load,'dissipation_total_w':losses,'balance_residual_w':sum(source_p)-losses,
                 'transfer_efficiency':rx_load/sum(source_p) if sum(source_p)>0 else 0},
        'energy':{'mean_magnetic_j':magnetic_j,'mean_capacitive_each_j':[.5*c['capacitor_each_f']*abs(v)**2 for v in caps]},
        'validity':{'linear_region':not warnings,'warnings':warnings,'source_port_requirement':'two independently phase-controlled isolated sine outputs; specified RMS amplitude under actual load; 50-ohm function-generator amplitude labels are insufficient'}
    }


def loop_axis_b_per_a(radius, dz):
    return MU0*radius*radius/(2*(radius*radius+dz*dz)**1.5)


def loop_field_per_a(radius, center_z, point, samples=128, exclusion_radius=0.0005):
    x,y,z = point
    dz = z-center_z
    if math.hypot(math.hypot(x,y)-radius,dz) <= exclusion_radius:
        raise ValueError('FIELD_IN_WIRE_EXCLUDED: filamento não modela campo no cobre.')
    if x*x+y*y < 1e-28:
        return (0.0,0.0,loop_axis_b_per_a(radius,dz))
    step = 2*math.pi/samples
    bx=by=bz=0.0
    for cosine,sine in angular_values(samples):
        dx,dy = x-radius*cosine,y-radius*sine
        r3 = (dx*dx+dy*dy+dz*dz)**1.5
        weight = MU0/(4*math.pi)*radius*step/r3
        bx += cosine*dz*weight
        by += sine*dz*weight
        bz += (radius-x*cosine-y*sine)*weight
    return bx,by,bz


def basis_fields(config, point, samples=None):
    g,p = config['geometry'],config['receiver']
    samples = samples or config['numerics']['field_angular_samples']
    fields = []
    for key in ('coil_center_lower_m','coil_center_upper_m'):
        out = [0.0]*3
        for r,z in winding_loops(g,g[key]):
            part = loop_field_per_a(r,z,point,samples,g['wire_bare_diameter_m']/2)
            for k in range(3): out[k] += part[k]
        fields.append(out)
    if p['enabled']:
        # Exclude actual receiver envelope around its effective coincident loops.
        if abs(math.hypot(point[0],point[1])-p['radius_m']) <= p['radial_depth_m']/2 and abs(point[2]-p['center_z_m']) <= p['axial_length_m']/2:
            raise ValueError('FIELD_IN_RECEIVER_ENVELOPE_EXCLUDED')
        fields.append([value*p['turns'] for value in loop_field_per_a(p['radius_m'],p['center_z_m'],point,samples,g['wire_bare_diameter_m']/2)])
    return fields


def toroidal_field_per_a(config, point, samples=None):
    """48 boucles poloidais reais no espaço; soma vetorial, não desenho decorativo."""
    t,g = config['toroidal'],config['geometry']
    samples = samples or config['numerics']['toroid_angular_samples']
    major,minor = t['major_radius_m'],t['minor_radius_m']
    bx=by=bz=0.0
    step = 2*math.pi/samples
    for turn in range(t['turns']):
        phi = 2*math.pi*turn/t['turns']
        cp,sp = math.cos(phi),math.sin(phi)
        local_radial = point[0]*cp+point[1]*sp
        local_normal = -point[0]*sp+point[1]*cp
        d_to_circle = math.sqrt((math.hypot(local_radial-major,point[2]-t['center_z_m'])-minor)**2+local_normal**2)
        if d_to_circle <= g['wire_bare_diameter_m']/2:
            raise ValueError('FIELD_IN_TOROID_WIRE_EXCLUDED')
        for ct,st in angular_values(samples):
            location = ((major+minor*ct)*cp,(major+minor*ct)*sp,t['center_z_m']-minor*st)
            dl = (-minor*st*cp*step,-minor*st*sp*step,-minor*ct*step)
            dx,dy,dz = (point[k]-location[k] for k in range(3))
            r3 = (dx*dx+dy*dy+dz*dz)**1.5
            factor = MU0/(4*math.pi)/r3
            bx += (dl[1]*dz-dl[2]*dy)*factor
            by += (dl[2]*dx-dl[0]*dz)*factor
            bz += (dl[0]*dy-dl[1]*dx)*factor
    return [bx,by,bz]


def complex_field_summary(field):
    # B(t) = sqrt(2) Re[Btilde exp(jwt)]. The phasor vector can describe an ellipse.
    norm2 = sum(abs(b)**2 for b in field)
    q = sum(b*b for b in field)
    major = math.sqrt(max(0.0,norm2+abs(q)))
    minor = math.sqrt(max(0.0,norm2-abs(q)))
    return {'components_t':[phasor(b) for b in field], 'magnitude_rms_t':math.sqrt(norm2),
            'ellipse_major_peak_t':major,'ellipse_minor_peak_t':minor,
            'mean_magnetic_energy_density_j_m3':norm2/(2*MU0)}


def field_solution(config, solution, point, samples=None):
    fields = basis_fields(config,point,samples)
    currents = [complex(i['re'],i['im']) for i in solution['physical_currents']]
    out = [sum(fields[i][k]*currents[i] for i in range(len(currents))) for k in range(3)]
    if config['toroidal']['enabled']:
        basis = toroidal_field_per_a(config,point)
        current = config['toroidal']['drive_current_rms_a']*cmath.exp(1j*math.radians(config['toroidal']['phase_deg']))
        for k in range(3): out[k] += basis[k]*current
    return complex_field_summary(out)


def toroidal_summary(config):
    t,g = config['toroidal'],config['geometry']
    radius,minor,n = t['major_radius_m'],t['minor_radius_m'],t['turns']
    length = n*2*math.pi*minor+t['leads_m']
    resistance = copper_resistivity(g)*length/(math.pi*(g['wire_bare_diameter_m']/2)**2)
    inductance = MU0*n*n*minor*minor/(2*radius)
    current = t['drive_current_rms_a'] if t['enabled'] else 0.0
    omega=2*math.pi*config['circuit']['frequency_hz']
    return {'enabled':t['enabled'],'turns':n,'wire_length_m':length,'copper_resistance_dc_ohm':resistance,
            'self_inductance_ideal_h':inductance,'ideal_bulk_field_rms_t':MU0*n*current/(2*math.pi*radius),
            'drive_current_rms_a':current,'required_voltage_estimate_rms_v':current*math.hypot(resistance,omega*inductance),
            'copper_loss_w':resistance*current**2,
            'qualification':'Independent ideal current-driven air-core toroid. L and voltage estimates use ideal bulk approximation, whereas field uses actual poloidal loop geometry. Leakage, parasitic capacitance, winding leads and toroid-to-drive mutual are not included in this circuit; optional toroid results are separate from axial transfer power balance.'}


def control_cc(config, params=None):
    """Ensaio separado de controle CC, capacitores desviados. Não recorta fasores CA."""
    p = params if params else parameters(config)
    ctrl,c = config['control_cc'],config['circuit']
    # Both axially aiding currents equal. Receiver transient not included, explicitly.
    inductance=p['self_inductance_each_h']+p['mutual_inductance_h']
    resistance=p['resistance_each_ohm'][0]
    target=ctrl['target_a']
    voltage_limit=c['source_max_rms_v']
    dt=ctrl['step_s']
    if dt > inductance/(20*resistance):
        raise ValueError('Passo de controle CC maior que tau/20.')
    current=integral=0.0
    rows=[]
    count=int(ctrl['duration_s']/dt)
    stride=max(1,count//1000)
    max_current=0.0
    for step in range(count+1):
        time=step*dt
        disturbance=1.0 if time >= ctrl['duration_s']*.5 else 0.0
        error=target-current
        unsaturated=resistance*target+ctrl['kp_ohm']*error+integral
        voltage=min(voltage_limit,max(0.0,unsaturated))
        # Conditional integrator anti-windup.
        if voltage == unsaturated or (unsaturated > voltage_limit and error < 0) or (unsaturated < 0 and error > 0):
            integral += ctrl['ki_ohm_per_s']*error*dt
        if step%stride==0: rows.append([time,current,voltage,disturbance,target])
        if step == count:
            break
        current += dt*(voltage-(resistance+disturbance)*current)/inductance
        max_current=max(max_current,current)
    return {'mode':'Separate DC RL bench with capacitors bypassed, receiver disconnected, two equal axially aiding ports; not an AC amplitude controller',
            'effective_inductance_per_port_h':inductance,'target_a':target,'final_current_a':current,
            'max_current_a':max_current,'absolute_final_error_a':abs(target-current),'voltage_limit_v':voltage_limit,
            'disturbance_ohm':1.0,'step_s':dt,'stable_linear_no_clipping':max_current<c['current_limit_rms_a'],
            'controller_saturation_is_voltage_only':True,'rows':rows}


def summary(config):
    p=parameters(config)
    circuit=circuit_solution(config,p)
    center=[0.0,0.0,(config['geometry']['coil_center_lower_m']+config['geometry']['coil_center_upper_m'])/2]
    field=field_solution(config,circuit,center)
    u=field['mean_magnetic_energy_density_j_m3']
    scale=8*math.pi*G/C_LIGHT**4*u
    ctl=control_cc(config,p)
    ctl.pop('rows')
    return {'schema_version':'2.0','units':'SI; phasor voltages/currents/fields are RMS; z measured from base plane',
            'config':config,'parameters':p,'circuit':circuit,'center_point_m':center,'center_field':field,
            'toroidal':toroidal_summary(config),'control_cc':ctl,
            'energy_curvature_scale':{'local_mean_magnetic_energy_density_j_m3':u,'einstein_tensor_magnetic_order_m_inv2':scale,
                 'meaning':'Local order of Einstein tensor sourced by mean classical magnetic energy only. Not Ricci scalar, not a computed spacetime metric. Maxwell stress-energy is traceless: R=0 in electrovacuum with Lambda=0. Electric energy and other stresses are not included in this local scale.'},
            'status':'CLASSICAL_NUMERICAL_PREDICTION_NOT_EXPERIMENTAL_CONFIRMATION',
            'missing_physics':['No vacuum energy extraction law','No wormhole mechanism','No reactionless thrust','No quantum coherence or quantum-state evolution','No practical controllable spacetime curvature']}


def write_csv(path, header, rows):
    with Path(path).open('w',encoding='utf-8',newline='') as stream:
        writer=csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


def sync_browser_reference(result):
    """Regenera a referência incorporada, sem reescrever o algoritmo JavaScript."""
    path=Path(__file__).with_name('modelo_browser.js')
    if not path.exists():
        return
    script=path.read_text(encoding='utf-8')
    start=script.index('  const BASE = ')
    end=script.index('\n  const MU0',start)
    payload=json.dumps(result,ensure_ascii=False,separators=(',',':'))
    script=script[:start]+'  const BASE = '+payload+';'+script[end:]
    path.write_text(script,encoding='utf-8')


def export_all(config, output):
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    result=summary(config)
    sync_browser_reference(result)
    (output/'baseline.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    p=result['parameters']
    c=result['circuit']
    g=config['geometry']
    center=result['center_point_m'][2]
    axis=[]
    for k in range(config['numerics']['axis_points']):
        z=0.0+0.25*k/(config['numerics']['axis_points']-1)
        f=field_solution(config,c,(0.0,0.0,z))
        b=f['components_t'][2]
        axis.append([z,b['re'],b['im'],f['magnitude_rms_t']])
    write_csv(output/'campo_eixo.csv',['z_m','Bz_real_rms_T','Bz_imag_rms_T','B_rms_T'],axis)
    point_count=config['numerics']['slice_points_per_dimension']
    slice_rows=[]
    basis_grid=[]
    for iz in range(point_count):
        z=.25*iz/(point_count-1)
        for ix in range(point_count):
            x=-.175+.35*ix/(point_count-1)
            try:
                basis=basis_fields(config,(x,0.0,z))
                f=field_solution(config,c,(x,0.0,z))
                vectors=f['components_t']
                slice_rows.append([x,z]+[v[s] for v in vectors for s in ('re','im')]+[f['magnitude_rms_t'],'ok'])
                basis_grid.append({'x_m':x,'z_m':z,'basis_t_per_a':basis})
            except ValueError as exc:
                slice_rows.append([x,z]+['']*7+[str(exc)])
                basis_grid.append({'x_m':x,'z_m':z,'basis_t_per_a':None,'excluded':str(exc)})
    write_csv(output/'campo_plano_xz.csv',['x_m','z_m','Bx_real_T','Bx_imag_T','By_real_T','By_imag_T','Bz_real_T','Bz_imag_T','B_rms_T','status'],slice_rows)
    (output/'field_basis.json').write_text(json.dumps({'schema_version':'2.0','grid_size':point_count,'meaning':'RMS phasor field = sum(unit DC vector per ampere × physical RMS current phasor). Fixed baseline geometry. Toroidal field not in this grid.','points':basis_grid},ensure_ascii=False),encoding='utf-8')
    sweep=[]
    for k in range(config['numerics']['sweep_points']):
        frequency=100+(6000-100)*k/(config['numerics']['sweep_points']-1)
        conf=copy.deepcopy(config)
        conf['circuit']['frequency_hz']=frequency
        sol=circuit_solution(conf,p)
        bf=field_solution(conf,sol,(0.0,0.0,center))
        sweep.append([frequency]+[i['rms'] for i in sol['currents']]+[sol['power']['source_total_w'],sol['power']['receiver_load_w'],bf['magnitude_rms_t']])
    current_headers=['I_lower_A','I_upper_A']+(['I_receiver_A'] if config['receiver']['enabled'] else [])
    write_csv(output/'varredura_frequencia.csv',['frequency_Hz']+current_headers+['P_sources_W','P_receiver_load_W','B_center_rms_T'],sweep)
    ctl=control_cc(config,p)
    write_csv(output/'controle_cc.csv',['time_s','current_A','voltage_V','added_resistance_ohm','target_A'],ctl['rows'])
    cases=[]
    for phase,orientation,rx_enabled in [(0,1,True),(90,1,True),(180,1,True),(0,-1,True),(0,1,False)]:
        conf=copy.deepcopy(config)
        conf['circuit']['drives'][1]['phase_deg']=phase
        conf['circuit']['drives'][1]['orientation']=orientation
        conf['receiver']['enabled']=rx_enabled
        pr=parameters(conf)
        sol=circuit_solution(conf,pr)
        cases.append({'upper_phase_deg':phase,'upper_orientation':orientation,'receiver_enabled':rx_enabled,
                      'parameters':pr,'circuit':sol,'center_field':field_solution(conf,sol,(0.0,0.0,center))})
    (output/'testvectors.json').write_text(json.dumps({'schema_version':'2.0','cases':cases},ensure_ascii=False,indent=2),encoding='utf-8')
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--config',default=None)
    parser.add_argument('--output',default='outputs')
    args=parser.parse_args()
    result=export_all(load_config(args.config),args.output)
    print(json.dumps({'I_each_rms_A':[i['rms'] for i in result['circuit']['currents']],
                      'B_center_rms_uT':result['center_field']['magnitude_rms_t']*1e6,
                      'P_sources_W':result['circuit']['power']['source_total_w'],
                      'P_receiver_W':result['circuit']['power']['receiver_load_w'],
                      'balance_W':result['circuit']['power']['balance_residual_w'],
                      'symmetric_resonance_Hz':result['parameters']['resonance_symmetric_unloaded_hz'],
                      'output':str(Path(args.output).resolve())},indent=2))
