"""Validação matemática independente de protótipo físico; não certifica hardware.

Executar: py validar.py --output resultados/resultados_validacao.json
"""

from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path

from modelo import (MU0, circuit_parameters, load_config, loop_axial_b_t,
                    loop_field_t, mutual_inductance_h, operating_point,
                    pair_axial_b_t, pair_field_t)


def relative_error(actual: float, expected: float) -> float:
    return abs(actual - expected) / max(abs(expected), 1e-30)


def run_validation() -> dict:
    config = load_config()
    parameters = circuit_parameters(config)
    coil, circuit = config["coil"], config["circuit"]
    r, n, d = coil["mean_radius_m"], coil["turns_each"], coil["center_separation_m"]
    checks = []

    def add(name: str, passed: bool, evidence: dict) -> None:
        checks.append({"name": name, "passed": bool(passed), **evidence})

    expected = MU0 * n * 0.2 / (2 * r)
    computed = loop_field_t(r, n, 0.2, (0, 0, 0), samples=360)
    err = relative_error(computed[2], expected)
    add("loop_center_against_closed_form", err < 1e-12 and abs(computed[0]) < 1e-15,
        {"relative_error": err, "tolerance": 1e-12, "computed_t": computed[2], "analytic_t": expected})

    axial_errors = []
    transverse = []
    for z in (-0.3, -0.1, -0.025, 0, 0.04, 0.16, 0.3):
        field = pair_field_t(config, 0.2, (0, 0, z), samples=360)
        axial_errors.append(relative_error(field[2], pair_axial_b_t(config, 0.2, z)))
        transverse.append(math.hypot(field[0], field[1]))
    add("pair_axis_against_closed_form", max(axial_errors) < 1e-12 and max(transverse) < 1e-15,
        {"max_relative_error": max(axial_errors), "max_transverse_field_t": max(transverse),
         "tolerance": 1e-12, "sample_points": 7})

    helmholtz = (4 / 5)**1.5 * MU0 * n * 0.2 / r
    helmholtz_value = pair_axial_b_t(config, 0.2)
    delta = 0.0001
    center = pair_axial_b_t(config, 0.2, 0)
    second_derivative = (pair_axial_b_t(config, 0.2, delta) - 2 * center
                         + pair_axial_b_t(config, 0.2, -delta)) / delta**2
    normalized_curvature = abs(second_derivative * r**2 / center)
    add("helmholtz_center_and_zero_axial_curvature", relative_error(helmholtz_value, helmholtz) < 1e-12
        and normalized_curvature < 1e-5 and d == r,
        {"relative_error_center": relative_error(helmholtz_value, helmholtz),
         "normalized_second_derivative": normalized_curvature,
         "curvature_tolerance": 1e-5, "finite_difference_step_m": delta})

    point = (0.034, -0.018, 0.027)
    pair = pair_field_t(config, 0.2, point)
    lower = loop_field_t(r, n, 0.2, point, -d / 2)
    upper = loop_field_t(r, n, 0.2, point, d / 2)
    doubled = pair_field_t(config, 0.4, point)
    difference = max(abs(pair[i] - lower[i] - upper[i]) for i in range(3))
    linear_error = max(abs(doubled[i] - 2 * pair[i]) for i in range(3))
    add("field_superposition_and_current_linearity", max(difference, linear_error) < 1e-15,
        {"max_superposition_error_t": difference, "max_linearity_error_t": linear_error})

    m12 = mutual_inductance_h(0.1, 0.08, 0.1, 50, 40, samples=1024)
    m21 = mutual_inductance_h(0.08, 0.1, 0.1, 40, 50, samples=1024)
    add("mutual_reciprocity", relative_error(m12, m21) < 1e-12,
        {"mutual_12_h": m12, "mutual_21_h": m21, "relative_error": relative_error(m12, m21)})

    m16 = mutual_inductance_h(r, r, d, n, n, samples=16)
    m32 = mutual_inductance_h(r, r, d, n, n, samples=32)
    m64 = mutual_inductance_h(r, r, d, n, n, samples=64)
    mref = mutual_inductance_h(r, r, d, n, n, samples=4096)
    mutual_errors = [relative_error(value, mref) for value in (m16, m32, m64)]
    add("neumann_integral_discretization_convergence", mutual_errors[1] < mutual_errors[0]
        and mutual_errors[2] < 1e-10,
        {"samples": [16, 32, 64], "reference_samples": 4096,
         "relative_errors": mutual_errors, "final_tolerance": 1e-10})

    near_point = (0.11, 0.0, 0.060)
    ref = pair_field_t(config, 0.2, near_point, samples=2880)
    norm = math.sqrt(sum(value * value for value in ref))
    field_errors = []
    for samples in (60, 120, 360):
        field = pair_field_t(config, 0.2, near_point, samples=samples)
        field_errors.append(math.sqrt(sum((field[i] - ref[i])**2 for i in range(3))) / norm)
    add("off_axis_biot_savart_discretization_convergence", field_errors[1] < field_errors[0]
        and field_errors[2] < 1e-6,
        {"point_m": near_point, "samples": [60, 120, 360], "reference_samples": 2880,
         "relative_vector_errors": field_errors, "final_tolerance": 1e-6})

    eigen_min = parameters["self_inductance_each_h"] - parameters["mutual_inductance_h"]
    eigen_max = parameters["self_inductance_each_h"] + parameters["mutual_inductance_h"]
    add("inductance_matrix_positive_energy", 0 < eigen_min <= eigen_max,
        {"eigenvalues_h": [eigen_min, eigen_max], "coupling_coefficient": parameters["coupling_coefficient"]})

    f0 = parameters["resonance_frequency_hz"]
    resonance = operating_point(config, parameters, f0)
    below = operating_point(config, parameters, f0 * 0.9)
    above = operating_point(config, parameters, f0 * 1.1)
    current_target = circuit["source_voltage_rms_v"] / parameters["total_series_resistance_ohm"]
    current_error = relative_error(resonance["current_rms_a"], current_target)
    add("series_rlc_resonance", abs(resonance["reactance_ohm"]) < 1e-10 and current_error < 1e-12
        and resonance["current_rms_a"] > max(below["current_rms_a"], above["current_rms_a"]),
        {"resonance_hz": f0, "residual_reactance_ohm": resonance["reactance_ohm"],
         "relative_current_error": current_error, "neighbor_current_rms_a": [below["current_rms_a"],
                                                                                above["current_rms_a"]]})

    max_power_error = 0.0
    passive = True
    instantaneous_energy_errors = []
    omega = 2 * math.pi * f0
    i_peak = resonance["current_peak_a"]
    for frequency in (100, 500, 1000, f0, 2000, 5000):
        point_state = operating_point(config, parameters, frequency)
        supplied = (point_state["source_voltage_rms_v"] * point_state["current_rms_a"]
                    * point_state["power_factor"])
        max_power_error = max(max_power_error, relative_error(point_state["total_dissipation_w"], supplied))
        passive = passive and 0 <= point_state["useful_load_output_power_w"] <= supplied * (1 + 1e-12)
    stored_target = parameters["series_inductance_h"] * resonance["current_rms_a"]**2
    for k in range(101):
        phase = 2 * math.pi * k / 100
        magnetic = 0.5 * parameters["series_inductance_h"] * (i_peak * math.sin(phase))**2
        cap_voltage = -i_peak / (omega * parameters["capacitor_f"]) * math.cos(phase)
        electric = 0.5 * parameters["capacitor_f"] * cap_voltage**2
        instantaneous_energy_errors.append(relative_error(magnetic + electric, stored_target))
    energy_error = relative_error(resonance["magnetic_energy_max_j"], resonance["capacitor_energy_max_j"])
    add("passive_real_power_balance", passive and max_power_error < 1e-12,
        {"max_relative_power_balance_error": max_power_error,
         "useful_output_w": 0.0, "note": "No useful load modeled; supplied power dissipates as heat."})
    add("resonant_electric_magnetic_energy_exchange", energy_error < 1e-12
        and max(instantaneous_energy_errors) < 1e-12,
        {"max_magnetic_energy_j": resonance["magnetic_energy_max_j"],
         "max_capacitor_energy_j": resonance["capacitor_energy_max_j"],
         "relative_max_energy_difference": energy_error,
         "max_relative_error_total_instantaneous_stored_energy": max(instantaneous_energy_errors)})

    high = copy.deepcopy(config)
    high["circuit"]["current_compliance_rms_a"] = 0.01
    outside = operating_point(high, circuit_parameters(high), f0)
    add("current_limit_is_compliance_check_only", not outside["current_compliance_satisfied"]
        and not outside["prediction_valid_if_sinusoidal_source_remains_in_voltage_mode"]
        and relative_error(outside["current_rms_a"], current_target) < 1e-12,
        {"declared_limit_a": 0.01, "unclipped_linear_prediction_rms_a": outside["current_rms_a"],
         "prediction_marked_outside_domain": True})

    maximum_voltage = operating_point(config, parameters, f0, circuit["source_voltage_max_rms_v"])
    add("baseline_and_maximum_source_limits", operating_point(config, parameters)["within_stated_operating_limits"]
        and maximum_voltage["within_stated_operating_limits"],
        {"source_max_rms_v": maximum_voltage["source_voltage_rms_v"],
         "current_max_at_resonance_rms_a": maximum_voltage["current_rms_a"],
         "series_resistor_dissipation_w": maximum_voltage["series_resistor_dissipation_w"],
         "capacitor_peak_voltage_v": maximum_voltage["capacitor_voltage_peak_v"],
         "note": "Ratings check is theoretical and omits thermal rise and actual AC capacitor specifications."})

    return {"validation_scope": "Numerical and analytic checks of approximate classical model; no hardware test.",
            "all_passed": all(check["passed"] for check in checks), "check_count": len(checks),
            "passed_count": sum(check["passed"] for check in checks), "checks": checks}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).with_name("resultados") / "resultados_validacao.json")
    args = parser.parse_args()
    results = run_validation()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    raise SystemExit(0 if results["all_passed"] else 1)


if __name__ == "__main__":
    main()
