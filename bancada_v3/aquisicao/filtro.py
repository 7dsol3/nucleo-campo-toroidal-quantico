"""Cálculo do filtro analógico proposto; não é medição nem certificação.

Somente stdlib. Valores típicos do OPA4277 não são limites garantidos.
Saída JSON tem origin=CALCULATED e nenhum resultado experimental.
"""
from __future__ import annotations

import argparse
import cmath
import itertools
import json
import math
from pathlib import Path

R_OHM = 3160.0
C_F = 1e-9
STAGES = 4
R_TOL = C_TOL = .01
GBW_TYP_HZ = 1e6
SR_TYP_V_PER_US = .8
OUTPUT_R_OHM = 47.0
ADC_R_OHM = 1e6
# Hipótese de cálculo, a medir para o cabo/conector/ADC realmente instalados.
CABLE_AND_ADC_C_ASSUMED_F = 100e-12
FC_HZ = 1 / (2 * math.pi * R_OHM * C_F)


def rc_transfer(frequency_hz, resistors=None, capacitors=None):
    if not math.isfinite(frequency_hz) or frequency_hz < 0:
        raise ValueError("Frequência precisa ser finita e não negativa")
    resistors = [R_OHM] * STAGES if resistors is None else resistors
    capacitors = [C_F] * STAGES if capacitors is None else capacitors
    if len(resistors) != STAGES or len(capacitors) != STAGES:
        raise ValueError("São necessários quatro R e quatro C")
    response = 1 + 0j
    for r, c in zip(resistors, capacitors):
        if not math.isfinite(r) or not math.isfinite(c) or r <= 0 or c <= 0:
            raise ValueError("R e C precisam ser positivos e finitos")
        response /= 1 + 2j * math.pi * frequency_hz * r * c
    return response


def first_stage_admittance(frequency_hz, r=R_OHM, c=C_F):
    """Admitância vista pelo nó medido; ignora corrente de bias e parasitas."""
    if frequency_hz == 0:
        return 0j
    return 1 / (r + 1 / (2j * math.pi * frequency_hz * c))


def response(frequency_hz):
    ideal = rc_transfer(frequency_hz)
    buffer = (1 + 1j * frequency_hz / GBW_TYP_HZ) ** -STAGES
    adc = 1 / (1 + OUTPUT_R_OHM * (1 / ADC_R_OHM + 2j * math.pi * frequency_hz * CABLE_AND_ADC_C_ASSUMED_F))
    combined = ideal * buffer * adc
    phase_ideal = -STAGES * math.degrees(math.atan(frequency_hz / FC_HZ))
    phase_combined = phase_ideal - STAGES * math.degrees(math.atan(frequency_hz / GBW_TYP_HZ)) + math.degrees(cmath.phase(adc))
    return {"frequency_hz": frequency_hz, "ideal_rc_gain": abs(ideal), "ideal_rc_attenuation_db": -20 * math.log10(abs(ideal)),
            "ideal_rc_phase_unwrapped_deg": phase_ideal, "typical_buffer_approximation_gain": abs(buffer),
            "combined_typical_approximation_gain": abs(combined), "combined_typical_phase_unwrapped_deg": phase_combined,
            "combined_re": combined.real, "combined_im": combined.imag}


def tolerance_corners(frequency_hz):
    # 2^8 =256 combinações independentes de quatro R e quatro C por canal.
    corners = []
    for signs in itertools.product((-1, 1), repeat=8):
        r = [R_OHM * (1 + s * R_TOL) for s in signs[:4]]
        c = [C_F * (1 + s * C_TOL) for s in signs[4:]]
        h = rc_transfer(frequency_hz, r, c)
        phase = -sum(math.degrees(math.atan(2 * math.pi * frequency_hz * ri * ci)) for ri, ci in zip(r, c))
        corners.append((abs(h), phase))
    gain_min, gain_max = min(x[0] for x in corners), max(x[0] for x in corners)
    phase_min, phase_max = min(x[1] for x in corners), max(x[1] for x in corners)
    return {"frequency_hz": frequency_hz, "corners_evaluated": len(corners), "rc_gain_min": gain_min, "rc_gain_max": gain_max,
            "rc_phase_min_deg": phase_min, "rc_phase_max_deg": phase_max,
            "pair_max_gain_ratio_minus_one": gain_max / gain_min - 1,
            "pair_max_phase_difference_deg": phase_max - phase_min,
            "not_included": "GBW/SR spread, amplifier offsets/noise, temperature, aging, source/load impedance, cables and parasitics"}


def burden(frequency_hz, voltage_rms_v=5.0):
    y = first_stage_admittance(frequency_hz)
    # Relação Vcarregado/Vsemfiltro para Thévenin resistivo no nó medido.
    ratio10 = 1 / (1 + 10 * y)
    ratio100 = 1 / (1 + 100 * y)
    return {"frequency_hz": frequency_hz, "input_admittance_real_s": y.real, "input_admittance_imag_s": y.imag,
            "input_impedance_magnitude_ohm": 1 / abs(y) if y else None, "at_voltage_rms_v": voltage_rms_v,
            "input_filter_current_rms_a": voltage_rms_v * abs(y), "input_filter_real_power_w": voltage_rms_v ** 2 * y.real,
            "ten_ohm_complex_loading_fraction": abs(10 * y), "hundred_ohm_complex_loading_fraction": abs(100 * y),
            "ten_ohm_loaded_voltage_gain": abs(ratio10), "ten_ohm_loaded_voltage_phase_deg": math.degrees(cmath.phase(ratio10)),
            "hundred_ohm_loaded_voltage_gain": abs(ratio100), "hundred_ohm_loaded_voltage_phase_deg": math.degrees(cmath.phase(ratio100)),
            "branch_power_error_upper_bound_due_to_shunt_filter_w_at_source_5vrms": 5 * voltage_rms_v * abs(y),
            "qualification": "Thevenin loading estimates and unmeasured-current bound, not a revised full coupled RLC solution"}


def check_calculations():
    """Verificações por identidades independentes, sem dados de hardware."""
    checks = []
    def check(name, condition):
        checks.append({"name": name, "passed": bool(condition), "origin": "CALCULATED"})
    check("DC unity of ideal RC cascade", rc_transfer(0) == 1)
    check("Each pole at fc gives total amplitude one quarter", math.isclose(abs(rc_transfer(FC_HZ)), .25, rel_tol=1e-12))
    check("Four poles at fc give minus 12.0412 dB", math.isclose(response(FC_HZ)["ideal_rc_attenuation_db"], 20 * math.log10(4), rel_tol=1e-12))
    check("Unwrapped phase at fc is minus 180 degrees", math.isclose(response(FC_HZ)["ideal_rc_phase_unwrapped_deg"], -180, abs_tol=1e-10))
    x = 5000 / FC_HZ
    check("Independent real closed form equals complex product at 5 kHz", math.isclose(abs(rc_transfer(5000)), (1 + x * x) ** -2, rel_tol=1e-12))
    check("Independent 5 kHz phase identity", math.isclose(math.degrees(cmath.phase(rc_transfer(5000))), -4 * math.degrees(math.atan(x)), abs_tol=1e-10))
    check("High-frequency identity at ten fc", math.isclose(abs(rc_transfer(10 * FC_HZ)), 101 ** -2, rel_tol=1e-12))
    check("Passive first stage draws nonnegative real power", all(burden(f)["input_filter_real_power_w"] >= 0 for f in (0, 100, 1400, 5000, 500000)))
    check("At DC RC input ideal admittance is zero", first_stage_admittance(0) == 0)
    corners = tolerance_corners(5000)
    check("256 independent R C corners and nominal lies between extremes", corners["corners_evaluated"] == 256 and corners["rc_gain_min"] < abs(rc_transfer(5000)) < corners["rc_gain_max"])
    check("Analytic all-fast and all-slow poles match enumerated extrema",
          math.isclose(corners["rc_gain_max"], abs(rc_transfer(5000, [R_OHM * .99] * 4, [C_F * .99] * 4)), rel_tol=1e-12) and
          math.isclose(corners["rc_gain_min"], abs(rc_transfer(5000, [R_OHM * 1.01] * 4, [C_F * 1.01] * 4)), rel_tol=1e-12))
    sr = 2 * math.pi * 5000 * math.sqrt(2) * 5 / 1e6
    check("5 Vrms at 5 kHz slew requirement below typical SR only", math.isclose(sr, .2221441469079183, rel_tol=1e-12) and sr < SR_TYP_V_PER_US)
    check("1 MSps Nyquist ideal attenuation exceeds calculated 70 dB design target", response(500000)["ideal_rc_attenuation_db"] > 70)
    check("100 kSps cannot meet calculated stopband target", response(50000)["ideal_rc_attenuation_db"] < 20)
    return checks


def capabilities():
    sr = 2 * math.pi * 5000 * math.sqrt(2) * 5 / 1e6
    # Projeto usa 70 dB ideal como critério interno, não especificação metrológica.
    minimum_fs_nominal = 2 * FC_HZ * math.sqrt(10 ** (70 / 40) - 1)
    return {"origin": "CALCULATED", "status": "PROPOSED_NOT_BUILT_NOT_MEASURED_NOT_CERTIFIED",
        "circuit": {"base_electrical_channels": 5, "optional_field_channels": 2, "optional_temperature_channels": 1, "channels_with_field": 7, "channels_with_field_and_temperature": 8, "stages_per_channel": STAGES, "quad_part_proposed": "OPA4277PA", "r_each_ohm": R_OHM,
                    "c_each_f": C_F, "r_relative_tolerance": R_TOL, "c_relative_tolerance": C_TOL, "single_pole_fc_hz": FC_HZ,
                    "whole_cascade_minus_3db_hz": FC_HZ * math.sqrt(2 ** .25 - 1), "output_isolation_ohm": OUTPUT_R_OHM,
                    "adc_resistance_assumed_ohm": ADC_R_OHM, "cable_and_adc_capacitance_assumed_f": CABLE_AND_ADC_C_ASSUMED_F},
        "opa4277_typical_only": {"gbw_hz": GBW_TYP_HZ, "slew_v_per_us": SR_TYP_V_PER_US,
            "buffer_model": "four independent one-pole unity followers, fp assumed equal to typical GBW; not vendor macromodel",
            "minimum_gbw_guaranteed_hz": None, "minimum_slew_guaranteed_v_per_us": None,
            "source": "https://www.ti.com/lit/gpn/OPA4277"},
        "responses": [response(f) for f in (0, 100, 1400, 5000, FC_HZ, 50000, 250000, 500000, 1000000)],
        "tolerance_mismatch": [tolerance_corners(f) for f in (1400, 5000, FC_HZ)],
        "input_burden": [burden(f) for f in (1400, 5000)],
        "slew_at_5vrms_5khz": {"required_v_per_us": sr, "ratio_typical_sr_to_required": SR_TYP_V_PER_US / sr,
            "guaranteed_margin": None, "must_measure": True},
        "sampling_assessment": [{"sampling_rate_hz": fs, "nyquist_hz": fs / 2,
            "ideal_rc_attenuation_at_nyquist_db": response(fs / 2)["ideal_rc_attenuation_db"],
            "satisfies_nominal_calculated_70db_design_target": response(fs / 2)["ideal_rc_attenuation_db"] >= 70,
            "hardware_antialias_proven": False,
            "status": "DEFAULT_PROPOSED_REQUIRES_BENCH_CHARACTERIZATION" if fs == 1e6 else "DEGRADED_REQUIRES_NEW_ERROR_BUDGET" if fs == 5e5 else "REJECT_FOR_THIS_FILTER_DESIGN"}
            for fs in (1e6, 5e5, 1e5)],
        "minimum_fs_for_70db_at_nyquist_ideal_nominal_hz": minimum_fs_nominal,
        "minimum_fs_for_70db_fast_rc_corner_hz": minimum_fs_nominal / (.99 * .99),
        "alias_statement": "Finite rolloff never eliminates aliasing. Spectral bounds on out-of-band input, calibrated full-chain response and all nonideal hardware effects are required. Nyquist attenuation alone is not an alias-error guarantee.",
        "calibration_statement": "A scalar gain and offset cannot remove frequency-dependent phase. Calibrate every full path in amplitude and phase at the fundamental and each harmonic, or include residual errors conservatively and leave comparison inconclusive.",
        "checks": check_calculations()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = capabilities()
    if args.output:
        if args.output.exists():
            parser.error("Saída já existe; escolha um nome novo")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps({"origin": report["origin"], "status": report["status"], "single_pole_fc_hz": FC_HZ,
        "at_5khz": response(5000), "checks_passed": sum(c["passed"] for c in report["checks"]), "checks_total": len(report["checks"]),
        "output": str(args.output) if args.output else None}, ensure_ascii=False, indent=2))
    return 0 if all(c["passed"] for c in report["checks"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
