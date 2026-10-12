"""Render montagem.obj to a z-buffered PNG using Python stdlib only."""
from pathlib import Path
import math, struct, zlib

ROOT=Path(__file__).resolve().parent
W,H=1000,800
COLORS={'plastico':(73,88,105),'cobre':(199,112,48),'nylon':(223,221,199),
        'base':(144,173,187),'borracha':(37,41,47)}
SQ=math.sqrt(0.5); SN=math.sin(math.radians(28)); CS=math.cos(math.radians(28))

def project(v):
    x,y,z=v; a=(x+y)*SQ
    return ((x-y)*SQ,a*SN-z*CS,a*CS+z*SN)

def render():
    verts=[]; faces=[]; material='plastico'
    for line in (ROOT/'montagem.obj').read_text().splitlines():
        row=line.split()
        if not row: continue
        if row[0]=='v': verts.append(tuple(map(float,row[1:4])))
        elif row[0]=='usemtl': material=row[1]
        elif row[0]=='f': faces.append((tuple(int(v)-1 for v in row[1:]),material))
    p=[project(v) for v in verts]
    lo=[min(v[i] for v in p) for i in range(2)]
    hi=[max(v[i] for v in p) for i in range(2)]
    scale=min((W-160)/(hi[0]-lo[0]),(H-140)/(hi[1]-lo[1]))
    projected=[((x-(lo[0]+hi[0])/2)*scale+W/2,
                (y-(lo[1]+hi[1])/2)*scale+H/2,z) for x,y,z in p]
    rgb=bytearray(bytes((247,249,251))*W*H)
    zb=[float('-inf')]*(W*H)
    for face,material in faces:
        pa,pb,pc=[projected[i] for i in face]
        ax,ay,az=pa; bx,by,bz=pb; cx,cy,cz=pc
        det=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
        # Projected front faces are clockwise in downward-positive screen Y.
        if det>=-1e-10: continue
        va,vb,vc=[verts[i] for i in face]
        ab=tuple(vb[i]-va[i] for i in range(3)); ac=tuple(vc[i]-va[i] for i in range(3))
        n=(ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0])
        norm=math.sqrt(sum(x*x for x in n))
        light=max(0,(0.2*n[0]-0.3*n[1]+n[2])/(norm*math.sqrt(1.13)))
        shade=0.55+0.45*light
        color=bytes(max(0,min(255,round(ch*shade))) for ch in COLORS[material])
        xmin=max(0,math.floor(min(ax,bx,cx))); xmax=min(W-1,math.ceil(max(ax,bx,cx)))
        ymin=max(0,math.floor(min(ay,by,cy))); ymax=min(H-1,math.ceil(max(ay,by,cy)))
        for y in range(ymin,ymax+1):
            for x in range(xmin,xmax+1):
                px,py=x+0.5,y+0.5
                u=((by-cy)*(px-cx)+(cx-bx)*(py-cy))/det
                v=((cy-ay)*(px-cx)+(ax-cx)*(py-cy))/det
                w=1-u-v
                if min(u,v,w)<-1e-8: continue
                depth=u*az+v*bz+w*cz; index=y*W+x
                if depth>zb[index]: zb[index]=depth; rgb[index*3:index*3+3]=color
    def chunk(kind,data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    pixels=b''.join(b'\0'+rgb[y*W*3:(y+1)*W*3] for y in range(H))
    png=(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0))+
         chunk(b'tEXt',b'Description\0Dimensional bench: two externally-powered circular coils. CAD units millimeters.')+
         chunk(b'IDAT',zlib.compress(pixels,9))+chunk(b'IEND',b''))
    (ROOT/'previa_3d.png').write_bytes(png)
    print(f'Wrote previa_3d.png ({len(png)} bytes; {len(faces)} source triangles)')

if __name__=='__main__': render()
