"""Modelo SI clássico, linear e aproximado de duas bobinas circulares no ar.

Sem dependências externas. Executar: py modelo.py --output resultados
Um limite de corrente NÃO recorta a senoide: somente marca a previsão fora
da região válida. Os valores de campo para CA são RMS, no regime permanente.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

MU0 = 4.0 * math.pi * 1e-7
INCH_M = 0.0254


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    source = Path(path) if path else Path(__file__).with_name("configuracao.json")
    config = json.loads(source.read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_config(config: dict[str, Any]) -> None:
    coil, circuit = config["coil"], config["circuit"]
    if coil["count"] != 2 or coil["connection"] != "series_aiding":
        raise ValueError("Este modelo requer duas bobinas idênticas em série aditiva.")
    for key in ("mean_radius_m", "center_separation_m", "turns_each",
                "bare_wire_diameter_m", "insulated_wire_diameter_m",
                "winding_radial_depth_m", "winding_axial_length_m",
                "copper_resistivity_20c_ohm_m"):
        value = coil[key]
        if not isinstance(value, (float, int)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"coil.{key} deve ser positivo e finito.")
    if coil["turns_each"] != int(coil["turns_each"]):
        raise ValueError("O número de espiras deve ser inteiro.")
    if coil["radial_layers"] * coil["turns_per_layer"] != coil["turns_each"]:
        raise ValueError("As camadas e espiras por camada devem reproduzir o total de espiras.")
    if coil["insulated_wire_diameter_m"] < coil["bare_wire_diameter_m"]:
        raise ValueError("Diâmetro isolado não pode ser menor que o diâmetro do cobre.")
    if 2 * coil["mean_radius_m"] <= coil["winding_radial_depth_m"]:
        raise ValueError("O pacote do enrolamento deve caber em torno do raio médio.")
    if coil["center_separation_m"] <= coil["winding_axial_length_m"]:
        raise ValueError("Pacotes de enrolamento sobrepostos não são suportados.")
    if coil["extra_lead_length_m_total"] < 0:
        raise ValueError("Comprimento adicional de fios não pode ser negativo.")
    if circuit["source_waveform"] != "sinusoidal":
        raise ValueError("Este modelo só descreve excitação senoidal.")
    for key in ("source_voltage_max_rms_v", "drive_frequency_hz",
                "current_compliance_rms_a", "series_resistor_ohm",
                "series_resistor_rating_w", "capacitor_f",
                "capacitor_voltage_rating_v", "ideal_tuning_target_hz"):
        value = circuit[key]
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"circuit.{key} deve ser positivo e finito.")
    voltage = circuit["source_voltage_rms_v"]
    if not math.isfinite(voltage) or not 0 <= voltage <= circuit["source_voltage_max_rms_v"]:
        raise ValueError("Tensão RMS da fonte fora da faixa permitida.")
    for key, value in config["numerics"].items():
        if not math.isfinite(value):
            raise ValueError(f"numerics.{key} deve ser finito.")
    for key in ("mutual_angular_samples", "field_angular_samples", "axis_points",
                "slice_points_per_dimension", "sweep_points"):
        value = config["numerics"][key]
        if value != int(value) or value < 8:
            raise ValueError(f"numerics.{key} deve ser inteiro e >=8.")


def wheeler_multilayer_inductance_h(radius_m: float, axial_m: float,
                                   radial_m: float, turns: int) -> float:
    """Wheeler multicamada: L[µH]=0.8 a²N²/(6a+9b+10c), a,b,c em polegadas.

    a=raio médio; b=comprimento axial; c=espessura radial. É estimativa,
    sem modelar passo helicoidal, terminais nem tolerâncias de fabricação.
    """
    a, b, c = radius_m / INCH_M, axial_m / INCH_M, radial_m / INCH_M
    return 1e-6 * 0.8 * a * a * turns * turns / (6 * a + 9 * b + 10 * c)


def mutual_inductance_h(radius_1_m: float, radius_2_m: float,
                        separation_m: float, turns_1: int, turns_2: int,
                        samples: int = 2048) -> float:
    """Integral de Neumann reduzida para dois filamentos circulares coaxiais.

    M = µ0 N1 N2 R1 R2/2 ∫0..2π cosδ /
        sqrt(R1²+R2²-2R1R2cosδ+d²) dδ.
    O fator 1/2 resulta da integral angular externa 2π em µ0/(4π).
    Somatória periódica por ponto médio; M positivo para orientação aditiva.
    """
    if samples < 8 or separation_m <= 0:
        raise ValueError("Separação positiva e pelo menos oito amostras são necessárias.")
    step = 2 * math.pi / samples
    total = 0.0
    for k in range(samples):
        cosine = math.cos((k + 0.5) * step)
        distance = math.sqrt(radius_1_m**2 + radius_2_m**2
                             - 2 * radius_1_m * radius_2_m * cosine + separation_m**2)
        total += cosine / distance
    return MU0 * turns_1 * turns_2 * radius_1_m * radius_2_m * 0.5 * step * total


def circuit_parameters(config: dict[str, Any]) -> dict[str, float]:
    validate_config(config)
    coil, circuit = config["coil"], config["circuit"]
    radius, turns = coil["mean_radius_m"], int(coil["turns_each"])
    self_l = wheeler_multilayer_inductance_h(radius, coil["winding_axial_length_m"],
                                            coil["winding_radial_depth_m"], turns)
    mutual_l = mutual_inductance_h(radius, radius, coil["center_separation_m"],
                                  turns, turns, int(config["numerics"]["mutual_angular_samples"]))
    if not 0 <= mutual_l < self_l:
        raise ValueError("A aproximação produziu M>=L; usar modelo distribuído ou geometria válida.")
    series_l = 2 * self_l + 2 * mutual_l
    winding_length = 2 * turns * 2 * math.pi * radius
    total_length = winding_length + coil["extra_lead_length_m_total"]
    area = math.pi * (coil["bare_wire_diameter_m"] / 2)**2
    resistivity = coil["copper_resistivity_20c_ohm_m"] * (
        1 + coil["copper_temperature_coefficient_per_c"] * (coil["temperature_c"] - 20))
    if resistivity <= 0:
        raise ValueError("Temperatura fora do domínio da aproximação linear de resistividade.")
    copper_r = resistivity * total_length / area
    total_r = copper_r + circuit["series_resistor_ohm"]
    cap = circuit["capacitor_f"]
    resonance = 1 / (2 * math.pi * math.sqrt(series_l * cap))
    tune_omega = 2 * math.pi * circuit["ideal_tuning_target_hz"]
    return {
        "self_inductance_each_h": self_l,
        "mutual_inductance_h": mutual_l,
        "coupling_coefficient": mutual_l / self_l,
        "series_inductance_h": series_l,
        "winding_wire_length_m_total": winding_length,
        "wire_length_m_total_including_leads": total_length,
        "copper_area_m2": area,
        "copper_resistivity_at_temperature_ohm_m": resistivity,
        "copper_resistance_dc_ohm_total": copper_r,
        "series_resistor_ohm": circuit["series_resistor_ohm"],
        "total_series_resistance_ohm": total_r,
        "capacitor_f": cap,
        "capacitor_for_target_frequency_f": 1 / (tune_omega**2 * series_l),
        "target_frequency_hz": circuit["ideal_tuning_target_hz"],
        "resonance_frequency_hz": resonance,
        "quality_factor_at_resonance": 2 * math.pi * resonance * series_l / total_r,
        "skin_depth_at_resonance_m": math.sqrt(2 * resistivity / (2 * math.pi * resonance * MU0))
    }


def loop_axial_b_t(radius_m: float, turns: int, current_a: float, delta_z_m: float) -> float:
    return MU0 * turns * current_a * radius_m**2 / (2 * (radius_m**2 + delta_z_m**2)**1.5)


def pair_axial_b_t(config: dict[str, Any], current_a: float, z_m: float = 0.0) -> float:
    coil = config["coil"]
    half_sep = coil["center_separation_m"] / 2
    return sum(loop_axial_b_t(coil["mean_radius_m"], int(coil["turns_each"]),
                             current_a, z_m - center) for center in (-half_sep, half_sep))


def loop_field_t(radius_m: float, turns: int, current_a: float,
                 point_m: tuple[float, float, float], center_z_m: float = 0.0,
                 samples: int = 360) -> tuple[float, float, float]:
    """Biot-Savart por elementos tangenciais dℓ no ponto médio angular.

    Aproxima todo o enrolamento por N espiras coincidentes no raio médio.
    Usar longe dos condutores; não representa o campo interno do cobre.
    """
    x, y, z = point_m
    dz = z - center_z_m
    step = 2 * math.pi / samples
    bx = by = bz = 0.0
    for k in range(samples):
        angle = (k + 0.5) * step
        cosine, sine = math.cos(angle), math.sin(angle)
        dx, dy = x - radius_m * cosine, y - radius_m * sine
        r2 = dx * dx + dy * dy + dz * dz
        if r2 < 1e-20:
            raise ValueError("Campo singular sobre o filamento ideal.")
        denominator = r2**1.5
        bx += radius_m * cosine * dz / denominator
        by += radius_m * sine * dz / denominator
        bz += radius_m * (radius_m - x * cosine - y * sine) / denominator
    factor = MU0 * turns * current_a * step / (4 * math.pi)
    return bx * factor, by * factor, bz * factor


def pair_field_t(config: dict[str, Any], current_a: float,
                 point_m: tuple[float, float, float], samples: int | None = None
                 ) -> tuple[float, float, float]:
    coil = config["coil"]
    half_sep = coil["center_separation_m"] / 2
    divisions = samples or int(config["numerics"]["field_angular_samples"])
    lower = loop_field_t(coil["mean_radius_m"], int(coil["turns_each"]), current_a,
                         point_m, -half_sep, divisions)
    upper = loop_field_t(coil["mean_radius_m"], int(coil["turns_each"]), current_a,
                         point_m, half_sep, divisions)
    return tuple(a + b for a, b in zip(lower, upper))


def point_inside_winding(config: dict[str, Any], point_m: tuple[float, float, float]) -> bool:
    coil = config["coil"]
    x, y, z = point_m
    radial_distance = abs(math.hypot(x, y) - coil["mean_radius_m"])
    axial_distance = min(abs(z + coil["center_separation_m"] / 2),
                         abs(z - coil["center_separation_m"] / 2))
    return (radial_distance <= coil["winding_radial_depth_m"] / 2
            and axial_distance <= coil["winding_axial_length_m"] / 2)


def operating_point(config: dict[str, Any], parameters: dict[str, float] | None = None,
                     frequency_hz: float | None = None, source_rms_v: float | None = None
                     ) -> dict[str, Any]:
    parameters = parameters or circuit_parameters(config)
    circuit = config["circuit"]
    freq = circuit["drive_frequency_hz"] if frequency_hz is None else frequency_hz
    source = circuit["source_voltage_rms_v"] if source_rms_v is None else source_rms_v
    if not math.isfinite(freq) or freq <= 0 or not math.isfinite(source) or source < 0:
        raise ValueError("Frequência positiva e tensão não negativa, ambas finitas, são necessárias.")
    omega = 2 * math.pi * freq
    resistance = parameters["total_series_resistance_ohm"]
    xl, xc = omega * parameters["series_inductance_h"], 1 / (omega * parameters["capacitor_f"])
    reactance = xl - xc
    impedance = math.hypot(resistance, reactance)
    current = source / impedance
    phase = math.atan2(reactance, resistance)
    power = current**2 * resistance
    resistor_power = current**2 * parameters["series_resistor_ohm"]
    copper_power = current**2 * parameters["copper_resistance_dc_ohm_total"]
    cap_v, ind_v = current * xc, current * xl
    current_ok = current <= circuit["current_compliance_rms_a"] * (1 + 1e-12)
    source_ok = source <= circuit["source_voltage_max_rms_v"] * (1 + 1e-12)
    resistor_ok = resistor_power <= circuit["series_resistor_rating_w"]
    # Rating is conservatively compared to sinusoidal peak, not directly to RMS.
    capacitor_peak_v = math.sqrt(2) * cap_v
    capacitor_ok = capacitor_peak_v <= circuit["capacitor_voltage_rating_v"]
    within_domain = current_ok and source_ok and resistor_ok and capacitor_ok
    return {
        "frequency_hz": freq,
        "source_voltage_rms_v": source,
        "impedance_magnitude_ohm": impedance,
        "reactance_ohm": reactance,
        "current_rms_a": current,
        "current_peak_a": math.sqrt(2) * current,
        "current_phase_degrees_relative_to_voltage": -math.degrees(phase),
        "power_factor": resistance / impedance,
        "input_real_power_w": power,
        "series_resistor_dissipation_w": resistor_power,
        "copper_dissipation_w": copper_power,
        "total_dissipation_w": resistor_power + copper_power,
        "useful_load_output_power_w": 0.0,
        "useful_load_present": False,
        "capacitor_voltage_rms_v": cap_v,
        "capacitor_voltage_peak_v": capacitor_peak_v,
        "inductors_voltage_rms_v_total": ind_v,
        "magnetic_energy_average_j": 0.5 * parameters["series_inductance_h"] * current**2,
        "magnetic_energy_max_j": parameters["series_inductance_h"] * current**2,
        "capacitor_energy_average_j": 0.5 * parameters["capacitor_f"] * cap_v**2,
        "capacitor_energy_max_j": parameters["capacitor_f"] * cap_v**2,
        "center_field_rms_t": pair_axial_b_t(config, current),
        "center_field_peak_t": pair_axial_b_t(config, math.sqrt(2) * current),
        "current_compliance_satisfied": current_ok,
        "source_range_satisfied": source_ok,
        "resistor_power_rating_satisfied": resistor_ok,
        "capacitor_peak_voltage_rating_satisfied": capacitor_ok,
        "within_stated_operating_limits": within_domain,
        "prediction_valid_if_sinusoidal_source_remains_in_voltage_mode": within_domain,
        "current_limit_action": "check_only_no_clipping"
    }


def linspace(start: float, stop: float, count: int) -> list[float]:
    return [start + (stop - start) * i / (count - 1) for i in range(count)]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def export_results(config: dict[str, Any], output: str | Path) -> dict[str, Any]:
    destination = Path(output)
    destination.mkdir(parents=True, exist_ok=True)
    parameters = circuit_parameters(config)
    baseline = operating_point(config, parameters)
    resonance = operating_point(config, parameters, parameters["resonance_frequency_hz"])
    maximum_source = operating_point(config, parameters, parameters["resonance_frequency_hz"],
                                     config["circuit"]["source_voltage_max_rms_v"])
    current = baseline["current_rms_a"]
    numeric = config["numerics"]
    axis_rows = []
    for z in linspace(numeric["axis_start_m"], numeric["axis_end_m"], int(numeric["axis_points"])):
        bx, by, bz = pair_field_t(config, current, (0, 0, z))
        analytic = pair_axial_b_t(config, current, z)
        axis_rows.append({"z_m": z, "bx_rms_t": bx, "by_rms_t": by, "bz_rms_t": bz,
                          "bz_analytic_rms_t": analytic,
                          "relative_error_bz": abs(bz - analytic) / abs(analytic)})
    slice_rows = []
    grid = linspace(numeric["slice_min_m"], numeric["slice_max_m"],
                    int(numeric["slice_points_per_dimension"]))
    for z in grid:
        for x in grid:
            inside = point_inside_winding(config, (x, 0, z))
            bx, by, bz = (None, None, None) if inside else pair_field_t(config, current, (x, 0, z))
            magnitude = None if inside else math.sqrt(bx * bx + by * by + bz * bz)
            slice_rows.append({"x_m": x, "y_m": 0.0, "z_m": z,
                               "bx_rms_t": bx, "by_rms_t": by, "bz_rms_t": bz,
                               "magnitude_rms_t": magnitude, "inside_winding_excluded": inside})
    frequencies = linspace(numeric["sweep_min_hz"], numeric["sweep_max_hz"],
                          int(numeric["sweep_points"]))
    frequencies.append(parameters["resonance_frequency_hz"])
    sweep_rows = []
    for freq in sorted(set(frequencies)):
        point = operating_point(config, parameters, freq)
        sweep_rows.append({key: point[key] for key in (
            "frequency_hz", "current_rms_a", "current_phase_degrees_relative_to_voltage",
            "input_real_power_w", "series_resistor_dissipation_w", "copper_dissipation_w",
            "capacitor_voltage_rms_v", "capacitor_voltage_peak_v", "inductors_voltage_rms_v_total",
            "center_field_rms_t", "magnetic_energy_average_j", "within_stated_operating_limits")})
    results = {
        "model": "Classical air-core coupled coils; ideal linear lumped series RLC",
        "units": "SI; voltages/currents/fields labelled RMS or peak explicitly",
        "parameters": parameters,
        "operating_point": baseline,
        "resonance_point": resonance,
        "maximum_source_at_resonance": maximum_source,
        "assumptions": [
            "Self inductance: Wheeler multilayer approximation, not measured inductance.",
            "Mutual inductance and field: N coincident mean-radius circular filaments per coil.",
            "Copper resistance estimated from DC resistivity and winding length at fixed temperature.",
            "Skin/proximity loss, winding capacitance, capacitor ESR, resistor parasitics and lead inductance omitted.",
            "Ideal sinusoidal voltage source; output impedance is omitted and must be measured or added.",
            "Current compliance only checks the prediction; no nonlinear current-limited waveform is simulated.",
            "Nominal 10 microfarad capacitor; component tolerances are not sampled.",
            "100 V capacitor rating checked against peak; verify the real AC/ripple and frequency rating.",
            "Continuous operation temperature and mechanical construction require bench validation.",
            "This calculation cannot demonstrate vacuum energy extraction, spacetime curvature or quantum propulsion."
        ],
        "field_grid": {
            "plane": "y=0",
            "basis": "RMS amplitude in phase with series current",
            "coil_pack_points_excluded": True,
            "sample_counts": {"axis": len(axis_rows), "slice": len(slice_rows), "sweep": len(sweep_rows)}
        }
    }
    (destination / "resultados.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    (destination / "campo.json").write_text(json.dumps({"axis": axis_rows, "slice": slice_rows},
                                                      ensure_ascii=False), encoding="utf-8")
    write_csv(destination / "campo_eixo.csv", axis_rows)
    write_csv(destination / "campo_plano_xz.csv", slice_rows)
    write_csv(destination / "varredura_frequencia.csv", sweep_rows)
    (destination / "configuracao_utilizada.json").write_text(json.dumps(config, ensure_ascii=False, indent=2),
                                                          encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("resultados"))
    args = parser.parse_args()
    results = export_results(load_config(args.config), args.output)
    print(json.dumps({"output": str(args.output.resolve()), "parameters": results["parameters"],
                      "operating_point": results["operating_point"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
