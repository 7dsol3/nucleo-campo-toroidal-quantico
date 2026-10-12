"""CAD reprodutível, em mm. Python padrão; sem pressão/vácuo nem peças quânticas."""
from pathlib import Path
import csv, json, math
from meshlib import Mesh, bobbin, tube, cylinder, polar, wall, patch_with_hole, rectangle_loop, planar_ring, TAU

OUT = Path(__file__).resolve().parent
ANGLES = [(45+90*k)*math.pi/180 for k in range(4)]
POSTS = [(155*math.cos(a),155*math.sin(a)) for a in ANGLES]
P = {
    'units':'mm','base_width':360,'base_thickness':12,
    'main_coil_radius_mean':100,'main_coil_turns':50,'main_centers_z':[65,185],
    'main_coil_wire_bare_diameter':1.0,'main_coil_wire_insulated_diameter':1.1,
    'main_winding_radial':5.5,'main_winding_axial':11,
    'spool_od':220,'spool_height':15.4,'frame_inner_radius':124,'frame_outer_radius':170,
    'frame_cover_thickness':4,'frame_covers_offset_z':[-16,12],
    'post_radius':155,'post_outer_diameter':10,'post_hole_diameter':5.5,
    'post_rod_diameter':5,'post_rod_length':231,'post_rod_z0':-5,
    'post_spacer_intervals':[[12,49],[57.3,72.7],[81,169],[177.3,192.7],[201,218]],
    'bridge_local_x':[104,160],'bridge_width':12,'bridge_height':4.3,
    'bridge_hole_radius_centers':[107,155],'bridge_hole_diameters':[3.4,5.5],
    'column_od':54,'column_id':50,'column_z':[22,220],
    'pickup_radius_mean':35,'pickup_turns':20,'pickup_z':125,
    'pickup_wire_bare_diameter':1.0,'pickup_wire_insulated_diameter':1.1,
    'pickup_pack_radial':4.4,'pickup_pack_axial':5.5,
    'toroid_major_radius':135,'toroid_effective_minor_radius':8,
    'toroid_former_minor_radius':6.5,'toroid_insulating_wrap_thickness':0.95,
    'toroid_turns':48,'toroid_z':125,
    'toroid_wire_bare_diameter':1.0,'toroid_wire_insulated_diameter':1.1,
    'instrumentation_chamber':'ordinary air, open ends, no vacuum rating',
    'electronics_box_external':[80,60,28],'electronics_box_corner':[-165,-165,12],
    'geometry_status':'proposed test rig; no physical fabrication or pressure validation',
}
COLORS={'polymer':[0.14,0.20,0.26,1],'blue':[0.11,0.43,0.68,1],
        'orange':[0.86,0.31,0.10,1],'copper':[0.88,0.44,0.16,1],
        'white':[0.75,0.83,0.87,1],'base':[0.22,0.28,0.34,1],
        'glass':[0.25,0.76,0.9,0.24],'green':[0.09,0.40,0.27,1],
        'rubber':[0.04,0.06,0.09,1],'sensor':[0.66,0.28,0.77,1]}
PARTS=[]; CHECKS={}; UNIQUE={}; BOM=[]

def box(name,x0,x1,y0,y1,z0,z1):
    m=Mesh(name)
    m.quad((x0,y0,z0),(x0,y1,z0),(x1,y1,z0),(x1,y0,z0),(0,0,-1))
    m.quad((x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1),(0,0,1))
    wall(m,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1,center=((x0+x1)/2,(y0+y1)/2))
    return m

def transformed(m,name,angle=0,dx=0,dy=0,dz=0):
    n=Mesh(name); co=math.cos(angle); si=math.sin(angle)
    n.v=[(co*x-si*y+dx,si*x+co*y+dy,z+dz) for x,y,z in m.v]; n.f=m.f[:]
    return n

def plate_grid(name,xs,ys,h,holes):
    m=Mesh(name)
    for ix in range(len(xs)-1):
        for iy in range(len(ys)-1):
            x0,x1=xs[ix:ix+2];y0,y1=ys[iy:iy+2]
            loop=rectangle_loop(x0,x1,y0,y1,n=12)
            hole=holes.get((ix,iy))
            for z,n in [(0,-1),(h,1)]:
                if hole:
                    xc,yc,r=hole; inside=patch_with_hole(m,loop,(xc,yc),r,z,(0,0,n))
                    if z==0: wall(m,inside,0,h,True,(xc,yc))
                else:
                    for a,b in zip(loop,loop[1:]+loop[:1]):
                        m.tri(((x0+x1)/2,(y0+y1)/2,z),(*a,z),(*b,z),(0,0,n))
            for a,b in zip(loop,loop[1:]+loop[:1]):
                if a[0]==b[0] and a[0] in (xs[0],xs[-1]):
                    m.quad((*a,0),(*b,0),(*b,h),(*a,h),(-1 if a[0]==xs[0] else 1,0,0))
                if a[1]==b[1] and a[1] in (ys[0],ys[-1]):
                    m.quad((*a,0),(*b,0),(*b,h),(*a,h),(0,-1 if a[1]==ys[0] else 1,0))
    return m

def base():
    c=155/math.sqrt(2); xs=[-180,-c-4,-c+4,c-4,c+4,180]
    holes={(i,j):((xs[i]+xs[i+1])/2,(xs[j]+xs[j+1])/2,2.75) for i in (1,3) for j in (1,3)}
    return plate_grid('base_360x360x12',xs,xs,12,holes)

def bridge():
    return plate_grid('ponte_56x12x4p3_M3_M5',[104,111,150,160],[-6,6],4.3,
                      {(0,0):(107,0,1.7),(2,0):(155,0,2.75)})

def frame():
    m=Mesh('tampa_anel_OD340_ID248_H4_M5')
    delta=3*math.pi/180; subdivisions=12
    special=[]
    for alpha in ANGLES:special.extend(alpha-delta+2*delta*i/subdivisions for i in range(subdivisions+1))
    angles=[0,math.pi/2,math.pi,3*math.pi/2,TAU]+special
    for k in range(4):
        start=ANGLES[k]+delta;end=ANGLES[(k+1)%4]-delta+(TAU if k==3 else 0)
        for i in range(1,45):angles.append((start+(end-start)*i/45)%TAU)
    angles=sorted(set(round(a,12) for a in angles));angles[0]=0;angles[-1]=TAU
    for z,n in [(0,-1),(4,1)]:
        planar_ring(m,[124,145],angles,z,(0,0,n))
        for a,b in zip(angles,angles[1:]):
            mid=(a+b)/2
            if not any(abs(math.atan2(math.sin(mid-alpha),math.cos(mid-alpha)))<delta for alpha in ANGLES):
                for j in range(subdivisions):
                    ri=145+25*j/subdivisions;ro=145+25*(j+1)/subdivisions
                    m.quad(polar(ri,a,z),polar(ro,a,z),polar(ro,b,z),polar(ri,b,z),(0,0,n))
        for alpha,center in zip(ANGLES,POSTS):
            al=[a for a in angles if alpha-delta-1e-10<=a<=alpha+delta+1e-10];lo,hi=al[0],al[-1]
            outer=[]
            for j in range(subdivisions):outer.append(polar(145+25*j/subdivisions,lo)[:2])
            for a in al[:-1]:outer.append(polar(170,a)[:2])
            for j in range(subdivisions):outer.append(polar(170-25*j/subdivisions,hi)[:2])
            for a in reversed(al[1:]):outer.append(polar(145,a)[:2])
            inner=patch_with_hole(m,outer,center,2.75,z,(0,0,n))
            if z==0:wall(m,inner,0,4,True,center)
    wall(m,[polar(124,a)[:2] for a in angles[:-1]],0,4,True)
    wall(m,[polar(170,a)[:2] for a in angles[:-1]],0,4)
    return m

def torus(name,R,r,n=144,p=16,z0=0):
    m=Mesh(name)
    def v(i,j):
        a=TAU*(i%n)/n;b=TAU*(j%p)/p
        return ((R+r*math.cos(b))*math.cos(a),(R+r*math.cos(b))*math.sin(a),z0+r*math.sin(b))
    for i in range(n):
        for j in range(p):
            a=TAU*(i+.5)/n;b=TAU*(j+.5)/p
            m.quad(v(i,j),v(i+1,j),v(i+1,j+1),v(i,j+1),
                   (math.cos(a)*math.cos(b),math.sin(a)*math.cos(b),math.sin(b)))
    return m

def toroid_wires(name,R,r,wire_r,N=48,z0=125):
    # Each turn is a closed poloidal circle; connections and terminals omitted.
    m=Mesh(name); p=40; q=8
    for k in range(N):
        alpha=TAU*k/N
        er=(math.cos(alpha),math.sin(alpha),0);ea=(-math.sin(alpha),math.cos(alpha),0)
        def v(i,j):
            b=TAU*(i%p)/p;t=TAU*(j%q)/q
            return tuple(R*er[c]+r*(math.cos(b)*er[c]+math.sin(b)*(1 if c==2 else 0))+
                         wire_r*(math.cos(t)*(math.cos(b)*er[c]+math.sin(b)*(1 if c==2 else 0))+math.sin(t)*ea[c])+
                         (z0 if c==2 else 0) for c in range(3))
        for i in range(p):
            for j in range(q):
                b=TAU*(i+.5)/p;t=TAU*(j+.5)/q
                norm=tuple(math.cos(t)*(math.cos(b)*er[c]+math.sin(b)*(1 if c==2 else 0))+math.sin(t)*ea[c] for c in range(3))
                m.quad(v(i,j),v(i+1,j),v(i+1,j+1),v(i,j+1),norm)
    return m

def nut(name,af=8,h=4,ri=2.5):
    m=Mesh(name); ro=af/math.sqrt(3); outer=[]
    for k in range(6):
        a=polar(ro,TAU*k/6)[:2];b=polar(ro,TAU*(k+1)/6)[:2]
        for j in range(8):outer.append(tuple(a[i]+(b[i]-a[i])*j/8 for i in range(2)))
    for z,n in [(0,-1),(h,1)]:
        inside=patch_with_hole(m,outer,(0,0),ri,z,(0,0,n))
        if z==0:wall(m,inside,0,h,True)
    wall(m,outer,0,h);return m

def add(m,group,name,color='polymer',status='proposto',role='',explode=None,manufacture=None,source=None):
    meta={'id':m.name,'name':name,'group':group,'vertices':[x for p in m.v for x in p],
          'faces':[i for f in m.f for i in f],'color':COLORS[color],
          'explode':explode or [0,0,0],'status':status,'role':role,
          'kind':manufacture or 'assembly','source':source or '',
          'units':'mm','bounds':[[min(p[i] for p in m.v) for i in range(3)],
                                  [max(p[i] for p in m.v) for i in range(3)]]}
    PARTS.append(meta);return meta

def fabricate(m,quantity,material,description,method='Imprimir/cortar; verificar medidas'):
    CHECKS[m.name]=m.verify();m.stl(OUT/(m.name+'.stl'));UNIQUE[m.name]=m
    BOM.append({'code':f'M{len(BOM)+1:02}','name':description,'quantity':quantity,
                'material':material,'file':m.name+'.stl','method':method,
                'dimensions_mm':CHECKS[m.name]['bounds_mm']})
    return m

def build():
    b=fabricate(base(),1,'Policarbonato/G10/PMMA isolante','Base 360 × 360 × 12 com 4 furos Ø5,5',
                'Preferir chapa cortada e furada; STL dimensional')
    cover=fabricate(frame(),4,'Polímero isolante PETG/PA','Tampa anular Ø340/248 × 4 com quatro furos Ø5,5')
    bb=fabricate(bobbin(),2,'Polímero isolante PETG/PA','Carretel principal Ø220 × 15,4; quatro furos Ø3,4')
    br=fabricate(bridge(),16,'Polímero isolante PETG/PA','Ponte radial 56 × 12 × 4,3; centros de furos 48')
    add(b,'base','Base isolante de bancada','base',role='Suporte de todos os módulos',explode=[0,0,-45],manufacture='fabricar')
    for label,z,color,offset in [('inferior',65,'orange',-35),('superior',185,'blue',35)]:
        group=label.replace('inferior','lower').replace('superior','upper')+'_frame'
        for suffix,z0 in [('baixo',z-16),('cima',z+12)]:
            add(cover.moved(f'tampa_{label}_{suffix}',dz=z0),group,f'Tampa {suffix} — módulo {label}',color,
                role='Anel de confinamento: carcaça mecânica isolante',explode=[0,0,offset+(8 if suffix=='cima' else -8)],manufacture='fabricar',source=cover.name+'.stl')
        for k,a in enumerate(ANGLES):
            for suffix,z0 in [('baixo',z-12),('cima',z+7.7)]:
                add(transformed(br,f'ponte_{label}_{suffix}_{k+1}',a,dz=z0),group,f'Ponte de apoio {k+1} {suffix} — {label}','white',
                    role='Conecta carretel R107 à fixação externa R155',explode=[12*math.cos(a),12*math.sin(a),offset],manufacture='fabricar',source=br.name+'.stl')
        # Exterior cassettes sit between mount azimuths and touch both covers.
        for k in range(8):
            a=TAU*k/8+math.pi/8
            c=box('cassete_visual',-10,10,-5,5,0,24)
            add(transformed(c,f'cassete_{label}_{k+1}',a,160*math.cos(a),160*math.sin(a),z-12),group,
                f'Cassete externo {k+1} — {label}',color,role='Guia e organização de cabos; polímero',
                explode=[35*math.cos(a),35*math.sin(a),offset],status='opcional',manufacture='referência')
        cg='lower_coil' if label=='inferior' else 'upper_coil'
        add(bb.moved(f'carretel_{label}',dz=z-7.7),cg,f'Carretel da bobina {label}','polymer',role='Guia isolante para 50 espiras',explode=[0,0,offset],manufacture='fabricar',source=bb.name+'.stl')
        winding=tube('envelope_cobre',102.75,97.25,11,n=128).moved(f'cobre_{label}',dz=z-5.5)
        add(winding,cg,f'Enrolamento 50 espiras — {label}','copper',status='envelope aproximado',
            role='Bobina circular azimutal; alimentada externamente',explode=[0,0,offset],manufacture='enrolar')
        # Bolts M3 connect bridge/bobbin/bridge stacks; no metal closed rings.
        for k,a in enumerate(ANGLES):
            x=107*math.cos(a);y=107*math.sin(a)
            add(cylinder('parafuso_M3',1.5,31).moved(f'fixacao_carretel_{label}_{k+1}',x,y,z-15),cg,
                f'Fixação M3 carretel {label} — {k+1}','white',role='Parafuso nylon M3×31 nominal, rosca ilustrativa',explode=[0,0,offset],manufacture='comprar')
            for suffix,z0 in [('baixo',z-12.5),('cima',z+12)]:
                add(tube('arruela_M3',3,1.7,.5,32).moved(f'arruela_carretel_{label}_{k+1}_{suffix}',x,y,z0),cg,
                    f'Arruela M3 {label} {k+1} {suffix}','white',role='Ø6/3,4 ×0,5',explode=[0,0,offset],manufacture='comprar')
            for suffix,z0 in [('baixo',z-14.9),('cima',z+12.5)]:
                add(nut('porca_M3',5.5,2.4,1.5).moved(f'porca_carretel_{label}_{k+1}_{suffix}',x,y,z0),cg,
                    f'Porca M3 {label} {k+1} {suffix}','white',role='AF5,5 ×2,4; nylon',explode=[0,0,offset],manufacture='comprar')
    # Main tie-rod stack: hollow spacers contact covers; rods pass through holes.
    rod=cylinder('tirante_M5_231',2.5,231)
    w=tube('arruela_M5_OD10_ID5p5_H1',5,2.75,1)
    nt=nut('porca_M5_AF8_H4')
    for k,(x,y) in enumerate(POSTS):
        add(rod.moved(f'tirante_{k+1}',x,y,-5),'supports',f'Tirante isolante M5 × 231 — {k+1}','white',role='Rosca M5 apenas representada por cilindro',explode=[30*x/155,30*y/155,0],manufacture='comprar')
        for j,(lo,hi) in enumerate(P['post_spacer_intervals']):
            h=round(hi-lo,3);label_h=str(h).replace('.','p');m=tube(f'espacador_OD10_ID5p5_H{label_h}',5,2.75,h)
            if m.name not in UNIQUE:fabricate(m,4,'Nylon/PA isolante',f'Espaçador Ø10/5,5 × {h}',method='Cortar tubo e facear; controlar comprimento ±0,1')
            add(m.moved(f'espacador_{k+1}_{j+1}',x,y,lo),'supports',f'Espaçador {h} mm — tirante {k+1}','white',role='Define alturas da montagem',explode=[30*x/155,30*y/155,0],manufacture='fabricar',source=m.name+'.stl')
        for suffix,z0 in [('baixo',-1),('cima',218)]:
            add(w.moved(f'arruela_{k+1}_{suffix}',x,y,z0),'supports',f'Arruela M5 {suffix} {k+1}','white',role='Distribui pressão de aperto',manufacture='comprar')
        for suffix,z0 in [('baixo',-5),('cima',219)]:
            add(nt.moved(f'porca_{k+1}_{suffix}',x,y,z0),'supports',f'Porca M5 {suffix} {k+1}','white',role='Hardware comprado; roscas não modeladas',manufacture='comprar')
    for k,(x,y) in enumerate([(x,y) for x in (-155,155) for y in(-155,155)]):
        add(cylinder('pe',8,8).moved(f'pe_{k+1}',x,y,-8),'base',f'Pé de borracha {k+1}','rubber',role='Isola vibração e protege apoio',manufacture='comprar')
    # Sensor tube is open to ordinary air. Collar rings mounted on base/top legs.
    col=tube('tubo_instrumentacao_OD54_ID50_H198',27,25,198,n=96)
    fabricate(col,1,'PMMA/policarbonato transparente','Tubo aberto Ø54/50 × 198',method='Comprar/cortar tubo; sem vedação, sem classificação de pressão')
    add(col.moved('coluna_transparente',dz=22),'column','Coluna transparente de instrumentação','glass',
        role='Câmara de interferência: volume de ar comum, aberta; sem vácuo',explode=[0,0,60],manufacture='comprar')
    collar=tube('colar_coluna_OD70_ID54p6_H6',35,27.3,6,n=96)
    fabricate(collar,2,'Polímero isolante','Colar Ø70/54,6 × 6',method='Apoio do tubo com folga diametral 0,6; fixar com adesivo compatível')
    for suffix,z0 in [('inferior',22),('superior',214)]:
        add(collar.moved(f'colar_{suffix}',dz=z0),'column',f'Colar da coluna — {suffix}','blue',
            role='Apoio da instrumentação',explode=[0,0,-15 if suffix=='inferior' else 70],manufacture='fabricar',source=collar.name+'.stl')
    add(cylinder('haste_sensor',4,111).moved('haste_diagnostica',dz=12),'column','Haste axial de posicionamento de sensores Ø8 × 111','white',
        role='Suporte isolante removível para sonda Hall; não é feixe energético',explode=[0,0,90],manufacture='comprar')
    # Lower collar pedestal has air clearance for tube ending at22.
    pedestal=tube('pedestal_coluna_OD70_ID10_H10',35,5,10,n=96)
    fabricate(pedestal,1,'Polímero isolante','Pedestal Ø70/10 × 10 da coluna',method='Aderir ao centro da base; tubo encosta em Z22, topo aberto')
    add(pedestal.moved('pedestal_coluna',dz=12),'column','Pedestal da instrumentação','polymer',role='Apoia colar inferior',manufacture='fabricar',source=pedestal.name+'.stl')
    # Pickup consists of two flanges and sleeve; no fictitious energy converter.
    # Winding4radial layers x5axial turns: R32.8..37.2; height5.5.
    pick=Mesh('carretel_receptor_OD80_ID62_H12')
    # Union surface generated with a single profile sweep, avoiding overlaps.
    profile=[(31,0),(40,0),(40,3),(32.5,3),(32.5,9),(40,9),(40,12),(31,12)]
    revolve_profile(pick,profile,128)
    fabricate(pick,1,'Polímero isolante','Carretel receptor Ø80/62 × 12')
    add(pick.moved('carretel_receptor',dz=119),'receiver','Carretel receptor de 20 espiras','polymer',role='Bobina secundária mede tensão induzida',explode=[0,0,10],manufacture='fabricar',source=pick.name+'.stl')
    add(tube('pickup_wire',37.2,32.8,5.5,128).moved('cobre_receptor',dz=122.25),'receiver','Enrolamento receptor 20 espiras R35','copper',
        role='Conversão eletromagnética convencional; dissipação na carga',status='envelope aproximado',manufacture='enrolar')
    # Receiver support: collar at118 with four radial pegs below lower flange.
    collarpick=tube('colar_receptor_OD62_ID54p6_H2',31,27.3,2,96)
    fabricate(collarpick,1,'Polímero isolante','Colar do receptor Ø62/54,6 × 2')
    add(collarpick.moved('colar_receptor',dz=115),'receiver','Colar de apoio do receptor','blue',role='Aderir ao tubo em Z115–117; linguetas acima em Z117–119',manufacture='fabricar',source=collarpick.name+'.stl')
    for k in range(4):
        a=TAU*k/4;m=box('lingueta',29,38,-3,3,0,2)
        add(transformed(m,f'lingueta_receptor_{k+1}',a,dz=117),'receiver',f'Apoio receptor {k+1}','white',role='Suporte sob flange receptor, fixar ao colar',manufacture='referência')
    # Separate auxiliary toroidal test former, removable; R135 outside receiver.
    former=torus('forma_toroidal_R135_r6p5',135,6.5,n=144,p=20)
    fabricate(former,1,'Polímero isolante','Forma toroidal Ø283/257 com seção Ø13',method='Enrolar manualmente fio através do centro; pode imprimir deitado com suporte')
    add(former.moved('forma_toroidal',dz=125),'toroid','Forma auxiliar toroidal R135/r6,5','polymer',
        role='Forma de ar isolante; canal experimental opcional',explode=[0,0,0],manufacture='fabricar',source=former.name+'.stl')
    # 0.95mm insulating wrap brings the surface to minorR7.45 so winding
    # centerR8 with insulateddiameter1.1 touches the wrapped former.
    tape_outer=torus('fita_toroidal',135,7.45,n=144,p=20,z0=125)
    tape_inner=torus('fita_interior',135,6.5,n=144,p=20,z0=125)
    vshift=len(tape_outer.v);tape_outer.v.extend(tape_inner.v)
    tape_outer.f.extend(tuple(vshift+i for i in reversed(face)) for face in tape_inner.f)
    add(tape_outer,'toroid','Camada isolante toroidal 0,95 mm','blue',
        role='Fita/enchimento medido: superfície Rminor7,45 para fio de centro Rminor8',manufacture='aplicar')
    tw=toroid_wires('espiras_toroidais',135,8,.55)
    add(tw,'toroid','48 espiras poloidais — toroide auxiliar','copper',
        role='Bobina toroidal convencional; alimentação independente',status='espiras separadas; terminais não detalhados',manufacture='enrolar')
    for k in range(4):
        # Four supports on lower cover topZ81, below tape bottomZ117.55,
        # between winding azimuths.
        # They do not pass through the lower covers or intersect the windings.
        a=TAU*k/4+math.pi/48;x=135*math.cos(a);y=135*math.sin(a)
        add(cylinder('apoio_toroide',4,36.55).moved(f'apoio_toroide_{k+1}',x,y,81),'toroid',
            f'Pilar auxiliar toroidal {k+1}','white',role='Ø8 × 36,55 sobre tampa inferior Z81; fixar com adesivo e abraçadeira',explode=[15*math.cos(a),15*math.sin(a),0],manufacture='comprar')
    # Control housing with separate flat bottom, four walls and vented lid.
    x0,y0=-165,-165;wbox,hbox=80,60
    add(box('controle_fundo',x0,x0+wbox,y0,y0+hbox,12,14),'control','Fundo da caixa eletrônica','polymer',role='Suporte para placas externas ao campo',manufacture='referência')
    for k,(xa,xb,ya,yb) in enumerate([(x0,x0+2,y0,y0+hbox),(x0+wbox-2,x0+wbox,y0,y0+hbox),(x0+2,x0+wbox-2,y0,y0+2),(x0+2,x0+wbox-2,y0+hbox-2,y0+hbox)]):
        add(box(f'controle_parede_{k+1}',xa,xb,ya,yb,14,40),'control',f'Parede da caixa eletrônica {k+1}','polymer',role='Caixa convencional ventilada',manufacture='referência')
    for k in range(5):
        add(box(f'controle_vent_{k+1}',x0+2,x0+wbox-2,y0+2+k*11,y0+7+k*11,40,42),'control',f'Lâmina tampa ventilada {k+1}','blue',
            role='Aberturas permitem dissipação natural; não estanca',explode=[0,0,25],manufacture='referência')
    add(box('placa_controle',-160,-120,-160,-111,17,19),'control','Placa de controle / aquisição','green',role='Esquemático e valores elétricos estão no projeto; geometria genérica',manufacture='comprar')
    add(box('carga_resistiva',-113,-92,-150,-121,18,26),'control','Carga resistiva — energia induzida dissipada','orange',role='Matriz de conversão: carga convencional, não energia de vácuo',manufacture='comprar')
    add(box('conector_potencia',-163,-156,-152,-136,23,34),'control','Conector de alimentação externa','white',role='Fonte de baixa tensão com limitação de corrente; adaptar abertura da caixa ao conector comercial',manufacture='comprar')
    # Probe faces contact winding envelope atX102.75; no winding intersection.
    for label,z in [('inferior',65),('superior',185)]:
        add(box(f'sonda_termica_{label}',102.75,106.75,-2,2,z-2,z+2),'thermal',f'Sonda de temperatura — bobina {label}','sensor',
            role='Sensor em contato externo ao envelope de cobre; fixar com fita isolante',manufacture='comprar')
    add(box('sonda_hall',-2,2,-2,2,123,127),'thermal','Sonda Hall no eixo Z125','sensor',
        role='Medida experimental do campo axial; haste possui suporte esquemático',manufacture='comprar')

def revolve_profile(m,profile,n=128):
    for (r0,z0),(r1,z1) in zip(profile,profile[1:]+profile[:1]):
        dr=r1-r0;dz=z1-z0
        for k in range(n):
            a=TAU*k/n;b=TAU*(k+1)/n;mid=(a+b)/2
            # Profile is CCW in(r,z); outward=(dz,-dr) in meridional plane.
            normal=(dz*math.cos(mid),dz*math.sin(mid),-dr)
            m.quad(polar(r0,a,z0),polar(r0,b,z0),polar(r1,b,z1),polar(r1,a,z1),normal)

def write_scene():
    scene={'version':2,'units':'mm','title':'Núcleo integral: bancada eletromagnética instrumentada',
           'parts':PARTS,'parameters':P,'groups':['base','lower_frame','upper_frame','lower_coil','upper_coil','column','receiver','supports','control','thermal','toroid'],
           'limits':'CAD proposto. Não constitui teste físico; não produz simulação quântica ou relativística.',
           'dimensions':{'width_mm':360,'depth_mm':360,'height_mm':234}}
    encoded=json.dumps(scene,ensure_ascii=False,separators=(',',':'))
    (OUT/'scene.json').write_text(encoded,encoding='utf-8')
    (OUT/'scene.js').write_text('window.NUCLEO_SCENE='+encoded+';\n',encoding='utf-8')
    with (OUT/'montagem_integral.mtl').open('w',encoding='utf-8') as f:
        for name,color in COLORS.items():f.write(f'newmtl {name}\nKd {color[0]} {color[1]} {color[2]}\nd {color[3]}\nNs 40\n\n')
    with (OUT/'montagem_integral.obj').open('w',encoding='utf-8') as f:
        f.write('# mm; proposed externally powered electromagnetic rig\nmtllib montagem_integral.mtl\n');idx=1
        for part in PARTS:
            col=next((k for k,v in COLORS.items() if v==part['color']),'polymer')
            f.write(f"g {part['id']}\nusemtl {col}\n")
            v=part['vertices'];faces=part['faces']
            for i in range(0,len(v),3):f.write(f'v {v[i]:.6f} {v[i+1]:.6f} {v[i+2]:.6f}\n')
            for i in range(0,len(faces),3):f.write('f '+' '.join(str(idx+j) for j in faces[i:i+3])+'\n')
            idx+=len(v)//3

def validate():
    for part in PARTS:
        m=Mesh(part['id']);v=part['vertices'];f=part['faces']
        m.v=[tuple(v[i:i+3]) for i in range(0,len(v),3)];m.f=[tuple(f[i:i+3]) for i in range(0,len(f),3)]
        if m.name not in CHECKS:CHECKS[m.name]=m.verify()
    checks={
       'main_centers_separation_mm':120,
       'main_copper_to_frame_inner_radial_clearance_mm':124-102.75,
       'main_copper_to_bridge_inner_clearance_mm':104-102.75,
       'main_spool_to_frame_radial_clearance_mm':124-110,
       'main_winding_axial_clearance_mm':11.4-11,
       'toroid_wire_to_post_clearance_mm':155-5-(135+8+.55),
       'toroid_former_to_coil_top_clearance_mm':125-6.5-(65+7.7),
       'pickup_to_column_radial_clearance_mm':31-27,
       'pickup_wire_to_sleeve_clearance_mm':32.8-32.5,
       'column_collar_radial_clearance_mm':27.3-27,
       'rod_to_hole_radial_clearance_mm':2.75-2.5,
       'control_lid_to_lower_frame_z_clearance_mm':49-42,
       'post_to_outer_frame_edge_ligament_mm':170-155-2.75,
       'main_coil_mount_ligament_mm':110-107-1.7,
       'base_mount_coordinates_mm':POSTS,
       'physical_validation':False,'global_collision_detection':False,
       'pressure_rating':False,'mesh_manifold_checked':True,
       'notes':['Folgas verificadas analiticamente nos principais encaixes.',
                'Contatos de apoio/adesivo e volumes esquemáticos não constituem detecção global de colisão.',
                'Espiras toroidais individuais fechadas ilustram percurso; conexões elétricas seguem esquema separado.'],
    }
    for k,v in checks.items():
        if 'clearance' in k or 'ligament' in k:assert v>0,(k,v)
    assert len(set(p['id'] for p in PARTS))==len(PARTS)
    (OUT/'validacao_mesh.json').write_text(json.dumps(CHECKS,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'validacao_montagem.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'parametros.json').write_text(json.dumps(P,ensure_ascii=False,indent=2),encoding='utf-8')

def write_bom():
    # A length repeated at two levels requires eight spacers, not four.
    for row in BOM:
        if row['file'].startswith('espacador_'):
            row['quantity']=sum(p['source']==row['file'] for p in PARTS)
    hardware=[
       ('H01','Tirante nylon M5 × 231',4,'Nylon isolante','Comprar M5×250 e cortar231; conferir diâmetro real'),
       ('H02','Porca M5 AF8 × 4 nominal',8,'Nylon isolante','Comprar; medir altura'),
       ('H03','Arruela M5 Ø10/5,5 × 1',8,'Nylon isolante','Comprar; não adicionar arruelas intermediárias'),
       ('H04','Fixação carretel M3 × 31 nominal',8,'Nylon isolante','Comprar/comprimento útil ajustado ao aperto; porcas e arruelas pequenas Ø6'),
       ('H05','Par porca M3 e arruela Ø6',16,'Nylon isolante','2 pares por fixação; 16porcas+16arruelas; não formam anel metálico'),
       ('H06','Pés Ø16 × 8',4,'Borracha','Adesivos; posições XY ±155'),
       ('H07','Pilar do toroide Ø8 × 36,55',4,'Polímero isolante','Sobre tampa Z81 em azimutes3,75/93,75/183,75/273,75°; apoio colado e abraçadeira isolante'),
       ('H08','Cassete externo 20 × 10 × 24',16,'Polímero isolante','Azimutes22,5°+45k; entre tampas, colados/abraçados, longe dos tirantes'),
       ('H09','Haste axial Ø8 × 111',1,'Polímero isolante','Z12–123; sonda Hall Z123–127 apoiada na extremidade; fixar ao pedestal'),
       ('H10','Caixa ventilada externa 80 × 60 × 30',1,'Polímero isolante','Caixa comercial equivalente; adaptar furação dos conectores'),
       ('E01','Bobina principal 50 espiras R100',2,'Cobre esmaltado Ø1,0 / externo1,1','31,416m ideal por bobina + terminais/sobra; reservar35m por bobina'),
       ('E02','Receptor 20 espiras R35',1,'Cobre esmaltado Ø1,0 / externo1,1','4,398m ideal + terminais/sobra; reservar5,5m'),
       ('E03','Toroide 48 espiras R135/r8',1,'Cobre esmaltado Ø1,0 / externo1,1','2,413m ideal poloidal + conexões; reservar4m; ramo experimental separado'),
       ('E04','Fonte, proteção, driver, sensor e carga',1,'Eletrônica convencional','Valores e conexões definidos no projeto elétrico; modelos geométricos genéricos'),
       ('E05','Fita, verniz e abraçadeiras isolantes',1,'Material compatível com fio e tubo','Fixação sem peças condutoras que fechem espiras ao redor do eixo'),
       ('E06','Camada isolante toroide 0,95 mm',1,'Fita/enchimento isolante','Medir camada contínua: forma raio6,5→superfície7,45; centro fio8 com externo1,1'),
    ]
    for code,name,qty,mat,method in hardware:BOM.append({'code':code,'name':name,'quantity':qty,'material':mat,'file':'','method':method,'dimensions_mm':None})
    (OUT/'pecas.json').write_text(json.dumps(BOM,ensure_ascii=False,indent=2),encoding='utf-8')
    with (OUT/'pecas.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f,delimiter=';');w.writerow(['codigo','peca','quantidade','material','arquivo','fabricacao'])
        for row in BOM:w.writerow([row[k] for k in ['code','name','quantity','material','file','method']])

def main():
    build();validate();write_scene();write_bom()
    print(json.dumps({'parts':len(PARTS),'stl_files':len(UNIQUE),'mesh_verified':len(CHECKS),
                      'triangles':sum(len(p['faces'])//3 for p in PARTS),'directory':str(OUT)},indent=2))

if __name__=='__main__':main()
