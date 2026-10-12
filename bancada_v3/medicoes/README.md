# Medições simultâneas da bancada V3

Este pacote analisa **arquivos capturados em instrumentos reais** e também testa o algoritmo com sinais matemáticos identificados como `SYNTHETIC`. Não existe aquisição experimental preenchida neste repositório. Os dois CSV fornecidos contêm somente cabeçalhos; `metadados_pendente.json` é deliberadamente incompleto e será rejeitado enquanto tiver `origin=PENDENTE`.

O programa não controla fontes, certifica instrumentos ou afirma que a bancada já foi construída. A aquisição de hardware está em `../aquisicao/`. O cálculo usa somente Python 3.10+ e biblioteca padrão, sem rede.

## Conexão e fronteira de potência

Usar a topologia documentada da V3: dois amplificadores OPA548EVM, cada um alimentando `capacitor 10 µF -> bobina -> resistor série 10 Ω -> SGND`. O resistor existente de 10 Ω é também o shunt; **não acrescentar outro resistor de 10 Ω**, pois isso mudaria o circuito simulado. Conexões Kelvin no resistor evitam incluir a queda dos cabos na medição. O valor efetivamente medido e seu limite de erro devem entrar no JSON, na temperatura de operação.

| Canal do PicoScope 4824A | CSV | Conexão positiva | Referência |
|---|---|---|---|
| A | `v_source1_v` | Saída do amplificador 1, antes do capacitor | SGND |
| B | `v_series1_v` | Topo do resistor série 1 no retorno | SGND |
| C | `v_source2_v` | Saída do amplificador 2, antes do capacitor | SGND |
| D | `v_series2_v` | Topo do resistor série 2 no retorno | SGND |
| E | `v_load_v` | Topo da carga resistiva do receptor | SGND |

Os BNC têm terra comum: prender todos os retornos **ao mesmo SGND em estrela**. Este esquema não mede tensões flutuantes de capacitor ou bobina. Prender um terra BNC em outro nó pode curto-circuitar o circuito. Um terminal da carga receptora fica em SGND; documentar essa ligação porque ela difere de um receptor completamente flutuante.

A corrente é positiva saindo da fonte: `i1=v_series1/R1` e `i2=v_series2/R2`. `mean(v_source*i)>0` significa potência entregue ao circuito; valor negativo significa potência recebida pela fonte. A tensão de fonte é medida na saída **carregada**, não deduzida da indicação do gerador. A fronteira inclui capacitor, cobre e resistor série, mas exclui consumo DC dos amplificadores, gerador, DAQ e computador. Assim, estes dados não medem a eficiência da tomada. A carga receptora resistiva usa `mean(v_load²)/Rload`.

## Captura e proveniência

1. Preservar CSV bruto e diagnóstico da captura. Não colar uma curva simulada num arquivo experimental. `origin=EXPERIMENTAL` exige identificação do instrumento, número de série, instante real da aquisição, commit do projeto, documentos de calibração, geometria construída e controles. `origin=SYNTHETIC` serve somente a sinais gerados por algoritmo.
2. Copiar o template para a pasta da campanha, preencher os valores **medidos** de R1, R2 e carga (10/10/100 Ω são nominais), e informar a frequência real e seu limite absoluto de erro. O caminho `model_config_path` é relativo ao arquivo JSON; ajuste-o ao mover o template ou use `--config`.
3. Usar relógio e disparo comuns aos cinco canais. Confirmar amostragem simultânea, limite de skew, taxa real retornada pelo driver, ausência de clipping e regime estacionário. Exportar uma linha por instante comum. O programa não alinha aquisições feitas em instantes diferentes.
4. Documentar filtragem antialias e sua resposta; o simples campo preenchido não cria um filtro. Informar ganho, offset, ruído e erro de fase de cada caminho de medição, inclusive sonda, divisor, cabo e amplificador de sensor. Considerar quantização no limite de ruído. `bandwidth_hz` é a banda **calibrada**, não apenas a banda anunciada.
5. Registrar controles: fontes desligadas, carga resistiva conhecida, troca de canais e repetição. `baseline_records` lista arquivos reais; o algoritmo não lê nem valida automaticamente o conteúdo dos documentos citados.

O cabeçalho obrigatório usa vírgulas e ponto decimal:

```text
time_s,v_source1_v,v_series1_v,v_source2_v,v_series2_v,v_load_v
```

As colunas opcionais `temperature_c` e `field_t` precisam ter valor finito em **todas** as linhas, em °C e tesla. `field_t` é um canal calibrado medindo a componente z no centro; a comparação do módulo da previsão V2 pressupõe campo axial. Registrar aquisição de fundo e sensor/posição/orientação. Não preencher zero para disfarçar um sensor ausente: campo ausente ou zero deixa sua validação inconclusiva. A ausência do campo não impede o cálculo elétrico dos cinco canais, mas impede validar o sistema completo. Temperatura exportada já é física e deve ter sensor/calibração identificados.

Formato mínimo dos instrumentos (substituir pelos dados de cada instrumento real, sem usar os textos a seguir como evidência):

```json
{
  "model": "PREENCHER_MODELO_REAL",
  "serial": "PREENCHER_SERIAL_REAL",
  "calibration_document": "documento_real_da_campanha.pdf",
  "calibration_valid_until": "AAAA-MM-DD"
}
```

O JSON guarda os metadados originais, SHA-256 dos arquivos brutos/JSON/configuração e instante de análise. Um nome de documento sozinho não prova calibração; a equipe deve verificar seu conteúdo e vigência. Metadados não documentados levam a `INCONCLUSIVE` e jamais a `PASS`.

## Calibração, janelas e cálculos

Para cada canal, a convenção é **físico = (valor exportado − offset) × gain**. Se a aquisição já aplicou a correção de um certificado, usar a identidade aqui e declarar seus limites residuais; não corrigir duas vezes. `offset_native_bound` está na unidade original do CSV; `noise_absolute_bound` está na unidade física após ganho. Os demais limites são relativos (`gain_relative_bound`, por exemplo 0.01 = 1%) ou graus (`phase_bound_deg`). Ganho negativo inverte polaridade. Todos precisam derivar de dados/calibração apropriados à amplitude e banda utilizadas.

`time_s` precisa ser crescente, sem duplicatas, NaN, Inf, células vazias ou divergência entre intervalos maior que 0,01%. A análise rejeita taxa inferior a 20 amostras por ciclo e skew superior a 0,001 período. O intervalo de potência é uma janela coerente de pelo menos cinco ciclos: `N*dt*f` precisa ser inteiro com tolerância de 0,0001 ciclo, sendo `N` o número de amostras **sem repetir o ponto final**. Pode fornecer `window_cycles`; se for nulo, procura a maior janela coerente possível e informa as amostras descartadas. Não interpola nem reamostra. Na condição inicial de 1400 Hz e 500 kS/s, 50000 amostras cobrem 140 ciclos. A taxa real retornada pelo driver pode exigir outra duração. Frequência/relógio cuja incerteza produza mais de 0,001 ciclo na janela deixa a comparação inconclusiva.

O relatório extrai média CC, RMS total, RMS CA após remover a média, fasor RMS por DFT na frequência medida, diferença de fase fonte/corrente, potência média assinada por multiplicação simultânea e energia durante a janela. A THD inclui harmônicos inteiros até o menor entre o 10º, a banda declarada e o limite de 20 amostras por harmônico; **não é uma certificação de THD em toda a banda ou análise de inter-harmônicos**. THD ausente, acima de 1%, componente CC acima de 1% ou energia relevante fora da fundamental impedem uma comparação conclusiva com o modelo senoidal V2.

A previsão importa o solver V2 em modo de leitura, com configuração fornecida, amplitudes/fases fundamentais realmente medidas, frequência, resistores e temperatura. Não executa os geradores de arquivos V2. O V2 tem R série igual nos dois ramos; a análise sinaliza valores diferentes em vez de esconder essa limitação. Toroide auxiliar ativo exige medir suas fontes extras. Geometria, orientação, resistência AC, parasitas e resposta do driver ainda exigem caracterização física.

## Limites de erro e interpretação

O pacote propaga **limites absolutos conservadores** de ganho/offset/ruído, resistor e fase/skew. Para a amostra de tensão corrigida, usa `eV=abs(V)*erro_relativo + abs(gain)*erro_offset + erro_ruído`; para corrente, inclui o menor denominador `R−eR` e o termo cruzado. Para a potência, soma `mean(abs(V)*eI + abs(I)*eV + eV*eI)` e uma contribuição de fase limitada pela banda declarada. Erros correlacionados não são cancelados. A duração e a energia incluem o limite do relógio comum. Bandwidth, fase e ruído devem cobrir **toda a banda transmitida** pelo filtro antialias; a documentação incorreta invalida esses limites.

Esses limites não são automaticamente incertezas padrão, não recebem `k=2` nem uma probabilidade de cobertura inventada. O relatório informa `coverage_probability=null` e `coverage_factor_k=null`. Para um orçamento metrológico formal, faltam distribuições, correlações, repetibilidade e incerteza do modelo. A distinção entre propagação de incertezas padrão, correções e cobertura é explicada pelo [NIST TN 1297, seção 5](https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-5-combined-standard-uncertainty) e [seção 6](https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-6-expanded-uncertainty). Este software não se apresenta como certificação NIST.

Uma diferença menor que o limite de medição significa apenas compatibilidade condicionada aos limites informados; a incerteza do modelo permanece não quantificada. Uma diferença maior exige revisar instrumento, conexão, modelo e controles. O resíduo fonte−carga contém todas as dissipações não medidas e possíveis transientes: **nunca é classificado como energia extra, energia do vácuo, gravitação ou efeito quântico**. Uma fonte que absorve potência requer um driver capaz de fazê-lo naquele ponto; o programa preserva o sinal negativo.

## Executar

Na raiz do repositório, após uma captura e preenchimento real dos metadados:

```powershell
py -B bancada_v3/medicoes/analisar.py C:/campanha/captura.csv C:/campanha/metadados.json --config nucleo_integral_v2/simulacao/configuracao.json --output C:/campanha/relatorio_001.json --summary-csv C:/campanha/resumo_001.csv
```

Os nomes de saída precisam ser novos e distintos; o programa recusa sobrescrever evidência. O resumo tem exatamente as colunas e separador `;` do `Modelo_Medicoes.csv` V2, com receptor representado por 0/1, e deve ser mantido junto do JSON de origem/incertezas. O resumo sozinho não diferencia simulação de ensaio; o JSON faz parte obrigatória do resultado. Campo/temperatura não medidos saem vazios, nunca inventados. Um resumo incompleto será rejeitado pela importação do visualizador V2, que exige todas as medições; os cálculos elétricos continuam disponíveis no JSON. Código de saída 2 significa aquisição/entrada rejeitada; código 0 significa análise concluída, **não aprovação física**. Consulte o campo `status` e os motivos inconclusivos.

Testar o algoritmo sem nenhum equipamento e sem criar resultados no repositório:

```powershell
py -B bancada_v3/medicoes/testes.py
py -B bancada_v3/medicoes/testes.py --json-output "$env:TEMP/nucleo_medicoes_testes.json"
```

Todos os sinais desses testes nascem em diretório temporário, trazem `origin=SYNTHETIC` e são removidos ao final. Os testes incluem potência em quadratura, fonte absorvendo potência, offset/ganho inversos, CC, harmônicos, incerteza de fase, relógio/janela/skew, timestamps inválidos, dados não finitos, baseline zero, ausência de campo, metadados pendentes e importação sem alteração do modelo V2.

## Ensaio CC estacionário para confronto com FEM

`analisar_cc.py` é a análise específica de magnetostática: **capacitores desviados, receptor aberto, toroide desligado**, duas correntes próximas de 0,15 A e sonda z no centro `[0,0,0.125]` m. Desligar fontes antes de reconfigurar conexões. A rotina CA acima usa uma fundamental e THD; não deve ser usada para julgar um ensaio CC estacionário.

Capturar dois arquivos reais distintos: energizado e fundo, mantendo instrumentos, sensor, posição, faixa e configuração de aquisição. No fundo, ambas as bobinas devem estar sem corrente; esperar os transientes terminarem antes de ambas as capturas. O capturador de hardware pode fornecer as colunas `field_t` e `temperature_c`, mas uma conversão por sensibilidade nominal não cria uma calibração. Preservar F/G/H brutos e diagnósticos. Copiar `metadados_cc_pendente.json` e preencher valores medidos dos shunts, correções, limites, documentos, hashes pré-existentes da captura e origem de **ambos** os registros. O template é deliberadamente pendente e não representa um ensaio.

```powershell
py -B bancada_v3/medicoes/analisar_cc.py C:/campanha/cc_energizado.csv C:/campanha/cc_fundo.csv C:/campanha/metadados_cc.json --output C:/campanha/cc_relatorio_001.json
py -B bancada_v3/medicoes/testes_cc.py
```

O programa usa a mesma calibração `(exportado-offset)*gain` da análise CA. Extrai médias de fonte/corrente, `Imean=mean(Vshunt)/Rshunt`, potência assinada `mean(Vsource*I)`, desvio padrão e RMS do resíduo em torno da média. O campo líquido é **mean(Benergizado)−mean(Bfundo)**. O limite conservador do campo soma os limites de ambos os registros e a deriva documentada entre capturas; não assume que erros ou ruído desconhecidos se cancelem. Desvio padrão da captura não é substituto automático para incerteza da média. Erro de tempo, transientes, deriva térmica e ambiente magnético precisam ser controlados no ensaio.

A previsão de Biot–Savart importa somente a geometria e as funções de campo do V2: soma cada espira axial com **correntes CC medidas e orientações reais**, preservando o sinal, inclusive com correntes negativas. Não utiliza tensão de fonte para supor corrente. A incerteza parcial propagada das correntes não inclui incerteza da geometria ou ambiente; não é incerteza completa do modelo.

O FEM `fine_box060` foi resolvido com 0,15 A iguais por bobina. Sua previsão central só é escalada linearmente por `média(I1_física,I2_física)/0.15` quando as correntes são demonstradas iguais dentro de **1%**, incluindo soma conservadora dos limites das duas correntes. Exige a geometria-base de 100 mm de raio médio, centros em 65/185 mm, 5×10 espiras com passo 1,1 mm, ponto central de origem z=125 mm, regime estacionário, receptor aberto, capacitores desviados e toroide desligado. Se qualquer condição faltar ou mudar, o campo FEM escalado fica vazio e sua comparação `INCONCLUSIVE`; não se inventa um novo caso FEM para correntes diferentes. O confronto axial V2 continua disponível para correntes independentes.

Os aproximadamente **2,79%** entre FEM e referência no centro são uma diferença **observada nesse caso numérico**, não uma incerteza universal do modelo nem intervalo de cobertura experimental. O relatório preserva o valor do artefato e seu SHA-256. Documentos, calibração ou geometria pendentes mantêm o resultado experimental inconclusivo. Testes matemáticos têm `origin=SYNTHETIC` e nunca geram `PASS` físico. Uma diferença residual não comprova efeitos quânticos, gravitacionais ou energia do vácuo.

Os testes CC verificam fundo separado, cancelamento de offset conhecido sem cancelar arbitrariamente limites, sinais invertidos, ruído analítico, médias/potências, bloqueio de escala FEM por correntes desiguais ou incerteza excessiva, receptor fechado, corrente no fundo, campo líquido zero e metadados ausentes/origens incompatíveis. Todos os fixtures são temporários e explicitamente sintéticos.
