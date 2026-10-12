# Núcleo — bancada e simulação de bobinas

Esta entrega transforma a referência visual em uma primeira bancada de engenharia que pode ser desenhada, fabricada e comparada com medições. O modelo trata eletromagnetismo clássico: duas bobinas circulares e um circuito RLC série. Nenhum aparelho foi construído nesta etapa. Energia do vácuo, controle da gravidade, propulsão e wormholes não foram demonstrados pela imagem ou pelo Atlas.

## Começar agora

1. Abra `index.html` no Chrome ou Edge. Funciona localmente, sem internet, servidor ou instalação.
2. Gire a montagem com o mouse, aproxime com a roda e clique nos nomes das peças. Use **Vista explodida** e **Medidas**.
3. Nas abas **Mapa do campo** e **Ressonância**, ajuste tensão, frequência, capacitância, distância e temperatura do cobre. O mapa mostra valores RMS; as setas mostram o sentido do campo na fase positiva. A escala de cores é automática e recortada no percentil 98; valores maiores compartilham a cor superior.
4. **Sintonizar f₀** aproxima a frequência de ressonância calculada. O gráfico usa I/V para permitir comparar ensaios feitos com tensões diferentes. A fonte desligada tem corrente e campo nulos; a curva normalizada descreve a resposta prevista por volt.
5. Leia `Projeto_Tecnico.pdf` e `cad/LEIA-ME_CAD.md` antes de fabricar. Use `cad/desenho_dimensional.svg` para conferir as medidas.

O CAD fornecido corresponde à geometria de referência: raio médio 100 mm, 50 espiras em cada bobina, distância entre centros 100 mm. Alterar distância no visualizador é um estudo; exige novos espaçadores e, se necessário, hastes maiores. A vista explodida desloca as peças para explicar a montagem.

## Arquivos principais

| Arquivo | Uso |
|---|---|
| `index.html` | Laboratório interativo local, independente de bibliotecas externas |
| `Projeto_Tecnico.pdf` / `.docx` / `.md` | Projeto, medidas, alimentação, montagem, previsões, protocolo e limites |
| `cad/montagem.obj` + `.mtl` | Montagem 3D com grupos e materiais; importar em Blender |
| `cad/nucleo_bancada.scad` | Fonte CAD paramétrica para OpenSCAD |
| `cad/*.stl` | Malhas das peças mecânicas; conferir unidades em mm e quantidade |
| `cad/pecas.csv` | Lista mecânica e materiais do enrolamento |
| `lista_completa_pecas.csv` | Mecânica, componentes elétricos e instrumentos necessários |
| `circuito_ensaio.svg` | Esquema elétrico vetorial do ensaio com instrumentos externos |
| `simulacao/modelo.py` | Modelo eletromagnético em SI, sem dependências |
| `simulacao/resultados/` | Previsões JSON e CSV de campo e frequência |
| `auditoria_cientifica.md` | Leitura crítica do Atlas/pôster, fontes e plano experimental |
| `validacao_entrega.json` | Registro final dos arquivos e verificações |

STL/OBJ são malhas; não há STEP de sólidos nativos nesta versão. O OpenSCAD não foi renderizado por seu executável nesta máquina. As malhas foram geradas por Python e verificadas digitalmente; ainda não foram fatiadas, impressas ou montadas.

## Resultados previstos de referência

Fonte 2 V RMS, 1.000 Hz, capacitor nominal 10 µF, cobre a 20 °C:

- Corrente: 174,392 mA RMS.
- Campo central: 78,405 µT RMS, ou aproximadamente 110,881 µT de pico.
- Indutância série estimada: 2,335638 mH; frequência de ressonância: 1.041,400 Hz.
- Potência ativa na bancada: 0,346739 W; 0,304126 W no resistor e 0,042613 W no cobre.
- Resistência de cobre estimada: 1,401151 Ω, incluindo 1 m de terminais.

Esses números são cálculos, não medições. Indutância aproximada de Wheeler e espiras equivalentes no raio médio precisam ser calibradas com L/R/C e dimensões medidos. A bancada tem formato de anéis toroidais, mas o campo central é axial. Um solenoide toroidal verdadeiro requer outro enrolamento.

## Reproduzir os cálculos

Com Python instalado, na pasta deste projeto:

```powershell
py .\simulacao\modelo.py --output .\simulacao\resultados
py .\simulacao\validar.py
py .\cad\gerar_cad.py
```

O modelo Python usa sua própria `configuracao.json`; mover controles no navegador não altera automaticamente esse arquivo. Os dados exportados pelo botão **Exportar previsão** usam os controles atuais.

O teste de navegador usa Python Playwright e o Chrome instalado; é ferramenta de desenvolvimento, não requisito para abrir o laboratório. Não é preciso instalar isso para usar a simulação.

## Inserir medições reais

Clique **Modelo de CSV**. O arquivo inicia vazio de dados, com estas colunas:

```text
frequency_hz;source_rms_v;current_rms_a;B_center_rms_uT;u_B_uT
```

Preencha uma linha por medição. Use frequências em Hz, tensão/corrente senoidais RMS e módulo do campo axial central RMS em µT. `u_B_uT` pode registrar a incerteza, mas o visualizador não calcula aprovação estatística nem usa essa coluna no diagnóstico percentual. Aceita separador `;` com decimal ponto ou vírgula. Mantenha L/R/C, geometria e temperatura do ensaio coerentes com os controles. Correntes de diferentes tensões são normalizadas no gráfico por I/V; linhas de 0 V não aparecem nesse gráfico.

O diagnóstico usa diferença absoluta relativa à previsão, não um veredito de comprovação. Para testar a hipótese, analise incerteza, repetibilidade e controles conforme o PDF. O arquivo `previsao_exportada_browser.csv` é uma saída de simulação produzida durante QA; não contém medições reais.

## O que falta para o ensaio físico

Comprar/fabricar as peças, selecionar a fonte senoidal e instrumentos adequados, verificar sua conexão elétrica, montar, medir L/R/C, calibrar o sensor, registrar campo/potência/temperatura e comparar com a previsão. A fonte é um instrumento externo especificado; esta entrega não contém um amplificador eletrônico completo ou PCB.

O Atlas relata 37 testes próprios, cujos fontes não foram anexados à solicitação. Eles não foram reexecutados aqui. As verificações desta entrega são novas e específicas para esta bancada.
