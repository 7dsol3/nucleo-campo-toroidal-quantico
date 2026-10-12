"""Revisão independente de encaixes críticos usando o scene.json exportado.

Não é detector global de colisões. Examina interfaces físicas identificadas.
Rodar após gerar_integral.py; não altera a geometria.
"""
from pathlib import Path
import json, math
OUT=Path(__file__).resolve().parent
SCENE=json.loads((OUT/'scene.json').read_text(encoding='utf-8'))
PARTS={p['id']:p for p in SCENE['parts']}
CHECKS=[]

def bounds(name):
    p=PARTS[name];v=p['vertices']
    return ([min(v[i::3]) for i in range(3)],[max(v[i::3]) for i in range(3)])

def check(name,condition,detail):
    CHECKS.append({'check':name,'passed':bool(condition),'detail':detail})
    assert condition,(name,detail)

def z_overlap(a,b):
    alo,ahi=bounds(a);blo,bhi=bounds(b)
    return min(ahi[2],bhi[2])-max(alo[2],blo[2])

def radial_range(name):
    v=PARTS[name]['vertices'];r=[math.hypot(v[i],v[i+1]) for i in range(0,len(v),3)]
    return min(r),max(r)

def center_xy(name):
    lo,hi=bounds(name);return (lo[0]+hi[0])/2,(lo[1]+hi[1])/2

def main():
    eps=2e-6
    for label in ['inferior','superior']:
        copper=radial_range('cobre_'+label)
        for suffix in ['baixo','cima']:
            frame=radial_range(f'tampa_{label}_{suffix}')
            check(f'cobre_{label}/tampa_{suffix}',frame[0]-copper[1]>0,
                  {'radial_clearance_mm':round(frame[0]-copper[1],6)})
        for k in range(1,5):
            for suffix in ['baixo','cima']:
                bridge=f'ponte_{label}_{suffix}_{k}'
                # Bridge starts atR104 at centerline; all its XY radius>=104.
                r=radial_range(bridge)
                check(f'cobre_{label}/ponte_{suffix}_{k}',r[0]-copper[1]>0,
                      {'radial_clearance_mm':round(r[0]-copper[1],6)})
            j=2 if label=='inferior' else 4
            spacer=f'espacador_{k}_{j}'
            overlaps=[z_overlap(spacer,f'ponte_{label}_{s}_{k}') for s in ['baixo','cima']]
            check(f'espaçador/ponte_{label}_{k}',all(v<=eps for v in overlaps),
                  {'z_overlap_mm':overlaps,'contacts':'Só contato nas faces; spacer não entra na ponte'})
            spool=f'carretel_{label}'
            for s in ['baixo','cima']:
                overlap=z_overlap(spool,f'ponte_{label}_{s}_{k}')
                check(f'carretel/ponte_{label}_{s}_{k}',overlap<=eps,
                      {'z_overlap_mm':overlap,'contact':'flange externo apoiado na face da ponte'})

    # Collar, tongues and receiver require disjoint interiors along Z.
    for k in range(1,5):
        tongue=f'lingueta_receptor_{k}'
        for other in ['colar_receptor','carretel_receptor']:
            overlap=z_overlap(tongue,other)
            check(f'{tongue}/{other}',overlap<=eps,{'z_overlap_mm':overlap})
    tube=radial_range('coluna_transparente');spool=radial_range('carretel_receptor')
    check('receptor/tubo',spool[0]-tube[1]>0,
          {'radial_clearance_mm':round(spool[0]-tube[1],6)})
    rod=radial_range('haste_diagnostica')
    check('haste/tubo',tube[0]-rod[1]>0,
          {'radial_clearance_mm':round(tube[0]-rod[1],6)})
    check('sondaHall/haste',z_overlap('sonda_hall','haste_diagnostica')<=eps,
          {'z_overlap_mm':z_overlap('sonda_hall','haste_diagnostica')})
    check('tubo/pedestal',z_overlap('coluna_transparente','pedestal_coluna')<=eps,
          {'z_overlap_mm':z_overlap('coluna_transparente','pedestal_coluna'),'contact':'Apoio em Z22'})

    wire=radial_range('espiras_toroidais')
    # Round spacer centers are known from their exact exported bounding boxes.
    for k in range(1,5):
        x,y=center_xy(f'espacador_{k}_3')
        lo,hi=bounds(f'espacador_{k}_3');rpost=(hi[0]-lo[0])/2
        gap=math.hypot(x,y)-rpost-wire[1]
        check(f'toroide/tirante_{k}',gap>0,{'radial_clearance_mm':round(gap,6)})
        # Each winding plane has constant toroidal azimuth. A pillar placed
        # halfway between planes clears every wire by this XY bound.
        x,y=center_xy(f'apoio_toroide_{k}')
        alpha=math.atan2(y,x);rp=math.hypot(x,y)
        delta=min(abs(math.atan2(math.sin(alpha-a),math.cos(alpha-a))) for a in [math.tau*i/48 for i in range(48)])
        gap=rp*math.sin(delta)-4-.55
        check(f'toroide/pilar_{k}',gap>0,{'lower_bound_xy_clearance_mm':round(gap,6),
              'plane_half_spacing_deg':round(math.degrees(delta),6)})

    for label in ['inferior','superior']:
        for k in range(1,9):
            c=f'cassete_{label}_{k}';x,y=center_xy(c)
            # Bounding circle of the local20x10 cassette footprint.
            rc=math.hypot(10,5)
            gap=min(math.hypot(x-px,y-py)-rc-5 for px,py in [center_xy(f'espacador_{j}_3') for j in range(1,5)])
            check(f'{c}/tirantes',gap>0,{'conservative_xy_clearance_mm':round(gap,6)})

    for k in range(1,5):
        rodlo,rodhi=bounds(f'tirante_{k}')
        nutlo,nuthi=bounds(f'porca_{k}_baixo')
        check(f'engajamento_porcas_inferiores_{k}',rodlo[2]<=nutlo[2]+eps and rodhi[2]>=nuthi[2]-eps,
              {'rod_z':(rodlo[2],rodhi[2]),'nut_z':(nutlo[2],nuthi[2])})
    result={'checks':CHECKS,'passed':len(CHECKS),'failed':0,
            'scope':'Interfaces críticas identificadas; não é detecção global de colisões',
            'fabrication_tested':False,'load_or_adhesive_analysis':False,
            'corrections':['Espaçadores entre pontes agora15,4mm, sem atravessar furosØ5,5',
                           'Colar receptor H2 emZ115–117; linguetasZ117–119',
                           'Cassetes deslocados para22,5°+45k, apoiados entre tampas',
                           'Tirantes231mmZ−5…226, engajamento integral inferior',
                           'Conector geométrico encosta na parede interna, sem penetrar a malha da parede'],
            'intentional_interfaces':['Roscas são cilindros em furos nominais de porcas',
                                    'Colares ao tubo com adesivo preenchem folga radial0,3',
                                    'HasteØ8 em furoØ10 do pedestal: calçar e aderir; folga radial1',
                                    'Apoios/adesivos/abraçadeiras precisam de ensaio físico']}
    (OUT/'revisao_mecanica.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'passed':len(CHECKS),'failed':0,'scope':result['scope']},ensure_ascii=False))

if __name__=='__main__':main()
