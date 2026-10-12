"""PI DC discreto com anti-windup. Unidades SI; separado do circuito AC."""
import math


class CurrentPI:
    def __init__(self, resistance_ohm=10.7, kp_ohm=2., ki_ohm_per_s=20.,
                 target_a=.15, maximum_voltage_v=2.5, trip_current_a=.25):
        values = (resistance_ohm, kp_ohm, ki_ohm_per_s, target_a, maximum_voltage_v, trip_current_a)
        if not all(math.isfinite(v) and v > 0 for v in values) or target_a > .2:
            raise ValueError('Parametros PI invalidos')
        self.resistance, self.kp, self.ki = resistance_ohm, kp_ohm, ki_ohm_per_s
        self.target, self.maximum, self.trip = target_a, maximum_voltage_v, trip_current_a
        self.integral, self.fault = 0., None

    def update(self, current_a, dt_s, enabled):
        if self.fault:
            return 0.
        if not math.isfinite(current_a) or current_a < -.01 or current_a > self.trip:
            self.fault = 'sensor_or_overcurrent'
            self.integral = 0.
            return 0.
        if not math.isfinite(dt_s) or not .001 <= dt_s <= .025:
            self.fault = 'sampling_deadline'
            self.integral = 0.
            return 0.
        if not enabled:
            self.integral = 0.
            return 0.
        error = self.target - current_a
        candidate = self.integral + self.ki * dt_s * error
        raw = self.resistance * self.target + self.kp * error + candidate
        # Integrate when unsaturated or when the error unwinds saturation.
        if 0 <= raw <= self.maximum or (raw > self.maximum and error < 0) or (raw < 0 and error > 0):
            self.integral = candidate
        return min(self.maximum, max(0., self.resistance * self.target + self.kp * error + self.integral))
