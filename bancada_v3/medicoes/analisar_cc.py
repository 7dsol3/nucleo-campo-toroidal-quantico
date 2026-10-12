"""Ensaio CC estacionário com fundo separado; não é validação quântica."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import statistics
import sys

from analisar import REPO, VOLTAGES, average, calibrated, current_from_shunt, finite, power_bound, read_waveforms, resistance, rms


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dc_record(path, meta):
    raw = read_waveforms(path)
    intervals = [b - a for a, b in zip(raw["time_s"], raw["time_s"][1:])]
    dt = statistics.median(intervals)
    if dt <= 0 or min(intervals) <= 0 or max(abs(value - dt) for value in intervals) > max(1e-15, dt * 1e-4):
        raise ValueError("CC: timestamps precisam ser crescentes e amostragem uniforme")
    values, bounds = {}, {}
    for name in VOLTAGES + (("field_t",) if "field_t" in raw else ()):
        if name not in meta["channels"]:
            raise ValueError("Metadados de canal ausentes: " + name)
        values[name], bounds[name] = calibrated(raw[name], meta["channels"][name], name)
    for j in (1, 2):
        r, er = resistance(meta, f"series{j}")
        values[f"current{j}_a"], bounds[f"current{j}_a"] = current_from_shunt(values[f"v_series{j}_v"], bounds[f"v_series{j}_v"], r, er)
    stats = {}
    for name, signal in values.items():
        center = average(signal)
        stats[name] = {"mean": center, "standard_deviation": statistics.stdev(signal),
                       "residual_rms_about_mean": rms([v - center for v in signal]),
                       "mean_absolute_error_bound": average(bounds[name]) if bounds[name] is not None else None}
    powers = {}
    for j in (1, 2):
        v, i = values[f"v_source{j}_v"], values[f"current{j}_a"]
        powers[f"source{j}"] = {"mean_signed_w": average([a * b for a, b in zip(v, i)]),
            "absolute_bound_w": power_bound(v, i, bounds[f"v_source{j}_v"], bounds[f"current{j}_a"], 0)}
    return {"samples": len(raw["time_s"]), "duration_s": len(raw["time_s"]) * dt, "signals": stats, "power": powers,
            "temperature_mean_c": average(raw["temperature_c"]) if "temperature_c" in raw else None}


def analyze_cc(on_path, off_path, metadata_path):
    metadata_path = Path(metadata_path)
    meta = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    essentials = ("origin", "experiment_id", "mode", "channels", "resistors", "model_config_path", "fem_results_path", "on_record", "background_record")
    if any(key not in meta for key in essentials):
        raise ValueError("Metadados CC essenciais ausentes")
    if meta["origin"] not in ("EXPERIMENTAL", "SYNTHETIC") or not meta["experiment_id"] or meta["mode"] != "DC_MAGNETOSTATIC":
        raise ValueError("Origem/identificação/modo CC pendentes ou inválidos")
    if any(meta[key].get("origin") != meta["origin"] for key in ("on_record", "background_record")):
        raise ValueError("Fundo e energizado precisam da mesma origem declarada")
    acq = meta.get("acquisition", {})
    if acq.get("simultaneous") is not True:
        raise ValueError("CC exige aquisição simultânea dos canais em cada registro")
    if Path(on_path).resolve() == Path(off_path).resolve():
        raise ValueError("Fundo e energizado precisam ser arquivos distintos")
    on, off = dc_record(on_path, meta), dc_record(off_path, meta)
    reasons, fem_reasons = [], []
    for key, path in (("on_record", on_path), ("background_record", off_path)):
        expected = meta[key].get("sha256")
        if expected and expected != digest(path):
            raise ValueError(key + ": SHA-256 não corresponde ao arquivo bruto")
        if not expected:
            reasons.append(key + ": hash prévio da captura pendente")
    if meta["origin"] == "SYNTHETIC":
        reasons.append("Sinais sintéticos não são evidência física")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", str(meta.get("git_commit", ""))):
        reasons.append("Commit do ensaio pendente")
    if not meta.get("geometry_as_built_document"):
        reasons.append("Geometria construída não documentada")
    if not meta.get("instruments") or any(not all(item.get(k) for k in ("model", "serial", "calibration_document")) for item in meta.get("instruments", [])):
        reasons.append("Identificação/calibração dos instrumentos pendente")
    if acq.get("stationary_confirmed") is not True or acq.get("clipping_detected") is not False:
        reasons.append("Regime estacionário/ausência de clipping não confirmados")
        fem_reasons.append("Regime estacionário não confirmado")
    if not meta.get("source_boundary_document"):
        reasons.append("Fronteira de potência e polaridades pendentes")
    if meta.get("field_axis") != "z":
        reasons.append("Orientação calibrada da sonda no eixo z pendente")
    for name in VOLTAGES + (("field_t",) if "field_t" in on["signals"] else ()):
        channel = meta["channels"][name]
        if not channel.get("calibration_document") or on["signals"][name]["mean_absolute_error_bound"] is None:
            reasons.append("Calibração/incerteza incompleta: " + name)
        if meta["origin"] == "EXPERIMENTAL" and all(channel.get(k) == 0 for k in ("gain_relative_bound", "offset_native_bound", "noise_absolute_bound")):
            reasons.append("Limites todos nulos não sustentam medição real: " + name)
    for name in ("series1", "series2"):
        if not meta["resistors"][name].get("calibration_document") or meta["resistors"][name].get("absolute_bound_ohm") is None:
            reasons.append("Shunt medido/incerteza pendente: " + name)
    config_path = (metadata_path.resolve().parent / meta["model_config_path"]).resolve()
    config = json.loads(config_path.read_text(encoding="utf-8-sig"))
    spec = importlib.util.spec_from_file_location("v2_dc_readonly", REPO / "nucleo_integral_v2/simulacao/modelo_integral.py")
    v2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v2)
    g = config["geometry"]
    point = meta.get("field_point_m")
    if not isinstance(point, list) or len(point) != 3 or any(not isinstance(v, (float, int)) or not math.isfinite(v) for v in point):
        reasons.append("Ponto da sonda pendente")
        point = [0, 0, .125]
        fem_reasons.append("Ponto da sonda não informado")
    if point[0] != 0 or point[1] != 0:
        raise ValueError("Comparação CC implementada apenas no eixo z, x=y=0")
    currents = [on["signals"][f"current{j}_a"]["mean"] for j in (1, 2)]
    current_bounds = [on["signals"][f"current{j}_a"]["mean_absolute_error_bound"] for j in (1, 2)]
    orientations = [config["circuit"]["drives"][j]["orientation"] for j in (0, 1)]
    physical_currents = [i * o for i, o in zip(currents, orientations)]
    coefficients = [sum(v2.loop_axis_b_per_a(radius, point[2] - z) for radius, z in v2.winding_loops(g, g[f"coil_center_{position}_m"])) for position in ("lower", "upper")]
    predicted_v2 = sum(c * i for c, i in zip(coefficients, physical_currents))
    measured_field, field_bound = None, None
    if "field_t" in on["signals"] and "field_t" in off["signals"]:
        measured_field = on["signals"]["field_t"]["mean"] - off["signals"]["field_t"]["mean"]
        drift = meta.get("background_drift_absolute_bound_t")
        eb = [record["signals"]["field_t"]["mean_absolute_error_bound"] for record in (on, off)]
        if drift is not None:
            drift = finite(drift, "background_drift_absolute_bound_t", nonnegative=True)
        if all(e is not None for e in eb) and drift is not None:
            field_bound = sum(eb) + drift
        else:
            reasons.append("Limite do campo/fundo/deriva pendente")
        if abs(measured_field) <= (field_bound or 1e-15):
            reasons.append("Campo líquido zero ou não resolvido pelo limite de medição")
    else:
        reasons.append("Campo ausente no energizado ou no fundo")
    for j in (1, 2):
        signal = on["signals"][f"current{j}_a"]
        if signal["standard_deviation"] > .01 * abs(signal["mean"]):
            fem_reasons.append("Corrente não estacionária dentro de 1%")
        baseline = off["signals"][f"current{j}_a"]
        if abs(baseline["mean"]) > max(1e-9, baseline["mean_absolute_error_bound"] or 0):
            reasons.append("Fundo tem corrente de bobina diferente de zero")
            fem_reasons.append("Fundo não corresponde a bobinas desligadas")
    mean_i = sum(physical_currents) / 2
    if abs(mean_i) <= 1e-12 or any(e is None for e in current_bounds) or abs(physical_currents[0] - physical_currents[1]) + sum(e or 0 for e in current_bounds) > .01 * abs(mean_i):
        fem_reasons.append("Correntes não demonstradas iguais dentro do limite conservador de 1%")
    if meta.get("receiver_open") is not True or meta.get("capacitors_bypassed") is not True or meta.get("toroid_off") is not True:
        fem_reasons.append("Exige receptor aberto, capacitores desviados e toroide desligado")
    if config.get("toroidal", {}).get("enabled"):
        fem_reasons.append("Configuração tem toroide auxiliar ativo")
    baseline_geometry = {"coil_mean_radius_m": .1, "coil_center_lower_m": .065, "coil_center_upper_m": .185,
                         "radial_layers": 5, "turns_per_layer": 10, "wire_pitch_m": .0011}
    if any(not math.isclose(g.get(key, -1), value, rel_tol=1e-10, abs_tol=1e-12) for key, value in baseline_geometry.items()) or point != [0, 0, .125]:
        fem_reasons.append("Geometria/ponto diferentes do FEM fine_box060; não escalar esse caso")
    fem_path = (metadata_path.resolve().parent / meta["fem_results_path"]).resolve()
    fem = json.loads(fem_path.read_text(encoding="utf-8-sig"))
    case = next((case for case in fem.get("cases", []) if case["name"] == "fine_box060"), None)
    if case is None or fem.get("current_A_each") != .15:
        raise ValueError("Artefato FEM esperado fine_box060 com 0,15 A por bobina ausente")
    fem_prediction = case["center_Bz_T"] * mean_i / .15 if not fem_reasons else None
    reasons += fem_reasons
    return {"schema_version": "3.0-CC", "origin": meta["origin"], "experiment_id": meta["experiment_id"],
        "status": "SYNTHETIC_SOFTWARE_CHECK_ONLY" if meta["origin"] == "SYNTHETIC" else "INCONCLUSIVE" if reasons else "MEASURED_WITH_DECLARED_BOUNDS_MODEL_UNCERTAINTY_UNKNOWN",
        "inconclusive_reasons": list(dict.fromkeys(reasons)), "metadata": meta,
        "sha256": {"on": digest(on_path), "background": digest(off_path), "metadata": digest(metadata_path), "config": digest(config_path), "fem": digest(fem_path)},
        "on": on, "background": off, "measured_net_Bz_T": measured_field, "measured_Bz_absolute_bound_T": field_bound,
        "v2": {"center_Bz_T": predicted_v2, "current_physical_A": physical_currents, "field_per_ampere_T_A": coefficients,
               "difference_measured_minus_model_T": measured_field - predicted_v2 if measured_field is not None else None,
               "current_only_prediction_bound_T": sum(abs(c) * e for c, e in zip(coefficients, current_bounds)) if all(e is not None for e in current_bounds) else None,
               "model_uncertainty": "NOT_QUANTIFIED: geometry and magnetic environment not covered"},
        "fem": {"case": "fine_box060", "comparison_status": "INCONCLUSIVE" if reasons else "SCALING_ELIGIBLE_MODEL_NOT_EXPERIMENTALLY_VALIDATED", "scaling_eligible": not fem_reasons,
                "skip_reasons": fem_reasons, "center_Bz_scaled_T": fem_prediction, "scale_current_mean_physical_A": mean_i,
                "difference_measured_minus_model_T": measured_field - fem_prediction if measured_field is not None and fem_prediction is not None else None,
                "observed_numerical_center_relative_error": case.get("center_relative_error"),
                "qualification": "Observed ~2.79% center discrepancy for this numerical case, not a universal model uncertainty or confidence bound"},
        "uncertainty": {"method": "conservative absolute bounds; on and background added plus documented drift; no assumed cancellation", "coverage_probability": None},
        "interpretation": "Classical magnetostatic comparison only. No conclusion about vacuum energy, gravity, spacetime or quantum effects; no physical PASS generated."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("energized", type=Path)
    parser.add_argument("background", type=Path)
    parser.add_argument("metadata", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.output.exists() or args.output.resolve() in (args.energized.resolve(), args.background.resolve(), args.metadata.resolve()):
            raise ValueError("Escolha uma saída nova, distinta das evidências")
        report = analyze_cc(args.energized, args.background, args.metadata)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        print(json.dumps({"status": report["status"], "origin": report["origin"], "output": str(args.output)}, ensure_ascii=False))
    except (ValueError, KeyError, TypeError, OSError) as error:
        print("CC rejeitado: " + str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
