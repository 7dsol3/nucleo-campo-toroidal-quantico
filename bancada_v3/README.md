# Bancada V3 — projeto elétrico, FEM e medição

Esta entrega complementa a montagem V2 com eletrônica especificada, cálculo 3D por elementos finitos efetivamente executado, captura de instrumentos, análise de formas de onda e firmware de controle CC. É documentação e software para construir e qualificar uma bancada; **não é uma bancada já fabricada ou medida**.

## Arquivos de uso direto

| Parte | Entrega |
|---|---|
| Manual consolidado | [Manual_Bancada_V3.pdf](Manual_Bancada_V3.pdf), [DOCX](Manual_Bancada_V3.docx) |
| Circuito, equipamentos, valores e limites | [eletronica/README.md](eletronica/README.md), [esquema.svg](eletronica/esquema.svg), [BOM.csv](eletronica/BOM.csv), [LIGACOES.md](eletronica/LIGACOES.md) |
| Caracterização para liberar cada ponto de operação | [eletronica/QUALIFICACAO.md](eletronica/QUALIFICACAO.md) |
| FEM tetraédrico 3D e resultados calculados | [fem/README.md](fem/README.md), [solver.py](fem/solver.py), [resultados.json](fem/outputs/resultados.json), [VTU](fem/outputs/fine_box060.vtu) |
| Aquisição PicoScope real, sem simulação de dispositivo | [aquisicao/README.md](aquisicao/README.md), [capturar_pico.py](aquisicao/capturar_pico.py) |
| Filtro de aquisição dimensionado | [aquisicao/FILTRO_ANTIALIAS.md](aquisicao/FILTRO_ANTIALIAS.md) |
| Calibração, potência assinada e comparação CA/CC | [medicoes/README.md](medicoes/README.md), [análise CA](medicoes/analisar.py), [análise CC e FEM](medicoes/analisar_cc.py) |
| Controle CC em Raspberry Pi Pico + MCP4725 | [controle/README.md](controle/README.md), [main.py](controle/main.py), [controlador.py](controle/controlador.py) |
| Pacote completo | [Nucleo_Bancada_V3.zip](../artifacts/Nucleo_Bancada_V3.zip) |

Os desenhos/STL mecânicos continuam na [V2](../nucleo_integral_v2/cad/LEIA-ME_CAD.md). Os documentos V1/V2 registram entregas anteriores; as escolhas de eletrônica desta V3 complementam a antiga lista de instrumentos a selecionar. O nome artístico do repositório não transforma o modelo em um dispositivo quântico.

## O que foi efetivamente executado

- Solver FEM Galerkin P1 tridimensional, três malhas/domínios, caso manufaturado, comparação independente com Biot–Savart e exportação VTU/NPZ. O caso principal tem 196.661 tetraedros e 33.000 nós.
- Dimensionamento do circuito com tolerâncias, correntes por fase, retorno de energia, sangrias, dissipação e limites condicionais.
- Testes analíticos da análise de formas de onda, contratos da captura e PI discreto com planta RL de evolução exata por amostra.
- Verificações de integridade e site; relatórios de software não são relatórios de ensaio físico.

O FEM prevê 57,7779 µT no centro para **duas correntes CC prescritas de 0,150 A**; a referência independente é 59,4386 µT, diferença de 2,79% nesse ponto. Erro RMS no eixo de 3,52% e fora do eixo de 3,13% nas amostras documentadas. Há calibre/contorno aproximados e homogeneização do enrolamento; isso não valida todo o campo com um erro único nem inclui perdas CA.

## Modos separados e reproduzíveis

| Modo | Conexão e objetivo |
|---|---|
| CA principal | Duas fontes sincronizadas, capacitores em série e receptor com carga. Referência inicial 2 V RMS, 1.400 Hz, fase 0°, toroide desligado. |
| CC de mapa/FEM | Duas bobinas com 0,150 A CC medidos, capacitores contornados, receptor aberto e toroide desligado. Ver ligações específicas; este é o caso do FEM. |
| PI CC | Uma bobina, capacitor contornado, segunda fonte e receptor desconectados. Firmware regula somente essa planta. Não equivale ao mapa FEM de duas bobinas. |
| Toroide auxiliar | Excitação independente documentada, contabilizada separadamente; não converter um campo toroidal em feixe axial. |

Reconfigurar somente desenergizado. Os instrumentos e a resposta real das proteções determinam os pontos liberados. A faixa 4,70 V RMS é uma recomendação baseada numa grade de cálculo, não garantia universal; 5 V RMS exige verificar corrente e integridade da senoide em cada condição.

## Execução e estado da evidência

```powershell
py -B bancada_v3/eletronica/calculos.py
py -B bancada_v3/fem/validate_artifacts.py
py -B bancada_v3/medicoes/testes.py
py -B bancada_v3/medicoes/testes_cc.py
py -B -m unittest discover -s bancada_v3/aquisicao -p "test_*.py"
py -B -m unittest discover -s bancada_v3/controle -p "test_*.py"
```

Para refazer o FEM, criar ambiente separado e instalar `fem/requirements.txt`, conforme as instruções do módulo. Não é necessário instalar esse solver para abrir a V2 ou consultar os resultados já calculados.

O adaptador real de captura precisa do driver PicoSDK e do instrumento conectado; falha explicitamente se faltarem. O diagnóstico deste ambiente encontrou **PicoSDK ausente**; nenhuma captura experimental foi criada. O firmware não foi carregado numa placa física. Os CSV de campanha continuam vazios e as calibrações pendentes. A compra, fabricação, montagem, qualificação térmica/elétrica e coleta real não podem ser substituídas por arquivos ou testes automatizados.

As alegações de energia do vácuo, gravidade controlada e wormholes continuam sem implementação demonstrada; consultar a [auditoria científica](../auditoria_cientifica.md).
