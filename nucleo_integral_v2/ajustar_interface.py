from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
p=ROOT/'laboratorio.js';s=p.read_text(encoding='utf-8')
s=s.replace("$('stage-title')","$('view-title')")
s=s.replace("159 elementos de referência", "160 elementos de referência")
s=s.replace('aos 80 ms','aos 400 ms')
s=s.replace("let c=P.baseline.control_cc;", "let c=P.baseline.control_cc;")
s=s.replace("if(renderer){if(state.vectors)", "if(x.temperature_c>=45){$('domain-status').textContent+=' Temperatura informada ≥45 °C: parar o ensaio físico inicial e revisar materiais.';$('domain-status').classList.add('warning');}if(x.toroid_enabled){$('domain-status').textContent+=' Campo do toroide usa espiras discretas; sua alimentação e perdas são separadas do circuito de transferência axial.';}if(renderer){if(state.vectors)")
p.write_text(s,encoding='utf-8')
p=ROOT/'index.html';s=p.read_text(encoding='utf-8').replace('<div class="stage-top">','<div class="stage-top" id="stage-top">')
p.write_text(s,encoding='utf-8')
data=json.loads((ROOT/'pesquisa/modulos.json').read_text(encoding='utf-8'))
(ROOT/'pesquisa/modulos.js').write_text('window.NUCLEO_MODULES='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';',encoding='utf-8')
