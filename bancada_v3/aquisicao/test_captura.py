"""Testes de unidades/contratos de captura; nao substituem teste com PicoScope."""
import csv
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from capturar_pico import plan, adc_volts, write_capture


class CaptureContracts(unittest.TestCase):
    def test_common_clock_baseline_contains_140_cycles(self):
        timebase, count = plan()
        self.assertEqual(timebase, 79)
        self.assertAlmostEqual(count * (timebase + 1) * 12.5e-9 * 1400, 140)

    def test_signed_adc_uses_driver_maximum_not_12bit_literal(self):
        self.assertAlmostEqual(adc_volts(-16380, 10, 32760), -5)
        self.assertAlmostEqual(adc_volts(16380, .2, 32760), .1)

    def test_refuses_nonfinite_parameters(self):
        for sample_rate, duration in [(float('nan'), .1), (500000, float('inf')), (500000, 0), (-1, .1)]:
            with self.assertRaises(ValueError):
                plan(sample_rate, duration)

    def test_bounded_memory_and_duration(self):
        for sample_rate, duration in [(1e8, 1), (500000, 6), (1000000, 2)]:
            with self.assertRaises(ValueError):
                plan(sample_rate, duration)

    def test_export_preserves_channel_polarity_time_and_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'fixture'
            # Synthetic unit-test fixture only, kept outside repository/publication.
            data = [[-10, 0, 10], [20, 0, -20], [30, 0, -30], [-40, 0, 40], [50, 0, -50]]
            record = write_capture(target, data, 2e-6, 100, {'model': 'SYNTHETIC_TEST_NOT_HARDWARE'}, origin='SYNTHETIC')
            with (target / 'formas_onda.csv').open() as stream:
                rows = list(csv.DictReader(stream, delimiter=','))
            self.assertEqual(len(rows), 3)
            self.assertAlmostEqual(float(rows[0]['v_series1_v']), 2)
            self.assertAlmostEqual(float(rows[2]['v_source1_v']), 1)
            self.assertAlmostEqual(float(rows[0]['v_load_v']), .1)
            self.assertAlmostEqual(float(rows[2]['time_s']), 4e-6)
            self.assertEqual(record['scientific_validation'], 'NOT_PERFORMED')
            self.assertEqual(record['origin'], 'SYNTHETIC')
            self.assertEqual(len(record['csv_sha256']), 64)
            self.assertEqual(json.loads((target / 'captura.json').read_text())['capture_id'], record['capture_id'])

    def test_existing_data_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                write_capture(temp, [[1]] * 5, 1e-6, 100, {}, origin='SYNTHETIC')

    def test_incomplete_channels_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            for data in ([[1]] * 4, [[], [], [], [], []], [[1, 2], [1], [1], [1], [1]]):
                with self.assertRaises(ValueError):
                    write_capture(Path(temp) / 'new', data, 1e-6, 100, {}, origin='SYNTHETIC')

    def test_experimental_without_device_provenance_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                write_capture(Path(temp) / 'new', [[1]] * 5, 1e-6, 100, {}, origin='EXPERIMENTAL')
            self.assertFalse((Path(temp) / 'new').exists())

    def test_clipping_rejected_before_creating_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                write_capture(Path(temp) / 'new', [[100]] * 5, 1e-6, 100, {}, origin='SYNTHETIC')
            self.assertFalse((Path(temp) / 'new').exists())

    def test_eight_channels_sensor_conversion_preserves_raw(self):
        with tempfile.TemporaryDirectory() as temp:
            data = [[1, 2]] * 5 + [[60, 60], [50, 50], [25, 25]]
            target = Path(temp) / 'new'
            record = write_capture(target, data, 1e-6, 100, {}, origin='SYNTHETIC',
                          field_sensitivity_v_t=5000, temperature_sensitivity_v_c=.01)
            with (target / 'formas_onda.csv').open() as stream:
                row = next(csv.DictReader(stream))
            self.assertAlmostEqual(float(row['field_t']), 1e-4)
            self.assertAlmostEqual(float(row['temperature_c']), 25)
            self.assertTrue((target / 'canais_sensores_brutos.csv').exists())
            self.assertEqual(record['sensor_raw_csv_sha256'], hashlib.sha256((target / 'canais_sensores_brutos.csv').read_bytes()).hexdigest())

    def test_capture_csv_is_consumed_by_scientific_reader(self):
        import importlib.util
        reader_path = Path(__file__).resolve().parents[1] / 'medicoes' / 'analisar.py'
        spec = importlib.util.spec_from_file_location('scientific_reader_contract', reader_path)
        reader = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(reader)
        with tempfile.TemporaryDirectory() as temp:
            for sensors in (False, True):
                target = Path(temp) / str(sensors)
                data = [[1] * 100 for _ in range(8 if sensors else 5)]
                write_capture(target, data, 1e-6, 100, {}, origin='SYNTHETIC',
                              field_sensitivity_v_t=4880, temperature_sensitivity_v_c=.01)
                columns = reader.read_waveforms(target / 'formas_onda.csv')
                self.assertEqual(len(columns['time_s']), 100)
                self.assertAlmostEqual(columns['v_source1_v'][0], .1)
                self.assertEqual('field_t' in columns, sensors)


if __name__ == '__main__':
    unittest.main()
