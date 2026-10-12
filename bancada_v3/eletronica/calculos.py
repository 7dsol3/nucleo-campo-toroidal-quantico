"""Dimensionamento analitico V3; nao substitui ensaio de hardware. Stdlib only."""
from __future__ import annotations
import argparse
import copy
import csv
import json
import math
from itertools import product
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'nucleo_integral_v2' / 'simulacao'))
from modelo_integral import load_config, parameters, solve_complex, circuit_solution, positive_definite


def calculation():
    cfg = load_config()
    p = parameters(cfg)
    root2 = math.sqrt(2)
    # Hardware qualifications, not guaranteed specifications at an untested limit.
    rails_min, rails_max = 11.88, 12.12
    current_rms_limit, qualified_current_peak_max = .5, 1.0
    bleed_r, bleed_tol = 4.7, .01
    bleed_min = rails_min / (bleed_r * (1 + bleed_tol))
    bleed_max = rails_max / (bleed_r * (1 - bleed_tol))
    rail_draw_max = bleed_max + 2 * qualified_current_peak_max + .08
    baseline = circuit_solution(cfg, p)
    envelope = []
    worst = {k: {'value': 0, 'case': None} for k in
             ('current_bound_rms_a', 'capacitor_peak_v', 'resistor_w', 'amplifier_dissipation_w', 'energy_residual_w')}
    def record(key, value, case):
        if value > worst[key]['value']:
            worst[key] = {'value': value, 'case': case}
    # Sweep includes analytic l1 row bounds over ALL relative phases/amplitudes
    # <=5 Vrms, plus explicit sampled port power cases. Tolerances are assumptions.
    corners = list(product((.85,1.15), (.85,1.15), (.85,1.15), (.9,1.1), (.9,1.1), (20,60)))
    corners.append((1,1,1,1,1,20))
    for inductance_factor, inductance_factor_2, mutual_factor, cap_factor, cap_factor_2, temp_c in corners:
        resistance_factor = 1 + .00393 * (temp_c - 20)
        inductance = copy.deepcopy(p['inductance_matrix_h'])
        inductance[0][0] *= inductance_factor
        inductance[1][1] *= inductance_factor_2
        for i in range(3):
            for j in range(3):
                if i != j:
                    inductance[i][j] *= mutual_factor
        if not positive_definite(inductance):
            raise ValueError('Tolerance corner has non-physical inductance matrix')
        resistances = [9.9 + p['copper_resistance_each_ohm'][i] * resistance_factor for i in range(2)]
        rx_r = 99 + p['receiver_copper_resistance_ohm'] * resistance_factor
        for f in range(100, 5001, 25):
            w = 2 * math.pi * f
            caps = [cfg['circuit']['capacitor_each_f'] * x for x in (cap_factor,cap_factor_2)]
            z = [[1j * w * x for x in row] for row in inductance]
            for i in range(2):
                z[i][i] += resistances[i] - 1j / (w * caps[i])
            z[2][2] += rx_r
            responses = [solve_complex(z, [1 if i == j else 0 for i in range(3)]) for j in range(2)]
            bounds = [5 * sum(abs(responses[j][i]) for j in range(2)) for i in range(2)]
            case = {'frequency_hz': f, 'L1_factor': inductance_factor, 'L2_factor':inductance_factor_2,
                    'mutual_factor': mutual_factor, 'C1_factor': cap_factor, 'C2_factor':cap_factor_2, 'temperature_c': temp_c}
            ibound = max(bounds)
            record('current_bound_rms_a', ibound, case)
            capacitor_peak = max(root2*bounds[i]/(w*caps[i]) for i in range(2))
            record('capacitor_peak_v', capacitor_peak, case)
            record('resistor_w', ibound * ibound * 10.1, case)
            for phase in (0, 90, 180, 270):
                vs = [5+0j, 5*complex(math.cos(math.radians(phase)), math.sin(math.radians(phase))), 0j]
                current = solve_complex(z, vs)
                power = [(vs[i] * current[i].conjugate()).real for i in range(2)]
                total_losses = sum(abs(current[i])**2 * resistances[i] for i in range(2)) + abs(current[2])**2 * rx_r
                record('energy_residual_w', abs(sum(power) - total_losses), case | {'phase_deg': phase})
                for i in range(2):
                    pd = 2 * rails_max * root2 * abs(current[i]) / math.pi - power[i] + 2 * rails_max * .02
                    record('amplifier_dissipation_w', pd, case | {'phase_deg': phase, 'port': i+1})
            if inductance_factor == inductance_factor_2 == mutual_factor == cap_factor == cap_factor_2 == 1 and temp_c == 20 and f in (100, 500, 1000, 1400, 1500, 2000, 3000, 5000):
                envelope.append({'frequency_hz': f, 'max_source_rms_v': 5, 'all_phases_current_bound_rms_a': ibound,
                                 'capacitor_peak_bound_v': capacitor_peak,
                                 'series_resistor_bound_w': ibound**2 * 10.1})
    # Independent passivity bound: R*||i||² <= |v|*||i||, L/C exchange no average energy.
    # This is a loose global bound; row sums above are tighter frequency dependent.
    pi_r = p['resistance_each_ohm'][0]
    theta_jc_conservative, theta_interface, theta_sink = 2.5, .5, 3.0
    # Stronger universal amplifier bound including negative real port power.
    amplifier_universal_w = 2 * rails_max * root2 * current_rms_limit / math.pi + 5 * current_rms_limit + 2*rails_max*.02
    tj_bound = 30 + amplifier_universal_w * (theta_jc_conservative + theta_interface + theta_sink)
    recommended_common_voltage = 4.7
    checks = {
        'recommended_4_7Vrms_all_phase_swept_current_within_0_5Arms': worst['current_bound_rms_a']['value'] * recommended_common_voltage/5 <= current_rms_limit,
        'bleeder_absorbs_two_qualified_1A_peak_returns': bleed_min >= 2 * qualified_current_peak_max,
        'rail_peak_current_below_4_8A_setting': rail_draw_max < 4.8,
        'rail_power_below_HMP_80W_per_channel': rails_max * rail_draw_max < 80,
        'two_rails_below_HMP_188W_total': 2*rails_max*rail_draw_max < 188,
        'output_peak_with_4_1V_headroom': 5*root2 < rails_min - 4.1,
        'capacitor_swept_bound_below_30V_peak_stop_level': worst['capacitor_peak_v']['value'] < 30,
        'resistor_below_10W_nominal_project_limit': worst['resistor_w']['value'] < 10,
        'junction_bound_below_100C': tj_bound < 100,
        'energy_balance_residual_below_1nW': worst['energy_residual_w']['value'] < 1e-9,
        'slew_requirement_below_one_tenth_typical_10V_per_us': 2*math.pi*5000*5*root2/1e6 < 1,
        'PI_max_2_5V_implies_current_below_0_25A': 2.5/(9.9 + p['copper_resistance_each_ohm'][0]) < .25,
    }
    return {
        'status': 'ANALYTICAL_DESIGN_ONLY_NOT_HARDWARE_CERTIFIED',
        'recommended_common_voltage_rms_v': recommended_common_voltage,
        'maximum_5Vrms_is_conditional': True,
        'all_phase_5Vrms_sweep_exceeds_0_5Arms': worst['current_bound_rms_a']['value'] > current_rms_limit,
        'all_analytical_checks_pass': all(checks.values()), 'checks': checks,
        'baseline': baseline, 'parameters_V2': p, 'nominal_envelope': envelope,
        'sweep_worst': worst, 'sweep_cases': len(corners)*197,
        'limitations': ['Frequency grid 25Hz is not a continuous-frequency proof; measured sweep is required.',
                       'Independent main L1/L2 +/-15%, common offdiagonal mutual factor +/-15%, independent C1/C2 +/-10%; receiver self-L fixed; Rseries/load -1%, copper20..60C. Corner study, not interval proof.',
                       'OPA548 peak limiter must be measured 0.72..1.0A in both directions, cold and warm before use.',
                       'Source waveform, stability, safe operating area, heatsink performance and turn-off transient require bench qualification.'],
        'supply': {'model': 'R&S HMP2030', 'rail_setting_v': 12, 'rail_min_v': rails_min, 'rail_max_v': rails_max,
                   'current_setting_a': 4.8, 'bleed_each_ohm': bleed_r, 'bleed_tolerance': bleed_tol,
                   'bleed_min_a': bleed_min, 'bleed_max_a': bleed_max,
                   'bleed_power_each_max_w': rails_max**2/(bleed_r*(1-bleed_tol)),
                   'qualified_driver_current_peak_max_a': qualified_current_peak_max, 'rail_draw_bound_peak_a': rail_draw_max},
        'driver': {'model': 'OPA548EVM', 'Rcl_ohm': 82000, 'nominal_limiter_peak_a': 15000*4.75/(13750+82000),
                   'signal_path': 'default noninverting: input divider1/2, feedback gain2; total approximately1; calibrate',
                   'universal_dissipation_bound_each_w': amplifier_universal_w, 'junction_bound_c': tj_bound,
                   'thermal_assumptions': {'ambient_max_c':30, 'theta_jc_conservative_c_per_w':2.5,
                                           'theta_interface_c_per_w':.5, 'theta_sink_max_c_per_w':3}},
        'PI_DC': {'target_a': .15, 'maximum_target_a': .2, 'maximum_DAC_v':2.5, 'Rnom_ohm':pi_r,
                  'expected_drive_v_at_target': .15*pi_r, 'ADC_divider_ratio':.5, 'ADC_expected_v':.15*10*.5,
                  'ADC_RC_tau_s':5000*1e-8, 'max_current_resolution_ideal_a':3.3/4096/(10*.5)},
        'auxiliary_toroid': {'supply_v':3.3, 'series_ohm':22, 'worst_nominal_current_a':3.3/22,
                             'worst_series_power_w':3.3**2/22, 'rating_w':5, 'mode':'separate DC only; AC needs third qualified driver'},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE/'relatorio_dimensionamento.json')
    args = parser.parse_args()
    result = calculation()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    with args.output.with_name('envelope_operacao.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(result['nominal_envelope'][0]))
        writer.writeheader(); writer.writerows(result['nominal_envelope'])
    print(json.dumps({'checks':result['checks'], 'worst':result['sweep_worst'], 'output':str(args.output)}, ensure_ascii=True))
    raise SystemExit(0 if result['all_analytical_checks_pass'] else 1)

if __name__ == '__main__':
    main()
