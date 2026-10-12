"""Verifica a aplicação 3D local e suas interações. Não é teste físico."""
from pathlib import Path
import json
import math
import sys
from playwright.sync_api import sync_playwright
from browser_runtime import launch_browser

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'simulacao'))
import modelo_integral as physics

def main():
    checks=[]
    def check(name,condition,**evidence):
        checks.append({'name':name,'passed':bool(condition),**evidence})
        assert condition,name
    with sync_playwright() as p:
        browser=launch_browser(p,headless=True,args=['--enable-unsafe-swiftshader'])
        page=browser.new_page(viewport={'width':1540,'height':1120},device_scale_factor=1)
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto((ROOT/'index.html').as_uri())
        page.wait_for_function('window.integralLab && integralLab.result')
        scene=json.loads((ROOT/'cad/scene.json').read_text(encoding='utf-8'))
        count=page.evaluate('integralLab.renderer?.parts.length || 0')
        check('all_cad_parts_renderable',count==len(scene['parts']),parts=count)
        check('webgl_active',page.evaluate('!!integralLab.renderer.gl && integralLab.renderer.gl.getError()===0'))
        cfg=physics.load_config();pr=physics.parameters(cfg);sol=physics.circuit_solution(cfg,pr)
        r=page.evaluate('integralLab.result')
        for i in range(3):
            relative_error=abs(r['currents'][i]['rms']-sol['currents'][i]['rms'])/sol['currents'][i]['rms']
            check('current_python_js_'+str(i),relative_error<1e-10,relative_error=relative_error)
        check('power_balance',abs(r['power']['balance_residual_w'])<1e-10)
        pixels=page.evaluate('''()=>{let gl=integralLab.renderer.gl, data=new Uint8Array(gl.drawingBufferWidth*gl.drawingBufferHeight*4);gl.readPixels(0,0,gl.drawingBufferWidth,gl.drawingBufferHeight,gl.RGBA,gl.UNSIGNED_BYTE,data);let count=0;for(let i=3;i<data.length;i+=4)if(data[i]>200)count++;return count;}''')
        check('actual_3d_pixels',pixels>5000,opaque_pixels=pixels)
        page.screenshot(path=str(ROOT/'Previa_Laboratorio.png'),full_page=True)
        page.locator('#stage').screenshot(path=str(ROOT/'Montagem_Integral.png'))
        page.locator('#explode').click();check('exploded_state',page.evaluate('integralLab.renderer.exploded'))
        page.locator('#stage').screenshot(path=str(ROOT/'Montagem_Explodida.png'))
        page.locator('#explode').click();page.locator('#open-shell').click();check('open_shell',page.evaluate('integralLab.renderer.open'))
        page.locator('#stage').screenshot(path=str(ROOT/'Montagem_Aberta.png'))
        page.locator('#open-shell').click()
        page.locator('#vectors').click();check('calculated_vector_geometry',page.evaluate('integralLab.renderer.vectorLines.length')>30)
        page.locator('#vectors').click()
        page.locator('#part-select').select_option('column');check('column_limit_explained','não é vaso de pressão' in page.locator('#part-description').inner_text() or 'não é' in page.locator('#part-description').inner_text())
        page.locator('#phase').fill('180');page.locator('#phase').dispatch_event('input');check('opposed_phase_cancels',page.evaluate('integralLab.centerField.rms_norm_t')<1e-9)
        page.locator('#reset').click()
        page.locator('#receiverEnabled').uncheck();check('open_receiver_zero_load',page.evaluate('integralLab.result.power.receiver_load_w')==0)
        page.locator('#receiverEnabled').check()
        page.locator('#toroidEnabled').check();check('actual_toroid_field',page.evaluate('NucleoPhysics.torusFieldAt([.135,0,.125],integralLab.input()).rms_norm_t')>1e-6)
        page.locator('#vectors').click();check('toroid_vector_points',page.evaluate('integralLab.renderer.vectorLines.length')>135)
        page.locator('#vectors').click();page.locator('#toroidEnabled').uncheck()
        page.locator('[data-tab=field]').click();check('field_view',page.locator('#plot').is_visible())
        page.locator('#stage').screenshot(path=str(ROOT/'Mapa_Campo_Integral.png'))
        page.locator('[data-tab=energy]').click();page.locator('#stage').screenshot(path=str(ROOT/'Balanco_Energia.png'))
        page.locator('[data-tab=sweep]').click();page.locator('#tune').click();check('peak_tuned',1450<page.evaluate('integralLab.input().frequency_hz')<1550)
        page.locator('[data-tab=tests]').click();page.locator('#run-tests').click();check('scenario_controls',page.evaluate('integralLab.state.controlsRun.every(t=>t[1])'))
        for step in range(1,6):
            page.locator('[data-step="'+str(step)+'"]').click()
            check('cycle_step_'+str(step),len(page.locator('#cycle-description').inner_text())>50)
            if step==4:
                check('separate_dc_control_chart',page.locator('#control-plot').is_visible())
                page.locator('#cycle-description').screenshot(path=str(ROOT/'Controle_CC_Descricao.png'))
        page.locator('#reset').click();page.locator('[data-tab=tests]').click()
        with page.expect_download() as d:
            page.locator('#template').click()
        dest=ROOT/'Modelo_Medicoes.csv';d.value.save_as(dest)
        check('empty_measurement_template',len(dest.read_text(encoding='utf-8-sig').splitlines())==1)
        baseline=json.loads((ROOT/'simulacao/outputs/baseline.json').read_text(encoding='utf-8'))
        row=[1400,2,2,0,100,1,20,sol['currents'][0]['rms'],sol['currents'][1]['rms'],baseline['center_field']['magnitude_rms_t']*1e6,sol['power']['source_total_w'],sol['power']['receiver_load_w']]
        # Fixture synthetic for QA only; never distributed as experimental evidence.
        csv=dest.read_text(encoding='utf-8-sig')+';'.join(map(str,row))+'\n'
        page.locator('#measurement-file').set_input_files({'name':'fixture_QA.csv','mimeType':'text/csv','buffer':csv.encode()})
        page.wait_for_function('integralLab.state.measurements.length===1')
        check('measurement_import', 'corrente 0,000 mA; campo 0,000 µT' in page.locator('#measurement-results').inner_text())
        bad=page.evaluate('''text=>{try {integralLab.parseMeasurements(text);return false;}catch{return true;}}''','a;b\n1;2')
        check('reject_bad_csv',bad)
        page.locator('[data-tab=hypotheses]').click();check('unresolved_claims_explicit',page.locator('#hypothesis-list .hipotese_sem_modelo').count()>=4)
        page.locator('[data-tab=assembly]').click();page.locator('#part-select').select_option('lower_coil')
        page.locator('#voltageLower').fill('0');page.locator('#voltageLower').dispatch_event('input');page.locator('#voltageUpper').fill('0');page.locator('#voltageUpper').dispatch_event('input')
        check('zero_drive_no_generated_power',abs(page.evaluate('integralLab.result.power.source_total_w'))<1e-12)
        page.locator('#reset').click()
        with page.expect_download() as d:
            page.locator('#export').click()
        dest=ROOT/'simulacao/outputs/cenario_exportado_browser.json';d.value.save_as(dest)
        export=json.loads(dest.read_text(encoding='utf-8-sig'));check('scenario_export',export['input']['frequency_hz']==1400)
        for width in [390,768]:
            page.set_viewport_size({'width':width,'height':900})
            check('no_horizontal_overflow_'+str(width),not page.evaluate('document.documentElement.scrollWidth>innerWidth'))
        page.set_viewport_size({'width':1540,'height':1120})
        check('no_javascript_errors',not errors,errors=errors)
        page.set_viewport_size({'width':1200,'height':710})
        page.goto((ROOT/'circuito_integral.svg').as_uri())
        page.screenshot(path=str(ROOT/'Circuito_Integral.png'))
        browser.close()
    results={'scope':'QA de navegador e concordância com modelo; nenhum ensaio físico','all_passed':all(c['passed'] for c in checks),'check_count':len(checks),'checks':checks}
    (ROOT/'validacao_navegador.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'passed':results['all_passed'],'checks':len(checks)}))

if __name__=='__main__':main()
