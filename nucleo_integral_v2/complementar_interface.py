from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parent
p=ROOT/'index.html';s=p.read_text(encoding='utf-8')
s=s.replace('O controle de amplitude é clássico; não calcula coerência quântica.','O ensaio PI de corrente DC é separado da excitação AC e não calcula coerência quântica.')
s=s.replace('<div id="control-result" class="hidden"></div>','<div id="control-result" class="hidden"></div><canvas id="control-plot" class="hidden" aria-label="Corrente simulada no ensaio separado de controle PI em DC"></canvas>')
s=s.replace('<script src="laboratorio.js"></script>','<script src="controle.js"></script><script src="laboratorio.js"></script>')
p.write_text(s,encoding='utf-8')
p=ROOT/'laboratorio.js';s=p.read_text(encoding='utf-8')
s=s.replace("Vetores do campo no pico/fase visual: direção física; comprimento gráfico limitado a 32 mm.","Vetores instantâneos em t = 0; fasores RMS convertidos ao sinal real. Comprimento gráfico limitado a 32 mm.")
s=s.replace('Campo do toroide usa espiras discretas; sua alimentação e perdas são separadas do circuito de transferência axial.','Campo do toroide usa espiras discretas; sua alimentação e perdas são separadas. Acoplamentos aos outros enrolamentos e perdas parasitas do hardware não estão incluídos.')
s=s.replace("$('control-result').classList.add('hidden');let description", "$('control-result').classList.add('hidden');$('control-plot').classList.add('hidden');let description")
s=s.replace("$('control-result').classList.remove('hidden');", "$('control-result').classList.remove('hidden');$('control-plot').classList.remove('hidden');")
s=s.replace("update();$('cycle-description').textContent=description;", "update();$('cycle-description').textContent=description;if(step===4)drawControl();")
insert="""
function drawControl(){let c=$('control-plot'),r=c.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,2);c.width=Math.round(r.width*dpr);c.height=Math.round(r.height*dpr);let g=c.getContext('2d');g.setTransform(dpr,0,0,dpr,0,0);let rows=window.NUCLEO_CONTROL||[],w=r.width,h=r.height,left=48,top=22,pw=w-75,ph=h-52;g.fillStyle='#101a28';g.fillRect(0,0,w,h);g.strokeStyle='#2f4354';g.strokeRect(left,top,pw,ph);g.strokeStyle='#6de9dd';g.lineWidth=1.6;g.beginPath();rows.forEach((row,i)=>{let x=left+row[0]/.4*pw,y=top+ph-row[1]/.17*ph;i?g.lineTo(x,y):g.moveTo(x,y);});g.stroke();g.font='10px Segoe UI';g.fillStyle='#a5b5c7';g.fillText('I / A',7,top+3);g.fillText('0,15',12,top+ph-.15/.17*ph+4);g.fillText('0',20,top+ph+3);g.fillText('0',left,top+ph+17);g.fillText('200 ms',left+pw/2-17,top+ph+17);g.fillText('400 ms',left+pw-30,top+ph+17);g.fillText('CC separado • degrau +1 Ω aos 200 ms • alvo 0,15 A',left,13);}
"""
s=s.replace('function init(){',insert+'\nfunction init(){')
p.write_text(s,encoding='utf-8')
p=ROOT/'estilo.css';s=p.read_text(encoding='utf-8')
s+='\n#control-plot{grid-column:1/-1;height:150px;width:100%;border:1px solid var(--line);border-radius:5px;}\n'
p.write_text(s,encoding='utf-8')
with (ROOT/'simulacao/outputs/controle_cc.csv').open(encoding='utf-8') as f:
    data=list(csv.DictReader(f))
stride=max(1,len(data)//1000)
rows=[[float(row['time_s']),float(row['current_A'])] for row in data[::stride]]
if rows[-1][0]!=float(data[-1]['time_s']):rows.append([float(data[-1]['time_s']),float(data[-1]['current_A'])])
(ROOT/'controle.js').write_text('window.NUCLEO_CONTROL='+json.dumps(rows,separators=(',',':'))+';',encoding='utf-8')
modules=json.loads((ROOT/'pesquisa/modulos.json').read_text(encoding='utf-8'))
(ROOT/'pesquisa/modulos.js').write_text('window.NUCLEO_MODULES='+json.dumps(modules,ensure_ascii=False,separators=(',',':'))+';',encoding='utf-8')
