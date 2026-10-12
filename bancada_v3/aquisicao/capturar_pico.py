"""Captura passiva real de cinco canais PicoScope 4824/4824A via PicoSDK.

Nao comanda gerador, fonte ou amplificador. Sem SDK/dispositivo, falha sem criar
medicoes. ctypes stdlib; assinaturas conferidas no guia oficial ps4000a.
"""
from __future__ import annotations

import argparse
import csv
import ctypes as ct
import ctypes.util
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import time
import uuid

CHANNELS = ('v_source1_v', 'v_series1_v', 'v_source2_v', 'v_series2_v', 'v_load_v')
SENSOR_CHANNELS = ('field_sensor_out_v', 'field_sensor_ref_v', 'temperature_sensor_v')
# PicoSDK PS4000A_RANGE: A-D +/-10V, E +/-200mV, pontas 1:1.
RANGES = ((9, 10.0), (9, 10.0), (9, 10.0), (9, 10.0), (4, .2), (8, 5.), (8, 5.), (6, 1.))


def plan(sample_rate_hz=1000000, duration_s=.1):
    if not all(math.isfinite(v) and v > 0 for v in (sample_rate_hz, duration_s)):
        raise ValueError('Taxa e duracao precisam ser positivas e finitas')
    if not 100000 <= sample_rate_hz <= 1000000 or duration_s > 5:
        raise ValueError('Envelope desta ferramenta: 100k-1M S/s, ate 5s')
    timebase = max(0, round(80e6 / sample_rate_hz) - 1)
    dt = 12.5e-9 * (timebase + 1)
    samples = round(duration_s / dt)
    if not 100 <= samples <= 1000000:
        raise ValueError('Solicite entre 100 e 1.000.000 amostras por canal')
    return timebase, samples


def adc_volts(code, full_scale_v, max_adc):
    if max_adc <= 0 or not math.isfinite(full_scale_v) or full_scale_v <= 0:
        raise ValueError('Escala ADC invalida')
    return int(code) * full_scale_v / max_adc


class Pico:
    def __init__(self, library_path=None):
        loader = ct.WinDLL if os.name == 'nt' else ct.CDLL
        candidates = [str(library_path)] if library_path else [
            ctypes.util.find_library('ps4000a'),
            r'C:\Program Files\Pico Technology\SDK\lib\ps4000a.dll' if os.name == 'nt' else 'libps4000a.so',
            'ps4000a.dll' if os.name == 'nt' else 'libps4000a.dylib',
        ]
        self.lib = None
        for candidate in filter(None, candidates):
            try:
                self.lib = loader(candidate)
                break
            except OSError:
                pass
        if self.lib is None:
            raise RuntimeError('PicoSDK ps4000a ausente. Instale o driver oficial compativel com Python 64 bits; nenhuma captura foi criada.')
        i16, i32, u32, ptr = ct.c_int16, ct.c_int32, ct.c_uint32, ct.c_void_p
        signatures = {
            'OpenUnit': [ptr, ct.c_char_p], 'CloseUnit': [i16],
            'GetUnitInfo': [i16, ptr, i16, ptr, u32],
            'SetChannel': [i16, i32, i16, i32, i32, ct.c_float],
            'GetTimebase2': [i16, u32, i32, ptr, ptr, u32],
            'MaximumValue': [i16, ptr],
            'SetDataBuffer': [i16, i32, ptr, i32, u32, i32],
            'SetSimpleTrigger': [i16, i16, i32, i16, i32, u32, i16],
            'RunBlock': [i16, i32, i32, u32, ptr, u32, ptr, ptr],
            'IsReady': [i16, ptr], 'GetValues': [i16, u32, ptr, u32, i32, u32, ptr],
            'Stop': [i16],
        }
        for name, argtypes in signatures.items():
            function = getattr(self.lib, 'ps4000a' + name)
            function.argtypes, function.restype = argtypes, u32
        self.handle = i16()

    def call(self, name, *args):
        status = getattr(self.lib, 'ps4000a' + name)(*args)
        if status:
            raise RuntimeError(f'PicoSDK {name}: status 0x{int(status):08x}; captura recusada')

    def info(self, info_id):
        text = ct.create_string_buffer(256)
        required = ct.c_int16()
        self.call('GetUnitInfo', self.handle, text, len(text), ct.byref(required), info_id)
        return text.value.decode('utf-8', errors='replace')

    def __enter__(self):
        try:
            self.call('OpenUnit', ct.byref(self.handle), None)
            self.model = self.info(3)  # PICO_VARIANT_INFO
            self.serial = self.info(4)  # PICO_BATCH_AND_SERIAL
            if self.model not in ('4824', '4824A'):
                raise RuntimeError('Este mapeamento exige PicoScope 4824 ou 4824A; dispositivo encontrado: ' + self.model)
        except Exception:
            self.__exit__(None, None, None)
            raise
        return self

    def __exit__(self, *_):
        if self.handle.value:
            # Stop/Close must run even when capture fails; preserve original error.
            try:
                self.lib.ps4000aStop(self.handle)
            finally:
                self.lib.ps4000aCloseUnit(self.handle)
                self.handle.value = 0

    def capture(self, sample_rate_hz, duration_s, timeout_s=15, sensors=False):
        timebase, count = plan(sample_rate_hz, duration_s)
        channel_count = 8 if sensors else 5
        for channel in range(8):
            range_id = RANGES[channel][0]
            self.call('SetChannel', self.handle, channel, int(channel < channel_count), 1, range_id, 0.)
        interval, capacity = ct.c_float(), ct.c_int32()
        self.call('GetTimebase2', self.handle, timebase, count, ct.byref(interval), ct.byref(capacity), 0)
        if capacity.value < count or not math.isfinite(interval.value) or interval.value <= 0:
            raise RuntimeError('Driver nao confirmou capacidade/intervalo solicitado')
        maximum = ct.c_int16()
        self.call('MaximumValue', self.handle, ct.byref(maximum))
        if maximum.value <= 0:
            raise RuntimeError('Driver retornou escala ADC invalida')
        buffers = [(ct.c_int16 * count)() for _ in range(channel_count)]
        for channel, buffer in enumerate(buffers):
            self.call('SetDataBuffer', self.handle, channel, buffer, count, 0, 0)
        # Free-running block; a common timebase for all five channels, no output.
        self.call('SetSimpleTrigger', self.handle, 0, 0, 0, 2, 0, 0)
        indisposed_ms = ct.c_int32()
        self.call('RunBlock', self.handle, 0, count, timebase, ct.byref(indisposed_ms), 0, None, None)
        deadline, ready = time.monotonic() + timeout_s, ct.c_int16()
        while not ready.value:
            self.call('IsReady', self.handle, ct.byref(ready))
            if time.monotonic() > deadline:
                raise TimeoutError('Aquisicao nao terminou; nenhum CSV foi gravado')
            if not ready.value:
                time.sleep(.01)
        received, overflow = ct.c_uint32(count), ct.c_int16()
        self.call('GetValues', self.handle, 0, ct.byref(received), 1, 0, 0, ct.byref(overflow))
        if overflow.value:
            raise RuntimeError('Saturacao de entrada detectada; reduza ganho/ajuste faixa e repita. CSV recusado.')
        if received.value != count:
            raise RuntimeError('Captura incompleta; CSV recusado')
        if any(abs(value) >= maximum.value for buffer in buffers for value in buffer):
            raise RuntimeError('Amostra no limite ADC; CSV recusado')
        return buffers, interval.value * 1e-9, maximum.value, timebase


def write_capture(directory, buffers, dt, maximum, instrument, *, origin,
                  field_sensitivity_v_t=None, temperature_sensitivity_v_c=None):
    directory = Path(directory)
    if directory.exists():
        raise ValueError('Escolha uma pasta nova; capturas anteriores nunca sao sobrescritas')
    if origin not in ('EXPERIMENTAL', 'SYNTHETIC'):
        raise ValueError('Origem obrigatoria: EXPERIMENTAL ou SYNTHETIC')
    if len(buffers) not in (5, 8) or not buffers[0] or len({len(b) for b in buffers}) != 1:
        raise ValueError('Captura exige cinco ou oito buffers simultaneos do mesmo comprimento')
    if not math.isfinite(dt) or dt <= 0 or maximum <= 0:
        raise ValueError('Intervalo/escala invalido')
    if origin == 'EXPERIMENTAL' and (
        instrument.get('model') not in ('4824', '4824A') or not instrument.get('serial')
        or instrument.get('sdk_capture_completed') is not True
    ):
        raise ValueError('Captura experimental exige modelo, serial e conclusao do driver')
    if any(abs(value) >= maximum for buffer in buffers for value in buffer):
        raise ValueError('Codigo ADC no limite ou fora da faixa; nao gravar clipping como valido')
    sensors = len(buffers) == 8
    if sensors and not all(isinstance(v, (int, float)) and math.isfinite(v) and v > 0
                           for v in (field_sensitivity_v_t, temperature_sensitivity_v_c)):
        raise ValueError('Oito canais exigem sensibilidades explicitas e positivas dos sensores')
    directory.mkdir(parents=True)
    target = directory / 'formas_onda.csv'
    with target.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.writer(stream, delimiter=',')
        writer.writerow(('time_s', *CHANNELS, *(('temperature_c', 'field_t') if sensors else ())))
        for index in range(len(buffers[0])):
            volts = [adc_volts(buffer[index], scale, maximum) for buffer, (_, scale) in zip(buffers, RANGES)]
            row = [index * dt, *volts[:5]]
            if sensors:
                row.extend((volts[7] / temperature_sensitivity_v_c,
                            (volts[5] - volts[6]) / field_sensitivity_v_t))
            writer.writerow([format(value, '.12g') for value in row])
    if sensors:
        with (directory / 'canais_sensores_brutos.csv').open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(('time_s', *SENSOR_CHANNELS))
            for index in range(len(buffers[0])):
                writer.writerow([format(index * dt, '.12g'), *[
                    format(adc_volts(buffers[ch][index], RANGES[ch][1], maximum), '.12g')
                    for ch in range(5, 8)
                ]])
    record = {
        'record_type': 'instrument_capture', 'origin': origin,
        'capture_id': str(uuid.uuid4()), 'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'instrument': instrument, 'software': 'capturar_pico.py v3',
        'samples_per_channel': len(buffers[0]), 'sample_interval_s': dt,
        'sample_rate_hz': 1 / dt, 'common_timebase': True,
        'range_full_scale_v': {name: scale for name, (_, scale) in zip(CHANNELS + SENSOR_CHANNELS if sensors else CHANNELS, RANGES)},
        'probe_attenuation': 1, 'adc_maximum': maximum,
        'csv_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
        'sensor_raw_csv_sha256': hashlib.sha256((directory / 'canais_sensores_brutos.csv').read_bytes()).hexdigest() if sensors else None,
        'clipping_detected': False,
        'calibration_status': 'PENDING_OPERATOR_RECORD',
        'scientific_validation': 'NOT_PERFORMED',
        'sensor_scaling': {'field_sensitivity_v_t': field_sensitivity_v_t,
                           'temperature_sensitivity_v_c': temperature_sensitivity_v_c,
                           'calibration_verified': False},
        'note': 'Captura nao implica calibracao, estacionariedade, conexoes corretas ou concordancia fisica. Complete metadados cientificos separados.',
    }
    (directory / 'captura.json').write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding='utf-8')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--biblioteca', type=Path, help='Caminho da biblioteca oficial ps4000a, opcional')
    parser.add_argument('--diagnostico', action='store_true', help='Identificar equipamento e fechar; nao captura')
    parser.add_argument('--output', type=Path, help='Pasta NOVA para CSV e registro de captura real')
    parser.add_argument('--sample-rate', type=float, default=1000000)
    parser.add_argument('--duration', type=float, default=.1)
    parser.add_argument('--sensores', action='store_true', help='Oito canais: DRV425EVM F/G e LM35 H')
    parser.add_argument('--field-sensitivity', type=float, help='Sensibilidade explicitada V/T; nominal DRV425EVM=4880, ainda exige calibracao')
    parser.add_argument('--temperature-sensitivity', type=float, help='V/degC; nominal LM35=0.01, ainda exige calibracao')
    args = parser.parse_args()
    try:
        if not args.diagnostico:
            if args.output is None:
                raise ValueError('--output PASTA_NOVA obrigatorio para capturar')
            if args.output.exists():
                raise ValueError('Pasta de captura ja existe; escolha outra')
            if args.sensores and not all(v is not None and math.isfinite(v) and v > 0
                                         for v in (args.field_sensitivity, args.temperature_sensitivity)):
                raise ValueError('--sensores exige --field-sensitivity e --temperature-sensitivity positivos')
            plan(args.sample_rate, args.duration)
        with Pico(args.biblioteca) as scope:
            instrument = {'manufacturer': 'Pico Technology', 'model': scope.model, 'serial': scope.serial}
            if args.diagnostico:
                print(json.dumps({'device_connected': True, 'instrument': instrument, 'capture_performed': False}))
                return 0
            buffers, dt, maximum, timebase = scope.capture(args.sample_rate, args.duration, sensors=args.sensores)
            record = write_capture(args.output, buffers, dt, maximum,
                                   {**instrument, 'timebase': timebase, 'sdk_capture_completed': True},
                                   origin='EXPERIMENTAL', field_sensitivity_v_t=args.field_sensitivity,
                                   temperature_sensitivity_v_c=args.temperature_sensitivity)
            print(json.dumps({'captured': True, 'origin': record['origin'], 'samples_per_channel': record['samples_per_channel'], 'output': str(args.output)}))
            return 0
    except (OSError, RuntimeError, ValueError, TimeoutError, AttributeError) as error:
        print(json.dumps({'captured': False, 'reason': str(error), 'physical_validation': False}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
