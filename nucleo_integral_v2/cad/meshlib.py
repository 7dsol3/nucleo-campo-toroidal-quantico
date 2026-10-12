from collections import Counter
import math, struct
TAU=2*math.pi
ANGLES=[(45+90*k)*math.pi/180 for k in range(4)]
CENTERS=[(107*math.cos(a),107*math.sin(a)) for a in ANGLES]
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


