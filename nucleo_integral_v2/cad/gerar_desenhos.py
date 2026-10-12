"""Desenhos dimensionais em SVG: abrir em navegador ou importar em CAD."""
from pathlib import Path
import math, json
OUT=Path(__file__).resolve().parent
P=json.loads((OUT/'parametros.json').read_text(encoding='utf-8'))
BASE='''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1200" viewBox="0 0 1600 1200">
<defs><marker id="a" markerWidth="7" markerHeight="7" refX="3.5" refY="3.5" orient="auto-start-reverse"><path d="M0 0L7 3.5L0 7" fill="#0a7187"/></marker></defs>
<style>text{font:17px Arial;fill:#21303b}.title{font-size:27px;font-weight:bold}.sub{font-size:20px;font-weight:bold}.tiny{font-size:14px}.part{fill:#e5edf2;stroke:#40586a;stroke-width:1.5}.coil{fill:#d78c52;stroke:#8d4a18;stroke-width:1.5}.line{fill:none;stroke:#6c8798;stroke-width:1.2;stroke-dasharray:5 4}.dim{fill:none;stroke:#0a7187;stroke-width:1.2;marker-start:url(#a);marker-end:url(#a)}.tube{fill:#8dd8e1;fill-opacity:.4;stroke:#0a7187;stroke-width:1.5}</style>
<rect width="1600" height="1200" fill="#fff"/>
'''
class SVG:
    def __init__(self,title):self.s=[BASE];self.text(35,42,title,'title')
    def text(self,x,y,t,cls=''):self.s.append(f'<text x="{x}" y="{y}" class="{cls}">{t}</text>')
    def line(self,x0,y0,x1,y1,cls='line'):self.s.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" class="{cls}"/>')
    def rect(self,x,y,w,h,cls='part'):self.s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="{cls}"/>')
    def circle(self,x,y,r,cls='part'):self.s.append(f'<circle cx="{x}" cy="{y}" r="{r}" class="{cls}"/>')
    def save(self,name):self.s.append('</svg>');(OUT/name).write_text('\n'.join(self.s),encoding='utf-8')

def assembly():
    d=SVG('NÚCLEO INTEGRAL V2 — MONTAGEM DIMENSIONAL DE BANCADA')
    d.text(35,74,'Unidades: mm · cotas propostas para ensaio eletromagnético · revisão 2 · 12/10/2026')
    d.text(35,104,'Geometria inspirada na imagem; câmara em ar comum. Não há peças de vácuo, curvatura ou propulsão.')
    d.text(35,148,'VISTA SUPERIOR — COM UM MÓDULO VISÍVEL','sub')
    cx,cy,s=350,460,1.45
    d.rect(cx-180*s,cy-180*s,360*s,360*s)
    for r in [170,124,110,102.75,97.25,94,40,31,27,25]:
        d.circle(cx,cy,r*s,'coil' if r==102.75 else ('tube' if r in (27,25) else 'line'))
    for k in range(4):
        a=math.radians(45+90*k);x=155*math.cos(a);y=155*math.sin(a)
        d.circle(cx+x*s,cy-y*s,5*s);d.circle(cx+x*s,cy-y*s,2.75*s,'line')
        d.circle(cx+107*math.cos(a)*s,cy-107*math.sin(a)*s,1.7*s)
    d.rect(cx-165*s,cy+105*s,80*s,60*s,'tube')
    d.line(cx-180*s,748,cx+180*s,748,'dim');d.text(330,776,'360')
    d.line(625,cy-180*s,625,cy+180*s,'dim');d.text(634,466,'360')
    d.text(55,817,'Carcaça: Ø340 / Ø248; 4 furos Ø5,5 em círculo Ø310')
    d.text(55,845,'Carretel: Ø220; 4 furos Ø3,4 em círculo Ø214')
    d.text(55,873,'Ângulos das fixações: 45° / 135° / 225° / 315°')
    d.text(55,901,'Tirantes: X e Y = ±109,6016; carretel = ±75,6604')
    d.text(55,929,'Caixa de controle: X −165…−85; Y −165…−105; Z12…42')
    d.text(770,148,'VISTA FRONTAL / CORTE PELO EIXO','sub')
    fx,fy,ss=1050,725,2.0
    yz=lambda z:fy-z*ss
    d.rect(fx-180*ss,yz(12),360*ss,24)
    d.rect(fx-27*ss,yz(220),54*ss,198*ss,'tube')
    for x in [-109.6016,109.6016]:d.rect(fx+x*ss-5,yz(226),10,231*ss)
    for z in [65,185]:
        for z0 in [z-16,z+12]:
            for sign in [-1,1]:d.rect(fx+(124 if sign==1 else -170)*ss,yz(z0+4),46*ss,8)
        for zz in [z-7.7,z+5.7]:
            for sign in [-1,1]:d.rect(fx+(94 if sign==1 else -110)*ss,yz(zz+2),16*ss,4)
        for sign in [-1,1]:d.rect(fx+(97.25 if sign==1 else -102.75)*ss,yz(z+5.5),5.5*ss,22,'coil')
        d.line(fx-360,yz(z),fx+390,yz(z));d.text(1446,yz(z)+6,f'Z{z}')
    for sign in [-1,1]:
        d.circle(fx+135*sign*ss,yz(125),7.45*ss,'tube')
        d.circle(fx+135*sign*ss,yz(125),8.55*ss,'line')
        d.rect(fx+(32.8 if sign==1 else -37.2)*ss,yz(127.75),4.4*ss,11,'coil')
    d.rect(fx-4*ss,yz(123),8*ss,111*ss)
    d.rect(fx-2*ss,yz(127),4*ss,8,'coil')
    d.line(1460,yz(65),1460,yz(185),'dim');d.text(1473,yz(125),'120')
    d.line(1510,yz(-8),1510,yz(226),'dim');d.text(1520,yz(106),'234')
    d.line(fx-360,785,fx+360,785,'dim');d.text(fx-22,813,'360')
    d.text(770,854,'Centros: bobinas Z65/185; receptor e toroide Z125')
    d.text(770,882,'Tampas: Z49–53 / 77–81 / 169–173 / 197–201')
    d.text(770,910,'Espaçadores: 37 (×4), 15,4 (×8), 88 (×4), 17 (×4)')
    d.text(770,938,'Tirantes M5 ×231: Z−5…226; pés Z−8…0')
    d.line(35,974,1565,974)
    d.text(35,1012,'TOLERÂNCIAS, MATERIAIS E LIMITES','sub')
    notes=[
        'Peças isolantes. Impressão: alvo ±0,3; espaçadores faceados: alvo ±0,1. Furos acabar com broca Ø5,5 / Ø3,4.',
        'Tampas completas Ø340: mesa útil mínima Ø346 com brim3, recomendado≥350. Base: preferir chapa cortada/furada.',
        'Carretéis Ø220: mesa útil mínimaØ226. Suporte removível sob flange superior; não imprimir com canal obstruído.',
        'Confirmar diâmetro real do fio, resistência, isolamento e posições antes de energizar. Roscas e eletrônica são referências.',
        'Validação digital: arestas fechadas/orientação/volume e folgas selecionadas. Sem certificação mecânica, térmica ou de pressão.',
    ]
    for i,t in enumerate(notes):d.text(35,1045+29*i,t,'tiny')
    d.save('01_montagem_dimensional.svg')

def components():
    d=SVG('NÚCLEO INTEGRAL V2 — PEÇAS, ENROLAMENTOS E ENCAIXES')
    d.text(35,74,'Unidades: mm · cotas a verificar na fabricação · sem dimensionamento de pressão/vácuo')
    d.text(35,126,'01 / CARRETEL PRINCIPAL — CORTE RADIAL','sub')
    ox,oy,ss=65,325,10
    xr=lambda r:ox+(r-94)*ss; yz=lambda z:oy-z*ss
    d.rect(xr(94),yz(2),160,20);d.rect(xr(94),yz(15.4),160,20)
    d.rect(xr(95.25),yz(13.4),20,114)
    d.rect(xr(97.25),yz(13.2),55,110,'coil')
    d.line(265,yz(0),265,yz(15.4),'dim');d.text(278,249,'15,4')
    d.line(340,yz(2),340,yz(13.4),'dim');d.text(353,247,'11,4')
    d.text(35,362,'Ø220 / aberturaØ188; mangaØ190,5 / 194,5')
    d.text(35,392,'Flanges2; 5 camadas ×10 espiras, fio externo1,1')
    d.text(35,422,'Cobre R97,25…102,75; altura11; centro R100')
    d.text(35,452,'4 furosØ3,4 em R107; margem externa1,3')
    d.text(580,126,'02 / RECEPTOR — CORTE RADIAL','sub')
    ox,oy,ss=610,325,10
    xr=lambda r:ox+(r-31)*ss;yz=lambda z:oy-z*ss
    d.rect(xr(31),yz(3),90,30);d.rect(xr(31),yz(12),90,30)
    d.rect(xr(31),yz(9),15,60);d.rect(xr(32.8),yz(8.75),44,55,'coil')
    d.line(800,yz(0),800,yz(12),'dim');d.text(815,272,'12')
    d.text(580,362,'Ø80 / Ø62; mangaØ65; flanges3; canal6')
    d.text(580,392,'4 camadas ×5 espiras; cobreØ1,0 / externo1,1')
    d.text(580,422,'R32,8…37,2; altura5,5; folga axial0,5')
    d.text(580,452,'Centro Z125; flanges Z119–122 / 128–131')
    d.text(1070,126,'03 / TOROIDE AUXILIAR','sub')
    d.circle(1305,270,110,'tube');d.circle(1305,270,98,'line')
    d.text(1070,414,'Raio maior135; forma raio menor6,5')
    d.text(1070,444,'Fita0,95 → superfície7,45; centro fio8')
    d.text(1070,474,'48 espiras poloidais; externo1,1; Z125')
    d.text(35,530,'04 / PONTE RADIAL — 16 UNIDADES','sub')
    ox,oy,ss=55,570,7
    d.rect(ox,oy,56*ss,12*ss)
    d.circle(ox+3*ss,oy+6*ss,1.7*ss,'line');d.circle(ox+51*ss,oy+6*ss,2.75*ss,'line')
    d.line(ox,oy+110,ox+56*ss,oy+110,'dim');d.text(ox+175,oy+140,'56')
    d.line(ox+3*ss,oy-15,ox+51*ss,oy-15,'dim');d.text(ox+171,oy-26,'48')
    d.text(35,752,'Espessura4,3; largura12; furosØ3,4 eØ5,5')
    d.text(35,782,'Centros locais R107 eR155; corpo R104…160')
    d.text(35,812,'Ponte inferior Z53–57,3; superior Z72,7–77')
    d.text(35,842,'No módulo superior somar120 em Z')
    d.text(580,530,'05 / COLUNA E SENSOR','sub')
    d.rect(625,563,108,240,'tube');d.rect(629,563,100,240,'line')
    d.line(625,835,733,835,'dim');d.text(660,865,'Ø54')
    d.text(580,900,'Tubo externoØ54 / internoØ50 ×198; Z22…220')
    d.text(580,930,'ColaresØ70/54,6 ×6: Z22–28 / 214–220')
    d.text(580,960,'PedestalØ70/10 ×10; Z12–22; hasteØ8 ×111')
    d.text(1070,530,'06 / PILHA DE TIRANTES','sub')
    rows=[('Z−5…−1','Porca M5'),('Z−1…0','Arruela1'),('Z0…12','Base'),('Z12…49','Espaçador37'),
          ('Z49…53','Tampa4'),('Z53…77','Pontes4,3+espaçador15,4+ponte4,3'),('Z77…81','Tampa4'),('Z81…169','Espaçador88'),
          ('Z169…173','Tampa4'),('Z173…197','Pontes4,3+espaçador15,4+ponte4,3'),('Z197…201','Tampa4'),('Z201…218','Espaçador17'),
          ('Z218…219','Arruela1'),('Z219…223','Porca M5')]
    for i,(z,label) in enumerate(rows):
        d.text(1070,566+i*27,z,'tiny')
        d.text(1255,566+i*27,label if 'Pontes' not in label else '4,3 + 15,4 + 4,3','tiny')
    d.line(35,1015,1565,1015)
    d.text(35,1052,'A coluna está aberta na extremidade superior e comunica com ar comum. Não aplicar vácuo ou pressão.')
    d.text(35,1086,'Toroide: pilaresØ8×36,55 sobre tampa Z81, azimutes3,75°+90k; tocam a fita em Z117,55 entre espiras.')
    d.text(35,1120,'Hardware comprado: nylonM5/M3. Para a imagem completa, ver OBJ colorido, scene.js e visualizador 3D.')
    d.text(35,1154,'Malhas e desenhos não substituem inspeção, ensaios de aquecimento e avaliação mecânica da montagem física.')
    d.save('02_componentes_enrolamentos.svg')

if __name__=='__main__':assembly();components();print('2 desenhos SVG dimensionais gerados.')
