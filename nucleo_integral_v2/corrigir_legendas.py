from pathlib import Path
p=Path(__file__).resolve().parent/'laboratorio.js'
s=p.read_text(encoding='utf-8')
old="let [title,caption]=titles[t];$('view-title').firstElementChild.textContent=title;"
new="let [title,caption]=titles[t];$('stage-bottom').textContent=t==='field'?'Mapa calculado: módulo RMS vetorial; cores saturadas acima do percentil 98.':t==='energy'?'Balanço das duas portas axiais; circuito toroidal e equipamentos externos têm alimentação separada.':t==='sweep'?'Geometria fixa e fontes de tensão; a fase da corrente é calculada pelo circuito.':state.vectors?'Vetores instantâneos em t = 0; comprimento gráfico limitado.':'Dimensões propostas de bancada; não são cotas extraídas da imagem.';$('view-title').firstElementChild.textContent=title;"
s=s.replace(old,new)
s=s.replace("else renderer?.setVectors([]);", "else{renderer?.setVectors([]);$('stage-bottom').textContent='Dimensões propostas de bancada; não são cotas extraídas da imagem.';}")
p.write_text(s,encoding='utf-8')
