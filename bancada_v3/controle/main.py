"""MicroPython/Raspberry Pi Pico: PI DC, MCP4725 e ADC GP26.

Copiar junto com controlador.py. Padrao desarmado: preencher calibracao antes.
Somente ramo DC: capacitor contornado, receptor desconectado, gerador retirado.
Parada fisica independente obrigatoria; DAC pode reter saida se MCU travar.
"""
from machine import ADC, I2C, Pin, WDT
import time
from controlador import CurrentPI

CALIBRATION_CONFIRMED = False
ADC_REFERENCE_V = 3.3       # Substituir por medicao rastreavel
ADC_DIVIDER_RATIO = .5     # Dois resistores 10k, valor efetivo medido
ADC_ZERO_V = 0.            # Offset medido com corrente zero
SERIES_RESISTOR_OHM = 10.  # Valor do shunt medido
TOTAL_DC_RESISTANCE_OHM = 10.7
DAC_REFERENCE_V = 3.3      # Medir VDD do MCP4725
DRIVER_GAIN = 1.           # Ganho total EVM calibrado com DAC
PERIOD_US = 5000           # 200 Hz, conferir jitter no equipamento

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
adc = ADC(Pin(26))
held = Pin(15, Pin.IN, Pin.PULL_UP)  # Botao momentaneo GP15->GND: segurar para operar
led = Pin(25, Pin.OUT)
watchdog = WDT(timeout=1000)


def set_voltage(value):
    code = round(min(2.5, max(0., value)) / DRIVER_GAIN / DAC_REFERENCE_V * 4095)
    code = min(4095, max(0, code))
    # Fast-mode update, volatile; this command does not write EEPROM.
    i2c.writeto(0x60, bytes(((code >> 8) & 15, code & 255)))


set_voltage(0.)
if not CALIBRATION_CONFIRMED:
    print('DESARMADO: calibracao pendente. Nenhum controle de corrente ativo.')
    while True:
        set_voltage(0.)
        watchdog.feed()
        time.sleep_ms(100)

control = CurrentPI(resistance_ohm=TOTAL_DC_RESISTANCE_OHM)
previous, log_time = time.ticks_us(), time.ticks_ms()
print('time_ms,current_a,command_v,held,fault')
try:
    while True:
        time.sleep_us(PERIOD_US)
        now = time.ticks_us()
        dt = time.ticks_diff(now, previous) * 1e-6
        previous = now
        sensed = adc.read_u16() / 65535 * ADC_REFERENCE_V
        current = (sensed - ADC_ZERO_V) / ADC_DIVIDER_RATIO / SERIES_RESISTOR_OHM
        enabled = held.value() == 0
        voltage = control.update(current, dt, enabled)
        set_voltage(voltage)
        led.value(enabled and control.fault is None)
        watchdog.feed()
        if time.ticks_diff(time.ticks_ms(), log_time) >= 100:
            log_time = time.ticks_ms()
            print('{},{:.6f},{:.6f},{},{}'.format(log_time, current, voltage, int(enabled), control.fault or ''))
except BaseException:
    try:
        set_voltage(0.)
    finally:
        led.off()
    raise
