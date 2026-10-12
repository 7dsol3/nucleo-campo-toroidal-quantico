"""Generate dimensioned, manifold demonstration-coil CAD using only stdlib.

Dimensions: millimetres. Meshes represent mechanics, not a vacuum energy device.
Run: py gerar_cad.py
"""
from pathlib import Path
import csv, json, math, struct
from collections import Counter

OUT = Path(__file__).resolve().parent
TAU = 2 * math.pi
P = dict(base_width=260.0, base_thickness=8.0,
         coil_radius_mean=100.0, turns_per_coil=50, wire_bare_diameter=1.0,
         wire_insulated_diameter=1.1, winding_radial=5.5, winding_axial=11.0,
         spool_inner_radius=94.0, sleeve_inner_radius=95.25,
         sleeve_outer_radius=97.25, flange_outer_radius=110.0,
         flange_thickness=2.0, winding_gap=11.4, spool_height=15.4,
         coil_lower_z=60.0, coil_upper_z=160.0, mounting_radius=107.0,
         mounting_hole_diameter=3.4, spacer_outer_diameter=6.0,
         spacer_lower_length=44.3, spacer_middle_length=84.6,
         threaded_rod_diameter=3.0, threaded_rod_length=180.0,
         threaded_rod_start_z=-5.0, washer_outer_diameter=6.0,
         washer_thickness=0.5, nut_height=2.4, rubber_foot_height=6.0)
SEG = 256
ANGLES = [(45+90*k)*math.pi/180 for k in range(4)]
CENTERS = [(107*math.cos(a),107*math.sin(a)) for a in ANGLES]


def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def sub(a,b): return tuple(a[i]-b[i] for i in range(3))
def dot(a,b): return sum(a[i]*b[i] for i in range(3))
def polar(r,a,z=0): return (r*math.cos(a),r*math.sin(a),z)


class Mesh:
    def __init__(self,name):
        self.name=name; self.v=[]; self.f=[]; self._index={}
    def vertex(self,p):
        p=tuple(round(float(x),8) for x in p)
        if p not in self._index:
            self._index[p]=len(self.v); self.v.append(p)
        return self._index[p]
    def tri(self,a,b,c,normal):
        n=cross(sub(b,a),sub(c,a))
        if dot(n,normal)<0: b,c=c,b
        if sum(x*x for x in n)<1e-18: raise ValueError('Degenerate triangle')
        self.f.append(tuple(self.vertex(p) for p in (a,b,c)))
    def quad(self,a,b,c,d,normal):
        self.tri(a,b,c,normal); self.tri(a,c,d,normal)
    def moved(self,name,dx=0,dy=0,dz=0):
        m=Mesh(name); m.v=[(x+dx,y+dy,z+dz) for x,y,z in self.v]; m.f=list(self.f)
        return m
    def verify(self):
        edges=Counter(); directed=Counter()
        for f in self.f:
            for a,b in zip(f,f[1:]+f[:1]):
                edges[tuple(sorted((a,b)))]+=1; directed[(a,b)]+=1
        bad=[e for e,n in edges.items() if n!=2]
        orient=[e for e in edges if directed[e]!=directed[(e[1],e[0])]]
        vol=sum(dot(self.v[a],cross(self.v[b],self.v[c]))/6 for a,b,c in self.f)
        if bad or orient or vol<=0:
            raise ValueError(f'{self.name}: bad_edges={len(bad)}, orientation={len(orient)}, volume={vol}')
        return dict(vertices=len(self.v),triangles=len(self.f),boundary_edges=0,
                    nonmanifold_edges=0,consistent_orientation=True,volume_mm3=round(vol,3),
                    bounds_mm=[[min(p[i] for p in self.v) for i in range(3)],
                               [max(p[i] for p in self.v) for i in range(3)]])
    def stl(self,path):
        with path.open('wb') as f:
            f.write((self.name+'; units mm').encode('ascii')[:80].ljust(80,b' '))
            f.write(struct.pack('<I',len(self.f)))
            for a,b,c in self.f:
                va,vb,vc=self.v[a],self.v[b],self.v[c]
                n=cross(sub(vb,va),sub(vc,va)); length=math.sqrt(dot(n,n))
                f.write(struct.pack('<12fH',*(x/length for x in n),*va,*vb,*vc,0))


def planar_ring(mesh,rs,angles,z,normal,skip_sleeve=False):
    for ri,ro in zip(rs,rs[1:]):
        if skip_sleeve and ri==95.25 and ro==97.25: continue
        for a,b in zip(angles,angles[1:]):
            mesh.quad(polar(ri,a,z),polar(ro,a,z),polar(ro,b,z),polar(ri,b,z),normal)


def wall(mesh,points,z0,z1,inward=False,center=(0,0)):
    for p,q in zip(points,points[1:]+points[:1]):
        n=((p[0]+q[0])/2-center[0],(p[1]+q[1])/2-center[1],0)
        if inward: n=tuple(-x for x in n)
        mesh.quad((*p,z0),(*q,z0),(*q,z1),(*p,z1),n)


def rectangle_loop(x0,x1,y0,y1,n=12):
    # Counterclockwise physical XY boundary; corners occur exactly once.
    pts=[]
    for i in range(n): pts.append((x0+(x1-x0)*i/n,y0))
    for i in range(n): pts.append((x1,y0+(y1-y0)*i/n))
    for i in range(n): pts.append((x1-(x1-x0)*i/n,y1))
    for i in range(n): pts.append((x0,y1-(y1-y0)*i/n))
    return pts


def patch_with_hole(mesh,outer,center,radius,z,normal):
    inner=[]
    for x,y in outer:
        dx,dy=x-center[0],y-center[1]; s=radius/math.hypot(dx,dy)
        inner.append((center[0]+dx*s,center[1]+dy*s))
    for i in range(len(outer)):
        j=(i+1)%len(outer)
        mesh.quad((*outer[i],z),(*outer[j],z),(*inner[j],z),(*inner[i],z),normal)
    return inner


def bobbin():
    m=Mesh('bobina_suporte_OD220_H15p4')
    # Four polar rectangle patches contain circular mount holes. Elsewhere,
    # polar annular strips join their boundaries without T-junctions.
    delta=2*math.pi/180; subdivisions=12
    special=[]
    for alpha in ANGLES:
        special.extend(alpha-delta+2*delta*i/subdivisions for i in range(subdivisions+1))
    # Uniform exterior intervals bounded by the patch corners.
    angles=[0.0,math.pi/2,math.pi,3*math.pi/2,TAU]+special
    for k in range(4):
        start=ANGLES[k]+delta
        end=(ANGLES[(k+1)%4]-delta)+(TAU if k==3 else 0)
        for i in range(1,53): angles.append((start+(end-start)*i/53)%TAU)
    angles=sorted(set(round(a,12) for a in angles))
    angles[0]=0.0; angles[-1]=TAU
    rs=[94.0,95.25,97.25,104.0]
    zsurfaces=[(0,-1,False),(2,1,True),(13.4,-1,True),(15.4,1,False)]
    for z,n,skip in zsurfaces:
        planar_ring(m,rs,angles,z,(0,0,n),skip)
        for a,b in zip(angles,angles[1:]):
            mid=(a+b)/2
            in_patch=any(abs(math.atan2(math.sin(mid-alpha),math.cos(mid-alpha)))<delta for alpha in ANGLES)
            if not in_patch:
                for i in range(subdivisions):
                    ri=104+6*i/subdivisions; ro=104+6*(i+1)/subdivisions
                    m.quad(polar(ri,a,z),polar(ro,a,z),polar(ro,b,z),polar(ri,b,z),(0,0,n))
        for alpha,center in zip(ANGLES,CENTERS):
            # Same exact angles as the inner strip, to maintain shared vertices.
            al=[a for a in angles if alpha-delta-1e-10<=a<=alpha+delta+1e-10]
            low,high=al[0],al[-1]
            outer=[]
            # Rectangle CCW in (radius,angle) coordinates.
            for i in range(subdivisions): outer.append(polar(104+6*i/subdivisions,low)[:2])
            for a in al[:-1]: outer.append(polar(110,a)[:2])
            for i in range(subdivisions): outer.append(polar(110-6*i/subdivisions,high)[:2])
            for a in reversed(al[1:]): outer.append(polar(104,a)[:2])
            inner=patch_with_hole(m,outer,center,1.7,z,(0,0,n))
            if z==0: wall(m,inner,0,2,True,center)
            if z==13.4: wall(m,inner,13.4,15.4,True,center)
    # Radius110 wall needs boundary vertices from hole-patch arc plus exterior.
    pts94=[polar(94,a)[:2] for a in angles[:-1]]
    pts110=[polar(110,a)[:2] for a in angles[:-1]]
    for lo,hi in [(0,2),(13.4,15.4)]:
        wall(m,pts94,lo,hi,True); wall(m,pts110,lo,hi)
    wall(m,[polar(95.25,a)[:2] for a in angles[:-1]],2,13.4,True)
    wall(m,[polar(97.25,a)[:2] for a in angles[:-1]],2,13.4)
    return m


def base():
    m=Mesh('base_260x260x8')
    c=107/math.sqrt(2); coords=[-130,-c-3,-c+3,c-3,c+3,130]
    outer_edges=[]
    for ix in range(len(coords)-1):
        for iy in range(len(coords)-1):
            x0,x1=coords[ix:ix+2]; y0,y1=coords[iy:iy+2]
            loop=rectangle_loop(x0,x1,y0,y1)
            hole=(ix in (1,3) and iy in (1,3))
            for z,n in [(0,-1),(8,1)]:
                if hole:
                    center=((x0+x1)/2,(y0+y1)/2)
                    inside=patch_with_hole(m,loop,center,1.7,z,(0,0,n))
                    if z==0: wall(m,inside,0,8,True,center)
                else:
                    center=((x0+x1)/2,(y0+y1)/2,z)
                    for a,b in zip(loop,loop[1:]+loop[:1]): m.tri(center,(*a,z),(*b,z),(0,0,n))
            for a,b in zip(loop,loop[1:]+loop[:1]):
                if ((a[0]==b[0] and abs(a[0])==130) or (a[1]==b[1] and abs(a[1])==130)):
                    normal=((a[0]+b[0])/2,(a[1]+b[1])/2,0)
                    m.quad((*a,0),(*b,0),(*b,8),(*a,8),normal)
    return m


def tube(name,ro,ri,h,n=64):
    m=Mesh(name); angles=[TAU*i/n for i in range(n+1)]
    planar_ring(m,[ri,ro],angles,0,(0,0,-1)); planar_ring(m,[ri,ro],angles,h,(0,0,1))
    wall(m,[polar(ro,a)[:2] for a in angles[:-1]],0,h)
    wall(m,[polar(ri,a)[:2] for a in angles[:-1]],0,h,True)
    return m


def cylinder(name,r,h,n=64):
    m=Mesh(name); pts=[polar(r,TAU*i/n)[:2] for i in range(n)]
    for z,nz in [(0,-1),(h,1)]:
        for a,b in zip(pts,pts[1:]+pts[:1]): m.tri((0,0,z),(*a,z),(*b,z),(0,0,nz))
    wall(m,pts,0,h); return m


def hexnut():
    # Hexagonal AF5.5 body, circular bore. Threads deliberately schematic.
    m=Mesh('porca_M3_AF5p5_H2p4'); ro=5.5/math.sqrt(3)
    outer=[]
    for k in range(6):
        a=TAU*k/6; b=TAU*(k+1)/6
        va=polar(ro,a)[:2]; vb=polar(ro,b)[:2]
        for j in range(8): outer.append(tuple(va[i]+(vb[i]-va[i])*j/8 for i in range(2)))
    for z,n in [(0,-1),(2.4,1)]:
        inner=patch_with_hole(m,outer,(0,0),1.5,z,(0,0,n))
        if z==0: wall(m,inner,0,2.4,True)
    wall(m,outer,0,2.4); return m


def toroidal_pack():
    # Visual winding envelope, NOT fifty separate conductors and NOT a
    # toroidal solenoid. Physical turns circulate around the main Z axis.
    return tube('envelope_cobre_50_espiras',102.75,97.25,11.0,256)


def write_obj(groups):
    materials=dict(plastico=(0.2,0.25,0.29),cobre=(0.78,0.32,0.12),
                   nylon=(0.85,0.89,0.82),base=(0.65,0.74,0.8),borracha=(0.08,0.09,0.11))
    with (OUT/'montagem.mtl').open('w',encoding='utf-8') as f:
        for name,color in materials.items():
            f.write(f'newmtl {name}\nKd {color[0]} {color[1]} {color[2]}\nKa 0.08 0.08 0.08\nNs 20\n\n')
    with (OUT/'montagem.obj').open('w',encoding='utf-8') as f:
        f.write('# Units: mm. Mechanical visualization of externally powered circular coils.\nmtllib montagem.mtl\n')
        index=1
        for mesh,mat in groups:
            f.write(f'g {mesh.name}\nusemtl {mat}\n')
            for x,y,z in mesh.v: f.write(f'v {x:.8f} {y:.8f} {z:.8f}\n')
            for face in mesh.f: f.write('f '+' '.join(str(index+i) for i in face)+'\n')
            index+=len(mesh.v)


SCAD=r'''// Bancada de duas bobinas circulares: unidades mm.
// Nenhuma previsão de energia de vácuo, propulsão ou curvatura do espaço-tempo.
// Espiras azimutais: NÃO é um solenoide toroidal. Roscas simplificadas.
$fn=128;
modo="montagem"; // montagem, bobina, base, espacador_inferior, espacador_meio
R=100; d_fio=1.1; N=50;
raio_flange=110; raio_furos=107; d_furo=3.4;
esp_flange=2; gap=11.4; h_bobina=2*esp_flange+gap;
centro_z=[60,160];
h_base=8; lado_base=260;
h_esp_inf=centro_z[0]-h_bobina/2-h_base;
h_esp_meio=centro_z[1]-centro_z[0]-h_bobina;
module anel(ri,ro,h) { difference(){cylinder(h=h,r=ro);translate([0,0,-0.1])cylinder(h=h+0.2,r=ri);} }
module furos(h){for(a=[45:90:315])translate([raio_furos*cos(a),raio_furos*sin(a),-0.1])cylinder(h=h+0.2,d=d_furo);}
module bobina(){difference(){union(){anel(94,raio_flange,esp_flange);translate([0,0,esp_flange+gap])anel(94,raio_flange,esp_flange);translate([0,0,esp_flange])anel(95.25,97.25,gap);}furos(h_bobina);}}
module base(){difference(){translate([-lado_base/2,-lado_base/2,0])cube([lado_base,lado_base,h_base]);furos(h_base);}}
module espacador(h){anel(d_furo/2,3,h);}
module montagem(){
  color([0.65,0.74,0.8])base();
  for(z=centro_z){color([0.2,0.25,0.29])translate([0,0,z-h_bobina/2])bobina();color([0.78,0.32,0.12])translate([0,0,z-5.5])anel(97.25,102.75,11);}
  for(a=[45:90:315])translate([raio_furos*cos(a),raio_furos*sin(a),0]){
    color([0.85,0.89,0.82]){
      translate([0,0,8])espacador(h_esp_inf);
      translate([0,0,centro_z[0]+h_bobina/2])espacador(h_esp_meio);
      translate([0,0,-5])cylinder(h=180,d=3);
      for(z=[-0.5,centro_z[1]+h_bobina/2])translate([0,0,z])anel(1.7,3,0.5);
      for(z=[-2.9,centro_z[1]+h_bobina/2+0.5])translate([0,0,z])difference(){cylinder(h=2.4,r=5.5/sqrt(3),$fn=6);translate([0,0,-0.1])cylinder(h=2.6,d=3);}
    }
  }
  for(x=[-110,110],y=[-110,110])color([0.08,0.09,0.11])translate([x,y,-6])cylinder(h=6,d=12);
}
if(modo=="montagem")montagem();
if(modo=="bobina")bobina();
if(modo=="base")base();
if(modo=="espacador_inferior")espacador(h_esp_inf);
if(modo=="espacador_meio")espacador(h_esp_meio);
'''


def drawing():
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1060" viewBox="0 0 1400 1060">',
         '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse"><path d="M0,0 L8,4 L0,8 z" fill="#155e75"/></marker></defs>',
         '<style>text{font:16px Arial;fill:#182530}.title{font-size:26px;font-weight:bold}.small{font-size:13px}.part{fill:#e5ebef;stroke:#263744;stroke-width:1.5}.copper{fill:#bf713d;stroke:#713b1d;stroke-width:1}.dim{stroke:#155e75;stroke-width:1.3;fill:none;marker-start:url(#arrow);marker-end:url(#arrow)}.ext{stroke:#8fa8b6;stroke-width:1;stroke-dasharray:4 3}</style>',
         '<rect width="1400" height="1060" fill="white"/>',
         '<text x="35" y="42" class="title">Bancada de duas bobinas circulares — desenho dimensional</text>',
         '<text x="35" y="70">Todas as medidas em mm • referência mecânica, não projeto de energia de vácuo • revisão A</text>']
    def line(x1,y1,x2,y2,cls='ext'): svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}"/>')
    def text(x,y,t,cl=''): svg.append(f'<text x="{x}" y="{y}" class="{cl}">{t}</text>')
    def rect(x,y,w,h,cls='part'): svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="{cls}"/>')
    def circle(cx,cy,r,cls='part'): svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" class="{cls}"/>')
    # Plan, 1.6 pixels/mm.
    s=1.6; cx,cy=260,335
    text(52,107,'VISTA SUPERIOR / base e furação')
    rect(cx-130*s,cy-130*s,260*s,260*s)
    circle(cx,cy,110*s);circle(cx,cy,102.75*s,'copper');circle(cx,cy,97.25*s)
    circle(cx,cy,95.25*s);circle(cx,cy,94*s)
    line(cx-210,cy,cx+210,cy);line(cx,cy-210,cx,cy+210)
    for x,y in CENTERS: circle(cx+x*s,cy-y*s,1.7*s)
    line(cx-130*s,568,cx+130*s,568,'dim');text(236,590,'260')
    line(510,cy-130*s,510,cy+130*s,'dim');text(517,cy+4,'260')
    line(cx-110*s,622,cx+110*s,622,'dim');text(221,645,'Ø220 flange')
    text(55,676,'4 × Ø3,4 em círculo Ø214, ângulos 45°, 135°, 225°, 315°')
    text(55,701,'Coordenadas dos centros: X / Y = ±75,6604')
    # Front view.
    s=2.0; fx,fy=850,530
    text(614,107,'VISTA FRONTAL / montagem e centros')
    y=lambda z:fy-z*s
    rect(fx-130*s,y(8),260*s,16)
    for xx in [-75.6604,75.6604]:
        rect(fx+xx*s-3,y(175),6,180*s)
        rect(fx+xx*s-6,y(52.3),12,44.3*s)
        rect(fx+xx*s-6,y(152.3),12,84.6*s)
    for z in (60,160):
        rect(fx-110*s,y(z-5.7),440,4)
        rect(fx-110*s,y(z+7.7),440,4)
        rect(fx-102.75*s,y(z+5.5),11,22,'copper')
        rect(fx+97.25*s,y(z+5.5),11,22,'copper')
        for sign in(-1,1):rect(fx+sign*95.25*s-(4 if sign<0 else 0),y(z+5.7),4,22.8)
        line(fx-235,y(z),fx+260,y(z));text(fx+268,y(z)+5,f'Z = {z}')
    for xx in(-110,110):rect(fx+xx*s-12,y(0),24,12)
    line(1220,y(60),1220,y(160),'dim');text(1228,y(110)+5,'100')
    line(1274,y(0),1274,y(60),'dim');text(1282,y(30)+5,'60')
    line(1220,y(0),1220,y(8),'dim');text(1228,y(4)+5,'8')
    text(620,583,'Z = 0 na face inferior da base; centros das bobinas em 60 e 160')
    text(620,608,'Espaçadores: 4 × 44,3 e 4 × 84,6; Ø6 / furo Ø3,4')
    text(620,633,'4 barras roscadas M3 × 180; vão do enrolamento 11,4')
    text(620,658,'Envelope do cobre: radial 5,5 × axial 11; 50 espiras por bobina')
    text(620,683,'Altura total nominal com pés: 181; base 260 × 260 × 8')
    # Local cross-section enlarged.
    text(45,759,'CORTE DO CARRETEL / seção radial ampliada')
    ox,oy,sc=90,940,12
    xr=lambda r:ox+(r-94)*sc
    yz=lambda z:oy-z*sc
    rect(xr(94),yz(2),16*sc,2*sc)
    rect(xr(94),yz(15.4),16*sc,2*sc)
    rect(xr(95.25),yz(13.4),2*sc,11.4*sc)
    rect(xr(97.25),yz(13.2),5.5*sc,11*sc,'copper')
    line(342,yz(0),342,yz(15.4),'dim');text(352,850,'15,4')
    line(405,yz(2),405,yz(13.4),'dim');text(414,850,'11,4')
    text(45,978,'Raios: flange 94…110; manga 95,25…97,25; cobre 97,25…102,75')
    text(45,1005,'Folga axial total 0,4; flange 2; bobina sem núcleo ferromagnético')
    text(590,751,'TOLERÂNCIAS E MONTAGEM', 'title')
    for i,t in enumerate([
        '• Furos Ø3,4: conferir / acabar com broca após impressão.',
        '• Peças impressas: alvo ±0,3; alturas dos tubos: alvo ±0,1.',
        '• Medir o fio esmaltado real; recalcular se o isolamento exceder 1,1.',
        '• Espaçadores e barras isolantes; não fechar anéis metálicos.',
        '• Base: chapa isolante cortada e furada; bobina: mesa útil ≥226.',
        '• 8 arruelas Ø6 × 0,5 e 8 porcas M3; aperto leve.',
        '• Fios, conectores e proteção elétrica definidos no projeto de bancada.',
        '• Roscas / filamento do cobre simplificados no modelo de visualização.']): text(590,783+i*28,t)
    svg.append('</svg>'); (OUT/'desenho_dimensional.svg').write_text('\n'.join(svg),encoding='utf-8')


README='''# CAD: bancada de duas bobinas circulares

Unidades: milímetros. Este conjunto é uma proposta de bancada mecânica para testar
campos magnéticos de duas bobinas circulares alimentadas externamente. O formato
visual remete à referência; ele NÃO demonstra energia do vácuo, antigravidade,
propulsão sem reação nem curvatura observável do espaço-tempo. O enrolamento é
azimutal em anéis circulares, não um solenoide toroidal.

## Arquivos

- `montagem.obj` + `montagem.mtl`: montagem em grupos e cores, importar em Blender.
- `previa_3d.png`: imagem do OBJ renderizada por `py render_preview.py`.
- `nucleo_bancada.scad`: modelo paramétrico para OpenSCAD; variável `modo` escolhe peça.
- `bobina_suporte_OD220_H15p4.stl`: imprimir 2 unidades, sem reduzir a escala.
- `base_260x260x8.stl`: referência para chapa de policarbonato; pode ser impressa
  apenas em equipamento com área útil adequada.
- `espacador_44p3.stl`, `espacador_84p6.stl`: 4 de cada, ou cortar tubo isolante.
- `desenho_dimensional.svg`: desenho técnico com medidas, abrir em navegador.
- `pecas.csv`, `parametros.json`, `validacao_mesh.json`, `validacao_montagem.json`:
  peças, parâmetros e verificações geométricas.
- `gerar_cad.py`: gerador reproduzível com Python padrão; rodar `py gerar_cad.py`.

## Geometria e encaixes

Base 260 × 260 × 8; face inferior em Z=0. Bobinas centradas em Z=60 e 160.
Cada carretel tem Ø220, altura 15,4, flanges de 2, vão de enrolamento de 11,4,
flange com abertura Ø188, manga Ø190,5 / Ø194,5. A manga une os flanges.
Enrolamento nominal com 50 espiras: 5 camadas radiais × 10 espiras axiais de
fio Ø1,0 cobre / Ø1,1 externo esmaltado. Envelope entre R=97,25 e 102,75,
Z do centro ±5,5. Há 0,4 de folga axial, não de tolerância do diâmetro do fio.
O raio médio da pilha é 100; as camadas físicas estão em R=97,8; 98,9; 100;
101,1; 102,2. Modelo de campo ideal deve informar se usa raio médio ou camadas.

As barras roscadas passam pelos 4 furos Ø3,4 em raio 107, nos ângulos
45°, 135°, 225°, 315°; X e Y = ±75,6604. A margem mínima do furo à borda
externa do flange é 1,3; a bancada é leve e requer aperto manual moderado.
Não usar este suporte para içamento, alta tensão ou cargas mecânicas.
Espaçadores Ø6 / Ø3,4 passam livres a 1,25 da borda do envelope do cobre.
Use apenas arruelas Ø6 no ponto de montagem; arruelas maiores exigem
revisão da geometria. Não use componentes condutores que formem uma espira
fechada ao redor do eixo durante ensaios com corrente variável.

## Fabricação e sequência

1. Cortar chapa isolante plana 260 × 260 × 8 e furar os quatro pontos Ø3,4.
   Colar quatro pés de borracha Ø12 × 6 nos cantos (±110, ±110).
2. Imprimir os 2 carretéis com eixo Z vertical, flange inferior na mesa,
   material isolante rígido, altura de camada adequada. O flange superior
   avança 12,75 radialmente da manga e EXIGE suporte removível no vão.
   Desativar suporte junto à manga conforme o fatiador; remover suportes e
   conferir o canal antes de enrolar. O modelo não foi fatiado nem impresso.
   Mesa útil mínima Ø226 com brim de 3; recomenda-se equipamento 230 ou maior.
   O desenho NÃO é segmentado: não imprimir partes cortadas sem redesenhar juntas.
3. Medir e registrar todas as dimensões, limpar os furos com broca Ø3,4 e
   verificar a passagem do fio no vão. Alvo peças impressas ±0,3, comprimentos
   dos espaçadores ±0,1; medir a separação dos centros da montagem concluída.
   A tolerância do furo pode ser corrigida no OpenSCAD após calibrar a impressora.
4. Medir o diâmetro isolado real do fio. Se ultrapassar 1,1, alterar o canal,
   a altura do carretel e os espaçadores antes de imprimir/enrolar. Enrolar
   10 voltas axiais por camada e 5 camadas. O fio é enrolado ao redor da manga
   circular pelo lado externo do carretel, com ele apoiado em gabarito giratório;
   os furos de montagem ficam fora da pilha de fio. Guiar e contar as voltas.
   Transições entre camadas, terminais, curvaturas e tolerâncias reais não são
   condutores detalhados no CAD. Reservar comprimento para as duas pontas e
   fixar com fita isolante / verniz adequado sem formar anel metálico fechado.
5. Para cada barra M3 × 180: porca inferior 2,4; arruela 0,5; base 8;
   espaçador 44,3; carretel inferior 15,4; espaçador 84,6; carretel superior
   15,4; arruela 0,5; porca superior 2,4. Não adicionar arruelas intermediárias,
   pois alteram as alturas. Apoiar a ponta inferior da barra em Z=-5. Ela termina
   em Z=175; flange superior em 167,7. As porcas ficam Z=-2,9…-0,5 e 168,2…170,6.
6. Conferir a distância entre os centros (100) e os terminais, continuidade,
   resistência e isolamento antes de ligar a eletrônica definida no projeto.

## Limites do arquivo

STL e OBJ são malhas aproximadas; as peças mecânicas individuais passam pela
verificação de arestas fechadas, orientação e volume positivo. O sólido cobre
no OBJ é um envelope visual, não um único condutor maciço a fabricar.
As roscas M3 são cilindros simplificados e as porcas são representações geométricas:
comprar o hardware. Materiais, resistência mecânica, impressão, aquecimento,
vibração e montagem real ainda exigem ensaios. Esta validação digital não
certifica fabricação ou desempenho físico. Nenhum STEP nativo é incluído.
'''


def main():
    parts=[bobbin(),base(),tube('espacador_44p3',3,1.7,44.3),tube('espacador_84p6',3,1.7,84.6)]
    validation={}
    for mesh in parts:
        validation[mesh.name]=mesh.verify(); mesh.stl(OUT/(mesh.name+'.stl'))
    rod=cylinder('barra_M3_180',1.5,180)
    washer=tube('arruela_OD6',3,1.7,0.5)
    nut=hexnut(); foot=cylinder('pe_borracha',6,6); copper=toroidal_pack()
    for mesh in [rod,washer,nut,foot,copper]: validation[mesh.name]=mesh.verify()
    groups=[(parts[1],'base')]
    for i,z in enumerate((60,160),1):
        groups.extend([(parts[0].moved(f'carretel_{i}',dz=z-7.7),'plastico'),
                       (copper.moved(f'enrolamento_{i}',dz=z-5.5),'cobre')])
    for i,(x,y) in enumerate(CENTERS,1):
        groups.extend([(parts[2].moved(f'esp_inf_{i}',x,y,8),'nylon'),
                       (parts[3].moved(f'esp_meio_{i}',x,y,67.7),'nylon'),
                       (rod.moved(f'barra_{i}',x,y,-5),'nylon')])
        for suffix,z in [('baixo',-0.5),('cima',167.7)]:groups.append((washer.moved(f'arruela_{suffix}_{i}',x,y,z),'nylon'))
        for suffix,z in [('baixo',-2.9),('cima',168.2)]:groups.append((nut.moved(f'porca_{suffix}_{i}',x,y,z),'nylon'))
    for i,(x,y) in enumerate([(x,y) for x in(-110,110) for y in(-110,110)],1):
        groups.append((foot.moved(f'pe_{i}',x,y,-6),'borracha'))
    write_obj(groups)
    (OUT/'nucleo_bancada.scad').write_text(SCAD,encoding='utf-8')
    (OUT/'parametros.json').write_text(json.dumps(P,indent=2),encoding='utf-8')
    (OUT/'validacao_mesh.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
    assembly_checks=dict(coil_center_separation_mm=100.0,
                         lower_coil_center_from_stack_mm=8+44.3+15.4/2,
                         upper_coil_center_from_stack_mm=8+44.3+15.4+84.6+15.4/2,
                         winding_axial_clearance_mm=round(11.4-11.0,4),
                         winding_to_spacer_radial_clearance_mm=107-3-102.75,
                         mounting_hole_outer_edge_ligament_mm=110-107-1.7,
                         top_flange_z_mm=167.7,rod_top_z_mm=175.0,
                         rod_above_upper_nut_mm=round(175-170.6,4),
                         total_height_including_feet_mm=181.0,
                         assembled_bounds_mm=[[-130,-130,-6],[130,130,175]],
                         assembly_groups=len(groups),
                         manufacturing_validation=False,
                         openscad_cli_validation=False)
    assert abs(assembly_checks['lower_coil_center_from_stack_mm']-60)<1e-8
    assert abs(assembly_checks['upper_coil_center_from_stack_mm']-160)<1e-8
    assert assembly_checks['winding_to_spacer_radial_clearance_mm']>0
    (OUT/'validacao_montagem.json').write_text(json.dumps(assembly_checks,indent=2),encoding='utf-8')
    (OUT/'LEIA-ME_CAD.md').write_text(README,encoding='utf-8')
    drawing()
    wire_length=TAU*100*50/1000
    rows=[
        ['B01','Base isolante',1,'Policarbonato','260 x 260 x 8; 4 furos Ø3,4','Cortar e furar chapa; STL de referência'],
        ['B02','Carretel circular',2,'Polímero isolante','Ø220 x 15,4; vão11,4; mangaØ190,5/194,5','STL; flange superior exige suporte removível'],
        ['B03','Espaçador inferior',4,'Nylon ou polímero isolante','Ø6 / Ø3,4 x44,3','Cortar tubo ou imprimir STL'],
        ['B04','Espaçador intermediário',4,'Nylon ou polímero isolante','Ø6 / Ø3,4 x84,6','Cortar tubo ou imprimir STL'],
        ['B05','Barra roscada',4,'Nylon','M3 x180','Comprar; rosca simplificada no OBJ'],
        ['B06','Porca',8,'Nylon','M3; AF5,5; altura nominal2,4','Conferir dimensões do fornecedor'],
        ['B07','Arruela',8,'Nylon','Ø6 / Ø3,4 x0,5','Não colocar entre carretéis e espaçadores'],
        ['B08','Pé adesivo',4,'Borracha','Ø12 x6','Colar em X/Y ±110'],
        ['E01','Enrolamento de cobre',2,'Cobre esmaltado','50 espiras; Ø1,0 cobre; Ø1,1 isolado',f'{wire_length:.3f} m ideal por bobina; comprar~35 m por bobina para pontas e sobra'],
        ['E02','Fixação do enrolamento',1,'Fita isolante / verniz','Adequado ao fio e à temperatura','Aplicar após medir e contar voltas'],
    ]
    with (OUT/'pecas.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f,delimiter=';'); writer.writerow(['codigo','peca','quantidade','material','medidas_mm','fabricacao_observacao']); writer.writerows(rows)
    print(json.dumps({'generated_files':[p.name for p in OUT.iterdir() if p.is_file()],
                      'assembly_groups':len(groups),'parts_validated':len(validation),
                      'wire_nominal_m_per_coil':round(wire_length,5)},indent=2))


if __name__=='__main__': main()
