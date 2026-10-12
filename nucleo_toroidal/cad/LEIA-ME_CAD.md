# CAD: bancada de duas bobinas circulares

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
