"""Testes analíticos SYNTHETIC; fixtures apenas em diretório temporário."""
from __future__ import annotations

import argparse
import copy
import csv
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest

import analisar


def synthetic_metadata():
    channels = {name: {"gain": 1.0, "offset": 0.0, "gain_relative_bound": 0.0, "offset_native_bound": 0.0,
                      "noise_absolute_bound": 0.0, "phase_bound_deg": 0.0, "bandwidth_hz": 1000.0,
                      "calibration_document": "SYNTHETIC_ANALYTICAL_FIXTURE_NOT_A_CERTIFICATE"}
                for name in analisar.VOLTAGES + ("field_t",)}
    return {"schema_version": "3.0", "origin": "SYNTHETIC", "experiment_id": "SYNTHETIC_ANALYTICAL_TEST_ONLY",
            "git_commit": "0" * 40, "frequency_hz": 100.0, "frequency_absolute_bound_hz": 0.0, "window_cycles": 10,
            "geometry_as_built_document": "SYNTHETIC_NO_PHYSICAL_BUILD", "receiver_enabled": True,
            "source_boundary": {"location": "SYNTHETIC before RLC and return resistor", "includes_series_resistors": True, "positive_current": "source_to_circuit"},
            "acquisition": {"simultaneous": True, "max_channel_skew_s": 0.0, "sample_clock_relative_bound": 0.0,
                            "antialias_cutoff_hz": 1000.0, "antialias_document": "SYNTHETIC exact finite Fourier signals",
                            "clipping_detected": False, "stationary_confirmed": True},
            "instruments": [{"model": "SYNTHETIC", "serial": "SYNTHETIC", "calibration_document": "SYNTHETIC", "calibration_valid_until": "2099-01-01"}],
            "channels": channels,
            "resistors": {"series1": {"measured_ohm": 10.0, "absolute_bound_ohm": 0.0, "calibration_document": "SYNTHETIC"},
                          "series2": {"measured_ohm": 10.0, "absolute_bound_ohm": 0.0, "calibration_document": "SYNTHETIC"},
                          "load": {"measured_ohm": 100.0, "absolute_bound_ohm": 0.0, "calibration_document": "SYNTHETIC"}},
            "temperature_sensor": {"calibration_document": "SYNTHETIC", "absolute_bound_c": 0.0},
            "field_measurement": {"axis": "z", "location": "center", "background_record": "SYNTHETIC"},
            "baseline_records": ["SYNTHETIC_NOT_AN_EXPERIMENT"]}


class MeasurementsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="nucleo_SYNTHETIC_")
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.meta = synthetic_metadata()
        self.dt = 1 / 12800
        self.rows = []
        for n in range(1280):
            t = n * self.dt
            theta = 2 * math.pi * 100 * t
            self.rows.append([t, 2 * math.sqrt(2) * math.cos(theta), math.sqrt(2) * math.cos(theta),
                              3 * math.sqrt(2) * math.cos(theta), 2 * math.sqrt(2) * math.cos(theta),
                              .1 * math.sqrt(2) * math.cos(theta)])
        self.names = list(analisar.REQUIRED)

    def files(self):
        raw = self.folder / "SYNTHETIC_waveforms.csv"
        meta = self.folder / "SYNTHETIC_metadata.json"
        with raw.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(self.names)
            writer.writerows(self.rows)
        meta.write_text(json.dumps(self.meta, allow_nan=False), encoding="utf-8")
        return raw, meta

    def report(self, config=None):
        raw, meta = self.files()
        return analisar.analyze(raw, meta, config)

    def rejected(self, pattern):
        with self.assertRaisesRegex(ValueError, pattern):
            self.report()

    def test_analytic_resistive_rms_power_and_energy(self):
        report = self.report()
        self.assertAlmostEqual(report["signals"]["current1_a"]["rms_ac"], .1, places=12)
        self.assertAlmostEqual(report["source_power_w"]["source1"], .2, places=12)
        self.assertAlmostEqual(report["source_power_w"]["source2"], .6, places=12)
        self.assertAlmostEqual(report["load_power_w"], .0001, places=12)
        self.assertAlmostEqual(report["integrated_energy_j"]["source1"], .02, places=12)
        self.assertEqual(report["origin"], "SYNTHETIC")
        self.assertEqual(report["status"], "SYNTHETIC_SOFTWARE_CHECK_ONLY")
        self.assertNotIn("PASS", report["status"])

    def test_quadrature_has_zero_real_power(self):
        for row in self.rows:
            row[2] = math.sqrt(2) * math.cos(2 * math.pi * 100 * row[0] - math.pi / 2)
        report = self.report()
        self.assertAlmostEqual(report["source_power_w"]["source1"], 0, places=12)
        self.assertAlmostEqual(report["source_voltage_minus_current_phase_deg"]["source1"], 90, places=10)
        self.assertAlmostEqual(report["signals"]["current1_a"]["rms_ac"], .1, places=12)

    def test_negative_power_preserves_absorption(self):
        for row in self.rows:
            row[2] *= -1
        report = self.report()
        self.assertAlmostEqual(report["source_power_w"]["source1"], -.2, places=12)
        self.assertIn("negative is absorbed", report["energy_interpretation"])

    def test_inverse_gain_and_offset_calibration(self):
        self.meta["channels"]["v_source1_v"].update(gain=-2.0, offset=.3)
        for row in self.rows:
            row[1] = row[1] / -2 + .3
        report = self.report()
        self.assertAlmostEqual(report["signals"]["v_source1_v"]["rms_ac"], 2, places=12)
        self.assertAlmostEqual(report["signals"]["v_source1_v"]["dc"], 0, places=12)
        self.assertAlmostEqual(report["source_power_w"]["source1"], .2, places=12)

    def test_dc_is_separated_from_ac(self):
        for row in self.rows:
            row[1] += .2
            row[2] += .1
        report = self.report()
        self.assertAlmostEqual(report["signals"]["current1_a"]["dc"], .01, places=12)
        self.assertAlmostEqual(report["signals"]["current1_a"]["rms_ac"], .1, places=12)
        self.assertAlmostEqual(report["source_dc_power_w"]["source1"], .002, places=12)
        self.assertAlmostEqual(report["source_ac_power_w"]["source1"], .2, places=12)
        self.assertTrue(any("componente CC" in text for text in report["inconclusive_reasons"]))

    def test_known_third_harmonic(self):
        for row in self.rows:
            row[1] += .2 * math.sqrt(2) * math.cos(6 * math.pi * 100 * row[0])
        report = self.report()
        self.assertAlmostEqual(report["signals"]["v_source1_v"]["thd_ratio"], .1, places=11)
        self.assertTrue(any("THD" in text for text in report["inconclusive_reasons"]))

    def test_phase_uncertainty_does_not_collapse_at_quadrature(self):
        for row in self.rows:
            row[2] = math.sqrt(2) * math.sin(2 * math.pi * 100 * row[0])
        self.meta["channels"]["v_source1_v"]["phase_bound_deg"] = 1.0
        report = self.report()
        self.assertAlmostEqual(report["source_power_w"]["source1"], 0, places=12)
        self.assertGreater(report["source_power_absolute_bounds_w"]["source1"], .0034)
        self.assertIsNone(report["uncertainty"]["coverage_probability"])

    def test_resistance_gain_bounds_enclose_exact_perturbation(self):
        self.meta["channels"]["v_source1_v"]["gain_relative_bound"] = .01
        self.meta["resistors"]["series1"]["absolute_bound_ohm"] = .1
        report = self.report()
        perturbed_power = .2 * 1.01 * 10 / 9.9
        self.assertGreaterEqual(report["source_power_absolute_bounds_w"]["source1"], abs(perturbed_power - .2) - 1e-12)

    def test_zero_baseline_never_validates_field(self):
        self.meta["origin"] = "EXPERIMENTAL"
        self.names.append("field_t")
        for row in self.rows:
            row[1:] = [0.0] * 5
            row.append(0.0)
        report = self.report()
        self.assertEqual(report["status"], "INCONCLUSIVE")
        self.assertAlmostEqual(report["source_power_w"]["total"], 0)
        self.assertTrue(any("Campo magnético ausente ou zero" in text for text in report["inconclusive_reasons"]))

    def test_missing_equipment_and_uncertainty_is_inconclusive(self):
        self.meta["origin"] = "EXPERIMENTAL"
        self.meta["instruments"] = []
        self.meta["channels"]["v_source1_v"]["gain_relative_bound"] = None
        self.meta["resistors"]["series1"]["absolute_bound_ohm"] = None
        report = self.report()
        self.assertEqual(report["status"], "INCONCLUSIVE")
        self.assertIsNone(report["source_power_absolute_bounds_w"]["source1"])
        self.assertTrue(any("instrumentos incompleta" in text for text in report["inconclusive_reasons"]))

    def test_duplicate_timestamp_rejected(self):
        self.rows[50][0] = self.rows[49][0]
        self.rejected("duplicatas")

    def test_nonuniform_sampling_rejected(self):
        self.rows[50][0] += self.dt * .01
        self.rejected("não uniforme")

    def test_desynchronized_acquisition_rejected(self):
        self.meta["acquisition"]["simultaneous"] = False
        self.rejected("simultâneos")

    def test_excess_channel_skew_rejected(self):
        self.meta["acquisition"]["max_channel_skew_s"] = .00002
        self.rejected("Desalinhamento")

    def test_invalid_window_rejected(self):
        self.meta["window_cycles"] = 11
        self.rejected("window_cycles")

    def test_short_noninteger_window_rejected(self):
        self.meta["window_cycles"] = None
        self.meta["frequency_hz"] = 103.21
        self.rejected("Nenhuma janela coerente")

    def test_automatic_window_discards_tail(self):
        self.meta["window_cycles"] = None
        for n in range(1280, 1300):
            t = n * self.dt
            self.rows.append([t, 0, 0, 0, 0, 0])
        report = self.report()
        self.assertEqual(report["window"]["samples"], 1280)
        self.assertEqual(report["window"]["discarded_samples"], 20)
        self.assertAlmostEqual(report["source_power_w"]["source1"], .2, places=12)

    def test_nan_in_raw_rejected(self):
        self.rows[40][1] = float("nan")
        self.rejected("NaN/Inf")

    def test_inf_in_raw_rejected(self):
        self.rows[40][2] = float("inf")
        self.rejected("NaN/Inf")

    def test_empty_cell_rejected(self):
        self.rows[40][2] = ""
        self.rejected("célula vazia")

    def test_pending_metadata_never_becomes_result(self):
        self.meta["origin"] = "PENDENTE"
        self.rejected("origin obrigatório")

    def test_gain_zero_and_bad_resistor_bound_rejected(self):
        self.meta["channels"]["v_source1_v"]["gain"] = 0
        self.rejected("ganho não pode ser zero")
        self.meta["channels"]["v_source1_v"]["gain"] = 1
        self.meta["resistors"]["series1"]["absolute_bound_ohm"] = 10
        self.rejected("limite de erro >= resistência")

    def test_clock_frequency_coverage_inconclusive(self):
        self.meta["acquisition"]["sample_clock_relative_bound"] = .01
        report = self.report()
        self.assertTrue(any("Erro possível de frequência/relógio" in text for text in report["inconclusive_reasons"]))

    def test_legacy_export_exact_header_and_missing_values_empty(self):
        report = self.report()
        destination = self.folder / "SYNTHETIC_summary.csv"
        analisar.write_legacy(destination, report)
        with destination.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.reader(stream, delimiter=";"))
        self.assertEqual(rows[0], list(analisar.LEGACY_HEADER))
        self.assertEqual(rows[1][6], "")
        self.assertEqual(rows[1][9], "")
        self.assertEqual(rows[1][5], "1")

    def test_model_import_is_read_only_and_uses_measured_drive(self):
        self.names.extend(["temperature_c", "field_t"])
        for row in self.rows:
            row.extend([25.0, 1e-6 * math.sqrt(2) * math.cos(2 * math.pi * 100 * row[0])])
        config = analisar.REPO / "nucleo_integral_v2/simulacao/configuracao.json"
        js = config.with_name("modelo_browser.js")
        before = (config.read_bytes(), js.read_bytes())
        report = self.report(config)
        self.assertEqual((config.read_bytes(), js.read_bytes()), before)
        predicted = report["prediction_v2"]
        self.assertEqual(predicted["configuration_used"]["geometry"]["temperature_c"], 25)
        self.assertAlmostEqual(predicted["configuration_used"]["circuit"]["drives"][0]["voltage_rms_v"], 2, places=12)
        self.assertAlmostEqual(predicted["configuration_used"]["circuit"]["drives"][1]["voltage_rms_v"], 3, places=12)
        self.assertEqual(set(report["comparisons"]), {"I_lower_rms_A", "I_upper_rms_A", "P_sources_W", "P_load_W", "B_center_rms_uT"})
        self.assertTrue(all(item["interpretation"] == "INCONCLUSIVE" for item in report["comparisons"].values()))

    def test_expired_calibration_is_inconclusive(self):
        self.meta["instruments"][0]["calibration_valid_until"] = "2000-01-01"
        report = self.report()
        self.assertTrue(any("vencida" in text for text in report["inconclusive_reasons"]))

    def test_inadequate_calibrated_band_is_inconclusive(self):
        self.meta["channels"]["v_source1_v"]["bandwidth_hz"] = 500
        report = self.report()
        self.assertTrue(any("não cobre toda a banda" in text for text in report["inconclusive_reasons"]))

    def test_cli_refuses_shared_output_paths(self):
        raw, meta = self.files()
        destination = self.folder / "SYNTHETIC_no_collision.json"
        self.assertEqual(analisar.main([str(raw), str(meta), "--output", str(destination), "--summary-csv", str(destination)]), 2)
        self.assertFalse(destination.exists())

    def test_cli_json_keeps_synthetic_label_and_raw_hash(self):
        raw, meta = self.files()
        destination = self.folder / "SYNTHETIC_report.json"
        summary = self.folder / "SYNTHETIC_summary.csv"
        raw_before = raw.read_bytes()
        self.assertEqual(analisar.main([str(raw), str(meta), "--output", str(destination), "--summary-csv", str(summary)]), 0)
        report = json.loads(destination.read_text(encoding="utf-8"))
        self.assertEqual(report["origin"], "SYNTHETIC")
        self.assertEqual(report["data_sha256"], analisar.hashlib.sha256(raw_before).hexdigest())
        self.assertEqual(raw.read_bytes(), raw_before)
        self.assertTrue(summary.exists())

    def test_cli_refuses_output_overwrite(self):
        raw, meta = self.files()
        existing = self.folder / "preserve.json"
        existing.write_text("EVIDENCE", encoding="utf-8")
        self.assertEqual(analisar.main([str(raw), str(meta), "--output", str(existing)]), 2)
        self.assertEqual(existing.read_text(encoding="utf-8"), "EVIDENCE")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(MeasurementsTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if args.json_output:
        if args.json_output.exists():
            parser.error("Relatório já existe: escolha outro nome para preservar o anterior")
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps({"origin": "SYNTHETIC_SOFTWARE_TESTS_NOT_EXPERIMENTAL", "tests_run": result.testsRun,
            "success": result.wasSuccessful(), "failures": [str(test) for test, _ in result.failures],
            "errors": [str(test) for test, _ in result.errors]}, indent=2), encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
