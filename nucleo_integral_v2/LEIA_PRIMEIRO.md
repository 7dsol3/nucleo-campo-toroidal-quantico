# Núcleo integral — versão 2

Abra index.html no Chrome/Edge. O laboratório funciona localmente, sem internet ou servidor. Ele amplia a primeira bancada para representar os conjuntos da imagem, com circuitos, campo vetorial3D, receptor de energia, toroide poloidal e teste PI emDC separado.

## Como usar

1. Montagem: gire com o mouse, aproxime com a roda, use Explodir/Abrir carcaças e selecione o conjunto no menu abaixo. VetoresB mostram o campo instantâneo emt=0; setas têm escala gráfica limitada, não representam feixes de energia.
2. Ajuste as duas tensões, frequência, fase, carga e temperatura. Fontes com fase180° cancelam o campo central quando o conjunto é simétrico. Uma fonte ajustada a0 V continua conectada como porta ideal no circuito; isso não equivale a desconectar fisicamente a bobina.
3. Campos: veja um corte x–z do modelo3D; z=0 está na base, z=125 no centro. Cores representam móduloRMS, recortadas no percentil98; zonas dos fios são excluídas. Mudança de escala é automática.
4. Energia: confira potência assinada das portas, perdas e carga. Toroide tem alimentação própria e balanço separado. Sensores, iluminação e amplificadores externos não integram a eficiênciaAC mostrada.
5. Frequência: encontre o pico calculado. Ensaios: execute os controles numéricos ou importe CSV reais. Um PASS não é resultado de experimento físico.
6. Hipóteses: consulte o estado de cada função da imagem. Os blocos quânticos/gravitacionais ainda exigem equações, parâmetros e observáveis.
7. Ciclo:1inicialização;2ressonância;3transferência;4PI emDC separado;5operação contínuaAC. O ensaio4 tem capacitores contornados e receptor desconectado; as métricas principais continuam no cenárioAC atual.

## O que foi entregue

- Projeto_Integral.pdf/.docx/.md: especificação, circuito, resultados, fabricação, testes e limites.
- cad/01_montagem_dimensional.svg e02_componentes_enrolamentos.svg: medidas da estrutura e peças.
- cad/montagem_integral.obj/.mtl: montagem completa para importar em software3D.
- cad/nucleo_integral.scad: fonte paramétrica; cad/*.stl: peças mecânicas.
- cad/LEIA-ME_CAD.md: processo de fabricação, sequência e folgas críticas revisadas.
- lista_completa_pecas.csv: mecânica, elétricos e instrumentação.
- circuito_integral.svg: conexões e fronteiras de potência; eletrônica externa não possui PCB validado.
- simulacao/modelo_integral.py e modelo_browser.js: motores numéricos; métodos emMETODOS.md.
- pesquisa/: cobertura dos quadros/rótulos do pôster e requisitos das funções ainda indefinidas.
- validacao_entrega.json: verificações digitais e limitações físicas.

## Referência geométrica

Base360×360×12 mm; anéisØ340 mm; bobinasR100 mm emz65/185 mm,50voltas cada; receptorR35 mm emz125 mm,20voltas; toroideR135/r8 mm,48voltas poloidais. ColunaØ54/50 mm aberta ao ar; não é uma câmara de pressão/vácuo. Nenhuma dessas cotas é recuperada da legenda artística de10m.

Fonte2 V RMS emcadaporta,1.400 Hz,fase0°,carga100 Ω: I≈185,446 mA por bobina, campo≈73,484 µT RMS, Pfontes≈0,735861 W, Pcarga≈24,055 µW. São previsões; não há medições de hardware. A transferência é alimentada pelas fontes externas e não indica energia líquida do vácuo.

## Reproduzir

```powershell
py .\simulacao\modelo_integral.py --output .\simulacao\outputs
py .\simulacao\validar.py --browser
py .\cad\gerar_integral.py
```

Python usa configuracao.json; mover controles no navegador não altera esse arquivo. O gerador do modelo atualiza a referência incorporada emmodelo_browser.js. Ao mudar geometriaCAD, sincronizar manualmente a configuração física e regenerar; não existe sincronização automáticaCAD→solver. Não executar scripts de ajuste de interface repetidamente: eles pertencem à produção desta entrega.

O teste de navegação requer Playwright/Chrome. Para usar o laboratório, basta abrir oHTML. Os arquivos funcionam offline e nenhum dado é enviado a um serviço externo.

## Medições

Modelo_Medicoes.csv está vazio. Preencha valoresRMS, potência ativa com sinal correto, fase, carga, temperatura e estado do receptor. receiver_enabled aceita1ou0. Usar separador; e decimal ponto/vírgula. A comparação usa toroide desligado. Analise incerteza e controles no protocolo; diferenças médias não são uma aprovação estatística.

JSON/CSV emsimulacao/outputs são saídas calculadas, inclusive cenario_exportado_browser.json. Nenhuma linha de simulação deve ser apresentada como medição. A versão1 permanece emoutra pasta comoutro circuito.

## Estado real

Projeto e simulação foram produzidos e verificados digitalmente. Falta fabricar, selecionar/verificar as fontes e sondas, montar, calibrar e executarP01–P10. Malha fechada não certifica impressão, montagem ou resistência. OpenSCAD não foi executado por ausência do programa; não há STEP nativo.

Geração de energia do vácuo, coerência quântica, propulsão e curvatura não foram implementadas como efeitos físicos nem demonstradas. O inventário de lacunas identifica o que precisa ser definido para investigar essas alegações.
