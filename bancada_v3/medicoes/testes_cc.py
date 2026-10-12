"""Fixtures CC SYNTHETIC geradas e removidas em diretório temporário."""
import copy
import csv
import json
import math
from pathlib import Path
import tempfile
import unittest

import analisar_cc as cc
from testes import synthetic_metadata


class TestDC(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="nucleo_CC_SYNTHETIC_")
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.meta = synthetic_metadata()
        self.meta.update(mode="DC_MAGNETOSTATIC", receiver_open=True, capacitors_bypassed=True, toroid_off=True,
                         model_config_path=str(cc.REPO / "nucleo_integral_v2/simulacao/configuracao.json"),
                         fem_results_path=str(cc.REPO / "bancada_v3/fem/outputs/resultados.json"), field_point_m=[0, 0, .125], field_axis="z",
                         background_drift_absolute_bound_t=0, source_boundary_document="SYNTHETIC",
                         on_record={"origin": "SYNTHETIC"}, background_record={"origin": "SYNTHETIC"})
        self.on, self.off = [], []
        for n in range(200):
            noise = 1e-8 * math.sin(2 * math.pi * n / 20)
            self.on.append([n * .001, 2, 1.5, 2, 1.5, 0, 80e-6 + noise, 25])
            self.off.append([n * .001, 0, 0, 0, 0, 0, 20e-6 + noise, 25])

    def run_analysis(self):
        paths = []
        for name, rows in (("on", self.on), ("off", self.off)):
            path = self.folder / ("SYNTHETIC_" + name + ".csv")
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(list(cc.VOLTAGES[:0]) + ["time_s"] + list(cc.VOLTAGES) + ["field_t", "temperature_c"])
                writer.writerows(rows)
            paths.append(path)
            self.meta["on_record" if name == "on" else "background_record"]["sha256"] = cc.digest(path)
        meta = self.folder / "SYNTHETIC_metadata.json"
        meta.write_text(json.dumps(self.meta), encoding="utf-8")
        return cc.analyze_cc(*paths, meta)

    def test_dc_means_power_noise_and_background(self):
        report = self.run_analysis()
        self.assertAlmostEqual(report["measured_net_Bz_T"], 60e-6, places=14)
        self.assertAlmostEqual(report["on"]["signals"]["current1_a"]["mean"], .15, places=13)
        self.assertAlmostEqual(report["on"]["power"]["source1"]["mean_signed_w"], .3, places=13)
        self.assertGreater(report["on"]["signals"]["field_t"]["standard_deviation"], 0)
        self.assertEqual(report["status"], "SYNTHETIC_SOFTWARE_CHECK_ONLY")
        self.assertTrue(report["fem"]["scaling_eligible"])
        self.assertAlmostEqual(report["fem"]["center_Bz_scaled_T"], 5.77778804314748e-5, places=14)

    def test_common_field_offset_cancels_without_assumed_error_cancellation(self):
        self.meta["channels"]["field_t"].update(offset=7e-6, gain=2, noise_absolute_bound=1e-6)
        for rows in (self.on, self.off):
            for row in rows:
                row[6] = row[6] / 2 + 7e-6
        report = self.run_analysis()
        self.assertAlmostEqual(report["measured_net_Bz_T"], 60e-6, places=14)
        self.assertAlmostEqual(report["measured_Bz_absolute_bound_T"], 2e-6, places=14)

    def test_reverse_currents_and_field_keep_signed_predictions(self):
        for row in self.on:
            row[2] *= -1
            row[4] *= -1
            row[6] = -40e-6
        report = self.run_analysis()
        self.assertLess(report["v2"]["center_Bz_T"], 0)
        self.assertLess(report["fem"]["center_Bz_scaled_T"], 0)
        self.assertAlmostEqual(report["measured_net_Bz_T"], -60e-6, places=14)
        self.assertLess(report["on"]["power"]["source1"]["mean_signed_w"], 0)

    def test_unequal_currents_skip_fem(self):
        for row in self.on:
            row[4] = 1.6
        report = self.run_analysis()
        self.assertIsNone(report["fem"]["center_Bz_scaled_T"])
        self.assertFalse(report["fem"]["scaling_eligible"])

    def test_current_uncertainty_prevents_asserting_matching(self):
        self.meta["resistors"]["series1"]["absolute_bound_ohm"] = .1
        self.assertFalse(self.run_analysis()["fem"]["scaling_eligible"])

    def test_missing_metadata_rejected(self):
        del self.meta["mode"]
        with self.assertRaisesRegex(ValueError, "essenciais"):
            self.run_analysis()

    def test_mixed_origins_rejected(self):
        self.meta["background_record"]["origin"] = "EXPERIMENTAL"
        with self.assertRaisesRegex(ValueError, "mesma origem"):
            self.run_analysis()

    def test_pending_real_calibration_inconclusive(self):
        self.meta["origin"] = self.meta["on_record"]["origin"] = self.meta["background_record"]["origin"] = "EXPERIMENTAL"
        self.meta["geometry_as_built_document"] = None
        self.meta["channels"]["field_t"]["calibration_document"] = None
        report = self.run_analysis()
        self.assertEqual(report["status"], "INCONCLUSIVE")
        self.assertEqual(report["fem"]["comparison_status"], "INCONCLUSIVE")

    def test_nonzero_background_current_skips_fem(self):
        for row in self.off:
            row[2] = .1
        self.assertFalse(self.run_analysis()["fem"]["scaling_eligible"])

    def test_receiver_closed_skips_fem(self):
        self.meta["receiver_open"] = False
        self.assertIsNone(self.run_analysis()["fem"]["center_Bz_scaled_T"])

    def test_zero_net_field_is_inconclusive(self):
        self.on = copy.deepcopy(self.off)
        report = self.run_analysis()
        self.assertAlmostEqual(report["measured_net_Bz_T"], 0)
        self.assertTrue(any("Campo líquido zero" in r for r in report["inconclusive_reasons"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
