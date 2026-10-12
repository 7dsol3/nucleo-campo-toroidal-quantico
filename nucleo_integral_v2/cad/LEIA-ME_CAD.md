# Montagem integral V2

Esta é uma bancada eletromagnética instrumentada proposta com aparência inspirada
no pôster. Os módulos são bobinas, suportes isolantes, instrumentação em ar comum,
receptor por indução e caixa de controle convencional. As medidas são uma proposta
de engenharia para bancada, em milímetros; não são medidas deduzidas da imagem.
A escala de 10 m do pôster não foi adotada. Não há projeto de geração de energia
do vácuo, motor sem reação, wormhole, curvatura ou câmara de alta/baixa pressão.

## Arquivos

- `scene.js` e `scene.json`: montagem com IDs, nomes, grupos, cores, vértices,
  índices de triângulos, deslocamentos para vista explodida e função de cada peça.
- `montagem_integral.obj` + `.mtl`: montagem por grupos para Blender e CAD.
- `nucleo_integral.scad`: fonte paramétrica OpenSCAD dos módulos mecânicos e
  representação da montagem. Alterar `modo` para exportar peças individuais.
- 14 arquivos STL: sólidos mecânicos individuais fechados, com furos reais.
- `01_montagem_dimensional.svg` e `02_componentes_enrolamentos.svg`: desenhos
  vetoriais dimensionais; abrir em navegador ou importar em programa gráfico.
- `pecas.csv`/`.json`, `parametros.json`, `validacao_mesh.json` e
  `validacao_montagem.json`: peças, medidas e resultados das verificações.
- `gerar_integral.py`, `meshlib.py` e `gerar_desenhos.py`: geradores reprodutíveis
  em Python padrão. Rodar `py gerar_integral.py` e `py gerar_desenhos.py`.
- `revisar_mecanica.py` / `revisao_mecanica.json`: revisão independente de
  84 interfaces mecânicas identificadas usando a cena exportada; todas passaram.
  Rodar `py revisar_mecanica.py` após gerar a cena. Não é detector global de colisão.

## Medidas essenciais

Base isolante 360×360×12, face inferior em Z0. Bobinas circulares centradas em
Z65 e Z185: separação120, raio médio100, 50 espiras cada. Fio cobreØ1,0;
diâmetro externo isolado nominal1,1. Cinco camadas radiais de dez espiras axiais;
centros dos condutores R97,8/98,9/100/101,1/102,2. Envelope R97,25–102,75,
altura11; carretelØ220×15,4, flanges2, canal11,4, mangaØ190,5/194,5.

Tampas anularesØ340/248×4 em Z49–53,77–81,169–173,197–201. Quatro tirantes
isolantes M5×231 em R155 e azimutes45/135/225/315°, coordenadas X/Y±109,6016;
quatro furosØ5,5 por tampa e na base. Tirantes Z−5…226, porca inferior
Z−5…−1, arruela Z−1…0, arruela superior Z218…219, porca Z219…223.
EspaçadoresØ10/5,5: quatro×37, oito×15,4, quatro×88, quatro×17. A pilha real é
base12 + espaçador37 + tampa4 + ponte4,3 + espaçador15,4 + ponte4,3 + tampa4
+ espaçador88 + tampa4 + ponte4,3 + espaçador15,4 + ponte4,3 + tampa4
+ espaçador17, terminando em Z218. As pontes entram na pilha; os espaçadores
não atravessam seus furosØ5,5. Não acrescentar
arruelas intermediárias sem recalcular alturas.

Dezesseis pontes de56×12×4,3 ligam R104…160. FurosØ3,4 emR107 eØ5,5 emR155,
distância entre centros48. Nos módulos inferiores: pontesZ53…57,3 e72,7…77;
somar120 para as superiores. Os carretéis tocam as pontes em suas faces externas
Z57,3/72,7 e177,3/192,7. Oito fixaçõesM3×31, dezesseis porcas e dezesseis
arruelasØ6/3,4×0,5; porcasM3 com AF5,5, altura2,4 nominal. Comprar hardware;
as roscas no OBJ/STL são simplificadas e não servem para imprimir parafusos.

Tubo transparenteØ54/50×198 emZ22…220, topo aberto. PedestalØ70/10×10 em
Z12…22; o tubo apoia nessa face. ColaresØ70/54,6×6 emZ22…28 e214…220.
Folga diametral0,6 exige adesivo compatível ou ajuste após calibração; não há
vedação. A coluna contém ar comum; não aplicar vácuo ou pressão. Haste isolante
Ø8×111 emZ12…123 apoia sondaHall esquemática emZ123…127. Não existe feixe de
energia na coluna.
O furoØ10 do pedestal deixa folga radial1 para a hasteØ8: centralizar com
calços isolantes e adesivo compatível antes de fixar a sonda; registrar a posição.

Receptor20espiras R35, centroZ125, cobreØ1/externo1,1; quatro camadas×cinco
espiras. EnvelopeR32,8…37,2 eZ122,25…127,75. CarretelØ80/62×12 emZ119…131,
flanges3, canal6, mangaØ65. ColarØ62/54,6×2 emZ115…117, com quatro linguetas
radiais9×6×2 emZ117…119, coladas sobre o colar deØ62/54,6×2 emZ115…117.
As linguetas tocam o colar emZ117 e o flange do receptor emZ119, sem atravessá-los.
Não se trata de uma peça fabricável
para capturar energia de vácuo: é uma bobina receptora convencional ligada à carga.

Toroide auxiliar separado: Rmaior135, forma isolante com raio menor6,5, centro
Z125. Aplicar camada isolante medida0,95 até superfície7,45; enrolar48espiras
poloidais de fioexterno1,1, centros em raio menor8. O pacote não modela conexões
helicoidais, pontas e verniz; as espiras separadas do OBJ são uma representação
do percurso. Quatro pilaresØ8×36,55 apoiados na tampaZ81, azimutes3,75/93,75/
183,75/273,75°, terminam no envoltório emZ117,55 entre espiras. Aderir e fixar
com abraçadeiras isolantes. Este ramo é opcional, alimentado externamente e
medido em separado; não implica geometria quântica ou campo relativístico.

Os16cassetes externos20×10×24 ocupam azimutes22,5°+45k, entre tampas e longe
dos tirantes. São opcionais; colar/abraçar às faces das tampas e guiar os cabos.

Caixa ventilada eletrônica externa80×60×30, X−165…−85, Y−165…−105,
Z12…42. Placas, conector e resistor são volumes genéricos, sem pinagem de
fabricante no CAD. Adaptar caixa comercial e furação à eletrônica do projeto.
Sondas térmicas ficam X102,75…106,75, Y±2, Zcentro±2, em contato externo
ao envelope de cada bobina; fixar com fita isolante. Cabos não são trajetórias
CAD definitivas: fixá-los fora das espiras, com alívio de tração.

## Fabricação e ordem de montagem

1. Cortar base em chapa isolante plana360×360×12; fazer quatro furosØ5,5
   nas coordenadas acima. Colar quatro pésØ16×8 emX/Y±155. Conferir planicidade.
2. Fabricar tampas, pontes e carretéis. Tampas inteirasØ340 exigem mesa útil
   ≥Ø346 com brim3; recomendado≥350 ou CNC. Para base impressa, mesa útil
   ≥366×366; preferir chapa. Esta revisão não contém juntas de segmentação:
   não recortar tampas ou carretéis para impressora menor sem redesenhar juntas.
3. CarretéisØ220 precisam de mesa útil≥Ø226. Flange superior requer suporte
   removível sob o balanço; remover completamente suportes do canal antes de
   enrolar. Analisar o fatiamento: os modelos não foram impressos/fatiados.
4. Alvo dimensional impresso±0,3; tubos/espaçadores faceados±0,1. Acabar furos
   com brocaØ3,4/5,5; evitar aperto que esmague polímero ou trincar PMMA.
   Confirmar diâmetro externo real do fio. Se exceder1,1, recalcular canais,
   envelopes, bobinas e folgas antes da fabricação.
5. Enrolar bobinas principais e receptor segundo as camadas acima. Reservar
   aproximadamente35m por bobina principal,5,5m receptor,4m toroide incluindo
   terminais/sobras. Contar espiras, medir continuidade e resistência.
6. Montar tirantes, espaçadores e tampas na pilha indicada; incluir pontes
   inferiores e superiores de cada carretel na própria montagem. FixaçõesM3
   prendem ponte/carretel/ponte; tirantesM5 passam nas pontes e tampas, sem
   fazer anéis metálicos completos que possam atuar como espiras em curto.
7. Instalar pedestal, tubo, colares, haste e receptor com adesivo compatível.
   Linguetas e pilares colados exigem ensaio mecânico leve antes de energizar.
   Instalar o toroide opcional sobre a tampa inferior; confirmar o alinhamento
   das quatro bases entre espiras. Manter a coluna aberta.
8. Instalar caixa de controle, sondas e cabos. Conferir separação dos centros,
   resistência e isolamento dos enrolamentos, fixação, afastamentos e alívio
   dos cabos. Seguir limite de corrente/temperatura e esquema do projeto elétrico.

## Alcance da validação

Todas as malhas geradas passam por checagem de arestas usadas duas vezes,
orientação consistente e volume positivo. Folgas analíticas selecionadas:
cobre/carretel/tampas/pontes; toroide/tirantes; tubo/receptor; caixa/tampa inferior;
furos/tirantes e margens de montagem. `validacao_montagem.json` registra valores.
Não foi executada detecção global de colisões, análise de tensão mecânica,
fatiamento, ensaio físico de impressão, validação térmica, classificação de
pressão ou certificação de segurança. Contatos nominais/cola/abraçadeiras e
dimensões de hardware comprado ainda precisam ser ajustados após inspeção real.
As peças eletrônicas e de organização são referências geométricas convencionais.
Os STL são malhas trianguladas; não há STEP/B-rep nativo nesta entrega.

## Mapeamento da imagem para peças reais

| Nome na imagem | Realização nesta bancada |
|---|---|
| Anel de confinamento | Carcaças e tampas isolantes de proteção/apoio |
| Campos superior/inferior | Campos magnéticos de bobinas alimentadas externamente |
| Câmara de interferência | Tubo aberto de instrumentação em ar comum |
| Núcleo de vácuo estável | Não implementado; imagem não fornece projeto/validação |
| Rede de campo quântico | Não implementada; cabos e sensores convencionais |
| Matriz de conversão | Receptor por indução e resistor/carga convencional |
| Anel de estabilização | Apoio mecânico, tirantes e aquisição/controle eletrônico |
| Fluxo de informação | Medidas elétricas e registro digital de sensores |
| Geometria toroidal | Bobina auxiliar toroidal convencional, medida separadamente |
| Saída de propulsão/curvatura | Não implementada; sem mecanismo físico demonstrado |
