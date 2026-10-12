"""Validacao numerica do PI discreto; nao e validacao de firmware em hardware."""
import math
import unittest
from controlador import CurrentPI


class ControllerTests(unittest.TestCase):
    def test_exact_rl_plant_measured_resistance_mismatch(self):
        control = CurrentPI(resistance_ohm=10.7)
        current, peak = 0., 0.
        for _ in range(600):
            voltage = control.update(current, .005, True)
            # Exact sample/hold RL response, not unstable forward Euler.
            resistance, inductance = 12., .001
            alpha = math.exp(-resistance * .005 / inductance)
            current = current * alpha + voltage / resistance * (1 - alpha)
            peak = max(peak, current)
        self.assertAlmostEqual(current, .15, delta=.001)
        self.assertLess(peak, .165)

    def test_release_forces_zero_and_clears_integrator(self):
        control = CurrentPI()
        control.update(.1, .005, True)
        self.assertEqual(control.update(.1, .005, False), 0)
        self.assertEqual(control.integral, 0)

    def test_overcurrent_latches_until_operator_reset(self):
        control = CurrentPI()
        self.assertEqual(control.update(.3, .005, True), 0)
        self.assertEqual(control.update(.15, .005, True), 0)
        self.assertEqual(control.fault, 'sensor_or_overcurrent')

    def test_late_sampling_cuts_command(self):
        control = CurrentPI()
        self.assertEqual(control.update(.1, .1, True), 0)
        self.assertEqual(control.fault, 'sampling_deadline')

    def test_saturation_does_not_wind_up(self):
        control = CurrentPI(maximum_voltage_v=.1)
        for _ in range(500):
            self.assertEqual(control.update(0, .005, True), .1)
        self.assertEqual(control.integral, 0)

    def test_nan_sensor_cuts_command(self):
        control = CurrentPI()
        self.assertEqual(control.update(float('nan'), .005, True), 0)


if __name__ == '__main__':
    unittest.main()
