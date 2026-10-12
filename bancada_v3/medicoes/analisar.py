"""Aquisição exportada e análise de bancada; somente biblioteca padrão.

Nenhum dado de exemplo é experimental. Não controla fontes ou instrumentos.
Os limites de erro declarados são limites conservadores, sem probabilidade de
cobertura ou fator k implícito. Consulte README.md antes de conectar a bancada.
"""
from __future__ import annotations

import argparse
import cmath
import copy
import csv
from datetime import date, datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import statistics
import sys

REQUIRED = ("time_s", "v_source1_v", "v_series1_v", "v_source2_v", "v_series2_v", "v_load_v")
OPTIONAL = ("temperature_c", "field_t")
VOLTAGES = REQUIRED[1:]
LEGACY_HEADER = ("frequency_hz", "V_lower_rms_V", "V_upper_rms_V", "phase_upper_deg", "load_ohm", "receiver_enabled", "temperature_C", "I_lower_rms_A", "I_upper_rms_A", "B_center_rms_uT", "P_sources_W", "P_load_W")
REPO = Path(__file__).resolve().parents[2]


def finite(value, name, positive=False, nonnegative=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name}: número finito obrigatório")
    if positive and value <= 0 or nonnegative and value < 0:
        raise ValueError(f"{name}: valor fora do intervalo")
    return float(value)


def read_waveforms(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        names = reader.fieldnames or []
        if len(names) != len(set(names)) or not set(REQUIRED).issubset(names):
            raise ValueError("CSV precisa dos cabeçalhos únicos: " + ",".join(REQUIRED))
        if set(names) - set(REQUIRED + OPTIONAL):
            raise ValueError("Colunas desconhecidas: converta a exportação para o formato documentado")
        columns = {name: [] for name in names}
        for line, row in enumerate(reader, 2):
            if None in row:
                raise ValueError(f"Linha {line}: colunas excedentes")
            for name in names:
                try:
                    value = float(row[name])
                except (ValueError, TypeError):
                    raise ValueError(f"Linha {line}, {name}: célula vazia ou não numérica") from None
                if not math.isfinite(value):
                    raise ValueError(f"Linha {line}, {name}: NaN/Inf não permitido")
                columns[name].append(value)
    if len(columns["time_s"]) < 40:
        raise ValueError("Aquisição vazia ou curta: pelo menos 40 amostras")
    return columns


def calibrated(raw, channel, name):
    """Convenção explícita: físico = (exportado - offset) * gain."""
    gain = finite(channel.get("gain"), name + ".gain")
    offset = finite(channel.get("offset"), name + ".offset")
    if gain == 0:
        raise ValueError(f"{name}: ganho não pode ser zero")
    values = [(value - offset) * gain for value in raw]
    if any(not math.isfinite(value) for value in values):
        raise ValueError(f"{name}: calibração produziu valor não finito")
    bound_keys = ("gain_relative_bound", "offset_native_bound", "noise_absolute_bound", "phase_bound_deg")
    for key in bound_keys:
        if channel.get(key) is not None:
            finite(channel[key], name + "." + key, nonnegative=True)
    ready = all(channel.get(key) is not None for key in bound_keys)
    if not ready:
        return values, None
    rel, off, noise, phase = [finite(channel[key], name + "." + key, nonnegative=True) for key in bound_keys]
    if rel >= 1 or phase > 180:
        raise ValueError(f"{name}: limites de calibração inválidos")
    return values, [abs(value) * rel + abs(gain) * off + noise for value in values]


def coherent_window(columns, metadata):
    times = columns["time_s"]
    diffs = [b - a for a, b in zip(times, times[1:])]
    if min(diffs) <= 0:
        raise ValueError("time_s precisa ser estritamente crescente, sem duplicatas")
    dt = statistics.median(diffs)
    if max(abs(d - dt) for d in diffs) > max(dt * 1e-4, 1e-15):
        raise ValueError("Amostragem não uniforme; não reamostrar silenciosamente")
    acquisition = metadata.get("acquisition", {})
    if acquisition.get("simultaneous") is not True:
        raise ValueError("Aquisição precisa declarar canais simultâneos em um mesmo relógio")
    skew = finite(acquisition.get("max_channel_skew_s"), "max_channel_skew_s", nonnegative=True)
    frequency = finite(metadata.get("frequency_hz"), "frequency_hz", positive=True)
    if skew * frequency > .001:
        raise ValueError("Desalinhamento entre canais excede 0,001 período; corrigir e recalibrar a aquisição")
    if 1 / dt < 20 * frequency:
        raise ValueError("Taxa de amostragem precisa ser >=20 vezes a frequência fundamental")
    requested = metadata.get("window_cycles")
    maximum = int(math.floor(len(times) * dt * frequency + 1e-4))
    if requested is not None:
        if isinstance(requested, bool) or not isinstance(requested, int) or requested < 5 or requested > maximum:
            raise ValueError("window_cycles: inteiro >=5 e dentro da aquisição")
        candidates = [requested]
    else:
        candidates = range(maximum, 4, -1)
    for cycles in candidates:
        count = round(cycles / (dt * frequency))
        if count <= len(times) and abs(count * dt * frequency - cycles) <= 1e-4:
            break
    else:
        raise ValueError("Nenhuma janela coerente >=5 ciclos inteiros; ajustar duração/frequência da aquisição")
    return {name: values[:count] for name, values in columns.items()}, {
        "sampling_rate_hz": 1 / dt, "sample_interval_s": dt, "samples": count,
        "cycles": cycles, "frequency_hz": frequency, "duration_s": count * dt,
        "discarded_samples": len(times) - count, "interchannel_skew_bound_s": skew,
        "integration": "média retangular em janela coerente, última amostra sem duplicar o ponto final",
    }


def average(values):
    return math.fsum(values) / len(values)


def rms(values):
    return math.sqrt(max(0.0, average([value * value for value in values])))


def dft(values, times, frequency, harmonic=1):
    start = times[0]
    omega = 2 * math.pi * frequency * harmonic
    # Fasor RMS com referência cosseno; o tempo inicial serve de referência.
    return math.sqrt(2) * sum(value * cmath.exp(-1j * omega * (t - start)) for value, t in zip(values, times)) / len(values)


def signal_stats(values, times, frequency, harmonics):
    dc = average(values)
    ac = rms([value - dc for value in values])
    fundamental = dft(values, times, frequency)
    amplitude = abs(fundamental)
    h = [abs(dft(values, times, frequency, order)) for order in range(2, harmonics + 1)]
    return {"dc": dc, "rms_total": rms(values), "rms_ac": ac,
            "fundamental_rms": amplitude, "phase_deg": math.degrees(cmath.phase(fundamental)) if amplitude > 1e-15 else None,
            "thd_ratio": math.sqrt(math.fsum(v * v for v in h)) / amplitude if amplitude > 1e-15 and harmonics >= 2 else None,
            "thd_max_harmonic": harmonics,
            "fundamental_fraction_of_ac_rms": min(1.0, amplitude / ac) if ac > 1e-15 else None}


def resistance(metadata, name):
    item = metadata.get("resistors", {}).get(name, {})
    value = finite(item.get("measured_ohm"), name + ".measured_ohm", positive=True)
    bound = item.get("absolute_bound_ohm")
    if bound is not None:
        bound = finite(bound, name + ".absolute_bound_ohm", nonnegative=True)
        if bound >= value:
            raise ValueError(f"{name}: limite de erro >= resistência")
    return value, bound


def current_from_shunt(voltage, voltage_bounds, resistor, resistor_bound):
    values = [v / resistor for v in voltage]
    if voltage_bounds is None or resistor_bound is None:
        return values, None
    # Intervalo conservador, também inclui termo cruzado do denominador.
    bounds = [e / (resistor - resistor_bound) + abs(v) * resistor_bound / (resistor * (resistor - resistor_bound)) for v, e in zip(voltage, voltage_bounds)]
    return values, bounds


def power_bound(voltage, current, voltage_bounds, current_bounds, angle_bound_rad):
    if voltage_bounds is None or current_bounds is None or angle_bound_rad is None:
        return None
    sample_bound = average([abs(v) * ei + abs(i) * ev + ev * ei for v, i, ev, ei in zip(voltage, current, voltage_bounds, current_bounds)])
    # Limite de mudança de correlação para fase relativa limitada em toda a banda.
    return sample_bound + 2 * rms(voltage) * rms(current) * math.sin(min(math.pi, angle_bound_rad) / 2)


def calibration_coverage(metadata, channels, window, reasons):
    acq = metadata["acquisition"]
    for key in ("sample_clock_relative_bound", "antialias_cutoff_hz"):
        if acq.get(key) is None:
            reasons.append(f"acquisition.{key} pendente")
        else:
            finite(acq[key], key, nonnegative=True)
    cutoff = acq.get("antialias_cutoff_hz")
    if cutoff is not None and (cutoff < window["frequency_hz"] or cutoff >= window["sampling_rate_hz"] / 2):
        raise ValueError("Filtro antialias precisa cobrir a fundamental e estar abaixo de Nyquist")
    if not acq.get("antialias_document"):
        reasons.append("Caracterização do filtro antialias pendente")
    if acq.get("clipping_detected") is not False:
        reasons.append("Ausência de clipping não confirmada")
    if acq.get("stationary_confirmed") is not True:
        reasons.append("Regime estacionário não confirmado")
    freq_bound = metadata.get("frequency_absolute_bound_hz")
    if freq_bound is None:
        reasons.append("Limite de erro da frequência medida pendente")
    else:
        freq_bound = finite(freq_bound, "frequency_absolute_bound_hz", nonnegative=True)
        clock_bound = acq.get("sample_clock_relative_bound") or 0
        if (freq_bound + clock_bound * window["frequency_hz"]) * window["duration_s"] > 1e-3:
            reasons.append("Erro possível de frequência/relógio >0,001 ciclo na janela; revisar coerência e DFT")
    instruments = metadata.get("instruments", [])
    if not instruments or any(not all(instrument.get(k) for k in ("model", "serial", "calibration_document", "calibration_valid_until")) for instrument in instruments):
        reasons.append("Identificação/calibração dos instrumentos incompleta")
    for instrument in instruments:
        validity = instrument.get("calibration_valid_until")
        if validity:
            try:
                if date.fromisoformat(validity) < date.today():
                    reasons.append("Calibração instrumental vencida na data desta análise")
            except ValueError:
                reasons.append("Data de validade da calibração inválida; usar AAAA-MM-DD")
    for name in channels:
        cal = metadata.get("channels", {}).get(name, {})
        if not cal.get("calibration_document") or any(cal.get(k) is None for k in ("gain_relative_bound", "offset_native_bound", "noise_absolute_bound", "phase_bound_deg", "bandwidth_hz")):
            reasons.append(f"Calibração/limites do canal {name} pendentes")
        bandwidth = cal.get("bandwidth_hz")
        if bandwidth is not None:
            bandwidth = finite(bandwidth, name + ".bandwidth_hz", positive=True)
            if bandwidth < window["frequency_hz"]:
                reasons.append(f"Banda do canal {name} não cobre a fundamental")
            if cutoff is not None and bandwidth < cutoff:
                reasons.append(f"Banda calibrada do canal {name} não cobre toda a banda transmitida pelo filtro")
        if metadata["origin"] == "EXPERIMENTAL" and all(cal.get(k) == 0 for k in ("gain_relative_bound", "offset_native_bound", "noise_absolute_bound", "phase_bound_deg")):
            reasons.append(f"{name}: todos os limites nulos não sustentam uma medição real")
    location = metadata.get("source_boundary", {}).get("location")
    if not location or "PENDENTE" in location.upper() or not metadata.get("source_boundary", {}).get("includes_series_resistors") is True:
        reasons.append("Fronteira das fontes precisa ser anterior aos shunts e descrita")
    if metadata.get("source_boundary", {}).get("positive_current") != "source_to_circuit":
        raise ValueError("Convenção positive_current precisa ser source_to_circuit")
    if not metadata.get("geometry_as_built_document"):
        reasons.append("Geometria construída e orientação não documentadas")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", str(metadata.get("git_commit", ""))):
        reasons.append("Commit Git de 40 caracteres pendente")
    for name in ("series1", "series2", "load"):
        item = metadata.get("resistors", {}).get(name, {})
        if item.get("absolute_bound_ohm") is None or not item.get("calibration_document"):
            reasons.append(f"Valor medido/limite/calibração do resistor {name} incompleto")
    return cutoff


def wrapped_phase(degrees):
    return (degrees + 180) % 360 - 180


def load_model(config_path, stats, metadata, temperatures, reasons):
    """Importa o solver existente sem executar export_all ou alterar arquivos V2."""
    if config_path is None:
        return None
    spec = importlib.util.spec_from_file_location("nucleo_v2_read_only", REPO / "nucleo_integral_v2/simulacao/modelo_integral.py")
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    config = json.loads(Path(config_path).read_text(encoding="utf-8-sig"))
    config = copy.deepcopy(config)
    if config.get("toroidal", {}).get("enabled"):
        reasons.append("Toroide adicional ativo: fontes extras fora da medição de cinco canais")
    if config["circuit"]["drives"][0]["orientation"] != 1 or config["circuit"]["drives"][1]["orientation"] != 1:
        reasons.append("Orientação de bobinas exige revisão manual da convenção de corrente")
    r1, _ = resistance(metadata, "series1")
    r2, _ = resistance(metadata, "series2")
    if not math.isclose(r1, r2, rel_tol=1e-5):
        reasons.append("Solver V2 usa um único R série; shunts reais diferentes requerem extensão do solver")
    config["circuit"]["series_resistor_each_ohm"] = (r1 + r2) / 2
    config["receiver"]["load_ohm"] = resistance(metadata, "load")[0]
    config["circuit"]["frequency_hz"] = metadata["frequency_hz"]
    reference_phase = stats["v_source1_v"]["phase_deg"]
    for j, name in enumerate(("v_source1_v", "v_source2_v")):
        config["circuit"]["drives"][j]["voltage_rms_v"] = stats[name]["fundamental_rms"]
        config["circuit"]["drives"][j]["phase_deg"] = wrapped_phase((stats[name]["phase_deg"] or 0) - (reference_phase or 0))
    if temperatures is not None:
        config["geometry"]["temperature_c"] = average(temperatures)
    else:
        reasons.append("Temperatura medida ausente; previsão usa temperatura do JSON")
    params = model.parameters(config)
    solution = model.circuit_solution(config, params)
    if solution["validity"]["warnings"]:
        reasons.append("Avisos de validade do modelo: " + "; ".join(solution["validity"]["warnings"]))
    field = model.field_solution(config, solution, (0, 0, (config["geometry"]["coil_center_lower_m"] + config["geometry"]["coil_center_upper_m"]) / 2))
    return {"configuration_path": str(config_path), "configuration_sha256": hashlib.sha256(Path(config_path).read_bytes()).hexdigest(),
            "I_lower_rms_A": solution["currents"][0]["rms"], "I_upper_rms_A": solution["currents"][1]["rms"],
            "P_sources_W": solution["power"]["source_total_w"], "P_load_W": solution["power"]["receiver_load_w"],
            "B_center_rms_uT": field["magnitude_rms_t"] * 1e6,
            "model_uncertainty": "NOT_QUANTIFIED; geometry, parasitics, AC resistance and parameter errors remain",
            "configuration_used": config}


def analyze(waveform_path, metadata_path, config_path=None):
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8-sig"))
    if metadata.get("origin") not in ("EXPERIMENTAL", "SYNTHETIC"):
        raise ValueError("origin obrigatório: EXPERIMENTAL ou SYNTHETIC; template PENDENTE não é resultado")
    if not metadata.get("experiment_id"):
        raise ValueError("experiment_id obrigatório")
    raw = read_waveforms(waveform_path)
    columns, window = coherent_window(raw, metadata)
    reasons = []
    names = list(VOLTAGES) + (["field_t"] if "field_t" in columns else [])
    cutoff = calibration_coverage(metadata, names, window, reasons)
    corrected, bounds = {}, {}
    for name in names:
        corrected[name], bounds[name] = calibrated(columns[name], metadata.get("channels", {}).get(name, {}), name)
    frequency = window["frequency_hz"]
    harmonics = max(1, min(10, int(window["sampling_rate_hz"] / (20 * frequency)), int(cutoff / frequency) if cutoff is not None else 1))
    times = columns["time_s"]
    stats = {name: signal_stats(values, times, frequency, harmonics) for name, values in corrected.items()}
    currents, current_bounds, powers, power_bounds, powers_dc, phase_vi = {}, {}, {}, {}, {}, {}
    for j in (1, 2):
        vname, sname = f"v_source{j}_v", f"v_series{j}_v"
        r, rb = resistance(metadata, f"series{j}")
        currents[j], current_bounds[j] = current_from_shunt(corrected[sname], bounds[sname], r, rb)
        stats[f"current{j}_a"] = signal_stats(currents[j], times, frequency, harmonics)
        powers[j] = average([v * i for v, i in zip(corrected[vname], currents[j])])
        powers_dc[j] = average(corrected[vname]) * average(currents[j])
        vp, ip = stats[vname]["phase_deg"], stats[f"current{j}_a"]["phase_deg"]
        phase_vi[j] = wrapped_phase(vp - ip) if vp is not None and ip is not None else None
        cv, ci = metadata["channels"][vname], metadata["channels"][sname]
        phase_bound = None
        if cv.get("phase_bound_deg") is not None and ci.get("phase_bound_deg") is not None and cutoff is not None:
            phase_bound = math.radians(cv["phase_bound_deg"] + ci["phase_bound_deg"]) + 2 * math.pi * cutoff * window["interchannel_skew_bound_s"]
        power_bounds[j] = power_bound(corrected[vname], currents[j], bounds[vname], current_bounds[j], phase_bound)
    load_r, load_rb = resistance(metadata, "load")
    load_i, load_i_bound = current_from_shunt(corrected["v_load_v"], bounds["v_load_v"], load_r, load_rb)
    p_load = average([v * i for v, i in zip(corrected["v_load_v"], load_i)])
    p_load_bound = power_bound(corrected["v_load_v"], load_i, bounds["v_load_v"], load_i_bound, 0)
    p_sum = powers[1] + powers[2]
    p_sum_bound = sum(power_bounds.values()) if all(value is not None for value in power_bounds.values()) else None
    field = stats.get("field_t")
    field_meta = metadata.get("field_measurement", {})
    if field is None or field["rms_ac"] <= 1e-15:
        reasons.append("Campo magnético ausente ou zero: sem validação do campo")
    elif field_meta.get("axis") != "z" or field_meta.get("location") != "center" or not field_meta.get("background_record"):
        reasons.append("Campo requer eixo z central e aquisição de fundo documentada; não é magnitude vetorial 3D")
    for name in VOLTAGES:
        if stats[name]["thd_ratio"] is None or stats[name]["thd_ratio"] > .01:
            reasons.append(f"{name}: THD fundamental ausente ou >1%; comparação fasorial V2 inconclusiva")
        fraction = stats[name]["fundamental_fraction_of_ac_rms"]
        if fraction is None or fraction < .995:
            reasons.append(f"{name}: energia fora da fundamental / sinal insuficiente")
        if abs(stats[name]["dc"]) > max(1e-12, .01 * stats[name]["rms_ac"]):
            reasons.append(f"{name}: componente CC relevante; modelo fasorial cobre apenas CA")
    if metadata["origin"] == "SYNTHETIC":
        reasons.append("Dados sintéticos verificam o software; não são evidência experimental")
    if not metadata.get("baseline_records"):
        reasons.append("Controles de fontes desligadas/carga conhecida não registrados")
    if config_path is None and metadata.get("model_config_path"):
        config_path = (Path(metadata_path).resolve().parent / metadata["model_config_path"]).resolve()
    predicted = load_model(config_path, stats, metadata, columns.get("temperature_c"), reasons)
    if "temperature_c" in columns:
        sensor = metadata.get("temperature_sensor", {})
        if not sensor.get("calibration_document") or sensor.get("absolute_bound_c") is None:
            reasons.append("Calibração/incerteza do sensor de temperatura pendente")
    if predicted is None:
        reasons.append("Configuração do modelo não fornecida: sem comparação quantitativa")
    measurements = {"I_lower_rms_A": stats["current1_a"]["rms_ac"], "I_upper_rms_A": stats["current2_a"]["rms_ac"],
                    "P_sources_W": p_sum, "P_load_W": p_load, "B_center_rms_uT": field["rms_ac"] * 1e6 if field else None}
    metric_bounds = {"I_lower_rms_A": rms(current_bounds[1]) if current_bounds[1] is not None else None,
                     "I_upper_rms_A": rms(current_bounds[2]) if current_bounds[2] is not None else None,
                     "P_sources_W": p_sum_bound, "P_load_W": p_load_bound,
                     "B_center_rms_uT": rms(bounds["field_t"]) * 1e6 if field and bounds["field_t"] is not None else None}
    comparisons = {}
    if predicted:
        for key, value in measurements.items():
            expected, bound = predicted[key], metric_bounds[key]
            delta = value - expected if value is not None else None
            comparisons[key] = {"measured": value, "predicted": expected, "difference": delta, "measurement_absolute_bound": bound,
                "interpretation": "INCONCLUSIVE" if value is None or bound is None or reasons else
                    "WITHIN_DECLARED_MEASUREMENT_BOUND_MODEL_UNCERTAINTY_UNKNOWN" if abs(delta) <= bound else
                    "DIFFERENCE_EXCEEDS_MEASUREMENT_BOUND_REVIEW_MODEL_AND_SETUP"}
    reasons = list(dict.fromkeys(reasons))
    phase12 = None
    if stats["v_source1_v"]["phase_deg"] is not None and stats["v_source2_v"]["phase_deg"] is not None:
        phase12 = wrapped_phase(stats["v_source2_v"]["phase_deg"] - stats["v_source1_v"]["phase_deg"])
    clock_bound = metadata["acquisition"].get("sample_clock_relative_bound")
    duration_bound = window["duration_s"] * clock_bound if clock_bound is not None else None
    def energy_bound(power, bound):
        return None if bound is None or duration_bound is None else bound * window["duration_s"] + abs(power) * duration_bound + bound * duration_bound
    return {"schema_version": "3.0", "analyzed_at_utc": datetime.now(timezone.utc).isoformat(), "origin": metadata["origin"], "experiment_id": metadata["experiment_id"],
            "status": "SYNTHETIC_SOFTWARE_CHECK_ONLY" if metadata["origin"] == "SYNTHETIC" else "INCONCLUSIVE" if reasons else "MEASURED_WITH_DECLARED_BOUNDS_MODEL_NOT_PHYSICALLY_VALIDATED",
            "inconclusive_reasons": reasons, "data_sha256": hashlib.sha256(Path(waveform_path).read_bytes()).hexdigest(),
            "metadata_sha256": hashlib.sha256(Path(metadata_path).read_bytes()).hexdigest(), "metadata": metadata,
            "window": window, "signals": stats, "source2_relative_phase_deg": phase12,
            "source_voltage_minus_current_phase_deg": {"source1": phase_vi[1], "source2": phase_vi[2]},
            "source_power_w": {"source1": powers[1], "source2": powers[2], "total": p_sum},
            "source_dc_power_w": {"source1": powers_dc[1], "source2": powers_dc[2]},
            "source_ac_power_w": {"source1": powers[1] - powers_dc[1], "source2": powers[2] - powers_dc[2]},
            "source_power_absolute_bounds_w": {"source1": power_bounds[1], "source2": power_bounds[2], "total": p_sum_bound},
            "load_power_w": p_load, "load_power_absolute_bound_w": p_load_bound,
            "integrated_energy_j": {"source1": powers[1] * window["duration_s"], "source2": powers[2] * window["duration_s"], "load": p_load * window["duration_s"]},
            "integrated_energy_absolute_bounds_j": {"source1": energy_bound(powers[1], power_bounds[1]), "source2": energy_bound(powers[2], power_bounds[2]), "load": energy_bound(p_load, p_load_bound)},
            "temperature_measured_c": average(columns["temperature_c"]) if "temperature_c" in columns else None,
            "measurements": measurements, "measurement_absolute_bounds": metric_bounds, "prediction_v2": predicted, "comparisons": comparisons,
            "uncertainty": {"method": "worst-case absolute bounds; correlated errors added, not RSS", "coverage_probability": None, "coverage_factor_k": None,
                "limitations": "Bounds conditional on declared calibration validity, bandwidth, anti-aliasing, stable coherent signals and bounded skew. No automatic metrology certification; model uncertainty unquantified."},
            "energy_interpretation": "Positive source power is supplied; negative is absorbed. Source-minus-load includes all unmeasured dissipation/storage. A residual is never evidence of extra energy or quantum/gravitational effects."}


def write_legacy(path, report):
    """CSV de resumo compatível; o JSON é o registro obrigatório de proveniência."""
    s, m, meta = report["signals"], report["measurements"], report["metadata"]
    temperature = report.get("temperature_measured_c")
    row = [report["window"]["frequency_hz"], s["v_source1_v"]["rms_ac"], s["v_source2_v"]["rms_ac"], report["source2_relative_phase_deg"],
           resistance(meta, "load")[0], int(bool(meta.get("receiver_enabled", True))), temperature,
           m["I_lower_rms_A"], m["I_upper_rms_A"], m["B_center_rms_uT"], m["P_sources_W"], m["P_load_W"]]
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter=";")
        writer.writerow(LEGACY_HEADER)
        writer.writerow(["" if v is None else v for v in row])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("waveforms", type=Path)
    parser.add_argument("metadata", type=Path)
    parser.add_argument("--config", type=Path, help="JSON V2 da geometria realmente construída")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary-csv", type=Path)
    args = parser.parse_args(argv)
    try:
        report = analyze(args.waveforms, args.metadata, args.config)
        if args.summary_csv and args.output.resolve() == args.summary_csv.resolve():
            raise ValueError("O JSON de proveniência e o CSV de resumo precisam de caminhos diferentes")
        for output in (args.output, args.summary_csv):
            if output and output.exists():
                raise ValueError(f"Saída já existe, preserve a evidência e escolha outro nome: {output}")
            if output and output.resolve() in (args.waveforms.resolve(), args.metadata.resolve()):
                raise ValueError("A saída não pode sobrescrever os dados brutos")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        if args.summary_csv:
            args.summary_csv.parent.mkdir(parents=True, exist_ok=True)
            write_legacy(args.summary_csv, report)
        print(json.dumps({"status": report["status"], "origin": report["origin"], "report": str(args.output), "inconclusive_reasons": report["inconclusive_reasons"]}, ensure_ascii=False))
    except (ValueError, KeyError, OSError, TypeError) as error:
        print(f"Aquisição rejeitada: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
