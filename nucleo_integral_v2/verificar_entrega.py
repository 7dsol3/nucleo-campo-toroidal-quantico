"""Valida artefatos e empacota V2; separa verificações digitais de ensaio físico."""
from pathlib import Path
from html.parser import HTMLParser
from xml.etree import ElementTree as ET
import csv,json,struct,zipfile,hashlib
import pymupdf
from docx import Document

ROOT=Path(__file__).resolve().parent

class Links(HTMLParser):
    def __init__(self):super().__init__();self.urls=[]
    def handle_starttag(self,tag,attrs):
        for name,value in attrs:
            if name in('href','src') and value and not value.startswith(('http:','https:','#','data:')):self.urls.append(value)

def main():
    scene=json.loads((ROOT/'cad/scene.json').read_text(encoding='utf-8'))
    mesh=json.loads((ROOT/'cad/validacao_mesh.json').read_text(encoding='utf-8'))
    mechanical=json.loads((ROOT/'cad/revisao_mecanica.json').read_text(encoding='utf-8'))
    model=json.loads((ROOT/'simulacao/outputs/validacao_modelo.json').read_text(encoding='utf-8'))
    browser=json.loads((ROOT/'validacao_navegador.json').read_text(encoding='utf-8'))
    assert browser['all_passed']
    physics_checks=model.get('checks',model.get('tests',[]))
    assert physics_checks and all(c['passed'] for c in physics_checks)
    assert mechanical['failed']==0
    assert all(m['boundary_edges']==0 and m['nonmanifold_edges']==0 and m['consistent_orientation'] and m['volume_mm3']>0 for m in mesh.values())
    assert len(scene['parts'])==len({p['id'] for p in scene['parts']})
    for p in scene['parts']:
        assert len(p['vertices'])%3==0 and len(p['faces'])%3==0
        assert all(0<=i<len(p['vertices'])//3 for i in p['faces'])
    stls=[]
    for f in sorted((ROOT/'cad').glob('*.stl')):
        raw=f.read_bytes();n=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*n
        stls.append({'file':str(f.relative_to(ROOT)),'triangles':n})
    for f in ROOT.rglob('*.svg'):ET.parse(f)
    parser=Links();parser.feed((ROOT/'index.html').read_text(encoding='utf-8'))
    missing=[u for u in parser.urls if not (ROOT/u).exists() and u!='validacao_entrega.json']
    assert not missing,missing
    pdf=pymupdf.open(ROOT/'Projeto_Integral.pdf');text='\n'.join(p.get_text() for p in pdf)
    assert len(pdf)>6 and len(text)>20000
    assert all(x in text for x in ['73,483675','185,445692','24,054656','0,735861','0,0032689%'])
    assert 'Sem ensaio físico' in text or 'Nenhum ensaio físico' in text
    pdf[0].get_pixmap(matrix=pymupdf.Matrix(1.1,1.1)).save(ROOT/'Previa_Projeto_PDF.png')
    pdf[-1].get_pixmap(matrix=pymupdf.Matrix(1.1,1.1)).save(ROOT/'Previa_BOM_PDF.png')
    (ROOT/'Projeto_Integral.txt').write_text(text,encoding='utf-8')
    doc=Document(ROOT/'Projeto_Integral.docx');assert len(doc.tables)>=5
    with (ROOT/'lista_completa_pecas.csv').open(encoding='utf-8-sig') as f:bom=list(csv.DictReader(f,delimiter=';'))
    for row in bom:
        assert not row['arquivo'] or (ROOT/'cad'/row['arquivo']).exists()
    info={'date':'2026-10-12','scope':'Geometria integral proposta e simulação clássica; nenhum hardware fabricado ou medido.',
          'all_digital_checks_passed':True,'cad_parts':len(scene['parts']),'cad_groups':len({p['group'] for p in scene['parts']}),
          'verified_closed_meshes':len(mesh),'stl_files':len(stls),'critical_mechanical_interfaces_passed':mechanical['passed'],
          'physics_and_parity_checks_passed':len(physics_checks),'browser_checks_passed':browser['check_count'],
          'pdf_pages':len(pdf),'pdf_text_characters':len(text),'bom_rows':len(bom),'missing_local_links':missing,
          'stl_binary_sizes_valid':True,'svg_xml_valid':True,
          'not_performed':['Fabricação/ensaio físico','Renderização CLI OpenSCAD','Detecção global de todas as colisões','Análise estrutural/térmica/FEM','PCB e amplificadores físicos validados','Comprovação dos efeitos quânticos/gravitacionais do pôster']}
    (ROOT/'validacao_entrega.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    files=[f for f in sorted(ROOT.rglob('*')) if f.is_file() and '__pycache__' not in f.parts]
    hashes=[hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.relative_to(ROOT).as_posix() for f in files if f.name!='SHA256SUMS.txt']
    (ROOT/'SHA256SUMS.txt').write_text('\n'.join(hashes)+'\n',encoding='utf-8')
    archive=ROOT.parent/'Nucleo_Integral_V2.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for f in sorted(ROOT.rglob('*')):
            if f.is_file() and '__pycache__' not in f.parts:z.write(f,arcname=Path('nucleo_integral_v2')/f.relative_to(ROOT))
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    print(json.dumps({**{k:info[k] for k in ['cad_parts','stl_files','critical_mechanical_interfaces_passed','physics_and_parity_checks_passed','browser_checks_passed','pdf_pages']},'archive_bytes':archive.stat().st_size}))

if __name__=='__main__':main()
