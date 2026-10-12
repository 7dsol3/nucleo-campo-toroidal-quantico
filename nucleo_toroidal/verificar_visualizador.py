"""QA do artefato local com Chrome instalado. Não executa experimento físico."""
from pathlib import Path
import json
import re
import sys
from playwright.sync_api import sync_playwright
from browser_runtime import launch_browser

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'simulacao'))
import modelo

def main():
    cfg = modelo.load_config()
    reference = modelo.operating_point(cfg)
    params = modelo.circuit_parameters(cfg)
    result = {'scope': 'Browser QA and comparison against Python classical model; no physical experiment.', 'checks': []}
    def check(name, condition, **details):
        result['checks'].append({'name': name, 'passed': bool(condition), **details})
        assert condition, name
    with sync_playwright() as p:
        browser = launch_browser(p, headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 1050}, device_scale_factor=1)
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto((ROOT/'index.html').as_uri())
        page.wait_for_function('window.lab && window.lab.circuit().I > 0')
        actual = page.evaluate('lab.circuit()')
        comparisons = {'I': reference['current_rms_a'], 'b': reference['center_field_rms_t'], 'power': reference['input_real_power_w'], 'f0': params['resonance_frequency_hz'], 'L': params['series_inductance_h'], 'Rcu': params['copper_resistance_dc_ohm_total']}
        for name, wanted in comparisons.items():
            err = abs(actual[name]-wanted)/abs(wanted)
            check('python_js_'+name, err < 1e-10, relative_error=err, value=actual[name])
        exact = page.evaluate('lab.axial(0, .25)')
        numeric = page.evaluate('lab.field(0,0,.25)[1]')
        check('biot_savart_center', abs(exact-numeric)/exact<1e-10)
        for x,z in [(0.03,0.02),(0.11,0.06),(0.08,-0.03)]:
            bx,by,bz = modelo.pair_field_t(cfg,.25,(x,0,z))
            b_browser=page.evaluate('([x,z])=>lab.field(x,z,.25)',[x,z])
            err=((b_browser[0]-bx)**2+(b_browser[1]-bz)**2)**.5/(bx*bx+bz*bz)**.5
            check('field_python_js_'+str((x,z)),err<2e-5,relative_error=err)
        before = page.locator('#detail-title').inner_text()
        page.locator('#explode').click()
        check('exploded_view', page.evaluate('lab.state.explode') is True)
        page.locator('#explode').click()
        page.screenshot(path=str(ROOT/'Apercu_3D.png'), full_page=True)
        page.locator('#stage').screenshot(path=str(ROOT/'Montagem_3D.png'))
        page.locator('[data-tab=field]').click()
        check('field_tab', page.locator('#view2d').is_visible())
        page.screenshot(path=str(ROOT/'Apercu_Campo.png'), full_page=True)
        page.locator('#stage').screenshot(path=str(ROOT/'Mapa_Campo.png'))
        page.locator('[data-tab=sweep]').click()
        page.locator('#resonance').click()
        peak = page.evaluate('lab.circuit()')
        check('resonance_preset', abs(peak['f0']-page.evaluate('lab.state.frequency'))<=.5)
        check('resonance_current', peak['I']>actual['I'])
        page.locator('#voltage').fill('0')
        page.locator('#voltage').dispatch_event('input')
        check('source_zero', page.evaluate('lab.circuit().I')==0)
        page.locator('#reset').click()
        with page.expect_download() as download:
            page.locator('#export').click()
        exported = download.value
        dest = ROOT/'simulacao'/'resultados'/'previsao_exportada_browser.csv'
        exported.save_as(dest)
        check('csv_export', len(dest.read_text(encoding='utf-8-sig').splitlines())==492)
        # Synthetic fixture strictly for testing import, never used as experiment evidence.
        fixture = 'frequency_hz;source_rms_v;current_rms_a;B_center_rms_uT;u_B_uT\n1000;2;'+str(actual['I'])+';'+str(actual['b']*1e6)+';1\n'
        page.locator('#measurements').set_input_files({'name':'fixture_qa.csv','mimeType':'text/csv','buffer':fixture.encode()})
        page.wait_for_function('lab.state.measurements.length === 1')
        status = page.locator('#measurement-status').inner_text()
        check('csv_import', status.count('0,0%')==2, status=status)
        normalized_points = page.evaluate('''()=>{
            const m=lab.state.measurements[0];
            lab.state.measurements.push({...m,source_rms_v:m.source_rms_v/2,current_rms_a:m.current_rms_a/2,B_center_rms_uT:m.B_center_rms_uT/2});
            const context=document.getElementById('view2d').getContext('2d');
            const original=context.arc,points=[];
            context.arc=function(x,y,r,...rest){if(r===4)points.push([x,y]);return original.call(this,x,y,r,...rest);};
            try {lab.update();} finally {context.arc=original;}
            return points.slice(-2);
        }''')
        check('measurement_voltage_normalization',len(normalized_points)==2 and abs(normalized_points[0][1]-normalized_points[1][1])<1e-10)
        parsed = page.evaluate("lab.parseMeasurements('frequency_hz;source_rms_v;current_rms_a;B_center_rms_uT\\n1000;2,0;0,17;78,0')")
        check('csv_decimal_comma', parsed[0]['source_rms_v']==2 and parsed[0]['current_rms_a']==.17)
        invalid = page.evaluate("(()=>{try {lab.parseMeasurements('frequency_hz;source_rms_v;current_rms_a;B_center_rms_uT\\n1000;2;-1;78');return false;}catch{return true;}})()")
        check('csv_reject_negative', invalid)
        page.evaluate('lab.state.measurements=[]')
        page.locator('[data-tab=build]').click()
        check('parts_tab', page.locator('#build').is_visible())
        for viewport in [{'width':390,'height':844},{'width':768,'height':1024}]:
            page.set_viewport_size(viewport)
            page.locator('[data-tab=model]').click()
            overflow=page.evaluate('document.documentElement.scrollWidth>window.innerWidth')
            check('responsive_'+str(viewport['width']), not overflow)
        page.set_viewport_size({'width':1440,'height':1050})
        page.locator('[data-tab=model]').click()
        page.mouse.move(800,400)
        page.mouse.down()
        page.mouse.move(880,430,steps=5)
        page.mouse.up()
        check('rotate_3d', abs(page.evaluate('lab.state.yaw')+.60)>.1)
        page.locator('#home-view').click()
        page.locator('#reset').click()
        check('no_browser_errors', not errors, errors=errors)
        page.set_viewport_size({'width':1100,'height':470})
        page.goto((ROOT/'circuito_ensaio.svg').as_uri())
        page.screenshot(path=str(ROOT/'Circuito_Ensaio.png'))
        browser.close()
    result['check_count']=len(result['checks'])
    result['all_passed']=all(c['passed'] for c in result['checks'])
    (ROOT/'validacao_visualizador.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'all_passed':result['all_passed'],'checks':result['check_count']}))

if __name__=='__main__':
    main()
