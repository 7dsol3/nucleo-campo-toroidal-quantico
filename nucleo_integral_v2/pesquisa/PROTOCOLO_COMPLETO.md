# Núcleo integral V2 — plano de construção, medição e decisão

Data: 12/10/2026. Referências: imagem fornecida e Atlas das Estruturas Fundamentais, edição técnica 1.0, especialmente páginas 3, 13, 22, 23 e 28. Este arquivo descreve um projeto de bancada e ensaios a realizar. Não contém resultados de aparelho físico, nem reproduz os 37 testes originais do Atlas.

A bancada conserva a organização visual em anéis, coluna, receptor e estruturas externas. Cada peça recebe uma função definida, com sensores e critérios de avaliação. A física implementada é eletromagnetismo clássico de bobinas acopladas, transferência indutiva e ressonância elétrica. Um modelo PI de corrente utiliza uma planta RL DC em ensaio separado. As funções adicionais anunciadas no pôster ficam registradas com os elementos que faltam para construir um modelo testável.

## 1. Configuração nominal e o que significa funcionar

| Item | Parâmetro proposto | Conferência necessária antes da operação |
|---|---|---|
| Bobina axial inferior | 50 espiras; raio médio 100 mm; centro z=65 mm | Contagem, raio médio, R, L e sentido de enrolamento |
| Bobina axial superior | 50 espiras; raio médio 100 mm; centro z=185 mm | Mesmas medições, além da fase relativa |
| Separação axial | 120 mm entre planos médios | Não é a configuração ideal de Helmholtz, que exige separação igual ao raio |
| Receptor | 20 espiras; raio médio 35 mm; centro z=125 mm | R, L, polaridade e carga real |
| Carga do receptor | 100 Ω nominal, resistor não indutivo | Valor medido, potência admissível, temperatura |
| Toróide auxiliar | 48 voltas sobre seção circular; raio maior 135 mm; raio menor 8 mm; z=125 mm | Enrolamento sobre a seção, R, L, fuga e geometria real; OFF no ensaio de referência |
| Excitação axial | Duas fontes senoidais externas, sincronizadas | Cada canal começa com 2 V RMS; limite de comando 5 V RMS; 100–5000 Hz |
| Cada ramo axial | Resistor 10 Ω/10 W não indutivo e capacitor 10 µF inicial em série | Medir R/C/ESR; incluir impedância da fonte e cabos |
| Corrente | Teto inicial 0,50 A RMS por ramo axial | Limitar também pico, temperatura e corrente permitida pelo equipamento |
| Estrutura | Suportes não magnéticos, aros inteiros Ø340 mm, coluna óptica aberta ao ar | Aros exigem CNC ou área de fabricação compatível. Não é câmara de vácuo, vaso de pressão nem plasma |

Estas cotas são novas escolhas de projeto, não medidas extraídas da legenda artística de 10 m. O desenho CAD estabelece a montagem; as tolerâncias e materiais efetivamente fabricados devem entrar na previsão. Se o CAD ou o fio mudar, registrar a alteração e recalcular antes de medir.

Funcionamento mecânico significa montar e reposicionar as peças com as cotas previstas. Funcionamento eletromagnético significa que tensão, corrente, fase e campo concordam com um modelo previamente fixado dentro da incerteza. Funcionamento da conversão significa medir potência numa carga e demonstrar sua origem nas fontes. Funcionamento do controle significa manter uma corrente DC medida na planta RL de ensaio conforme a resposta dinâmica escolhida. Nenhum desses critérios, isoladamente, demonstra os efeitos de vácuo, gravidade ou informação pura indicados na arte.

## 2. Rastreabilidade dos quadros do pôster

O pôster apresenta os números 1–5 e 7–13. O número 6 não aparece no arquivo fornecido. A posição 6 é registrada como ausente, preservando a numeração original.

| Nº | Quadro da imagem | Realização nesta bancada / tratamento |
|---|---|---|
| 1 | Estrutura geral | CAD com peças separadas; bobinas, suportes, receptor, coluna e toróide; os oito rótulos são mapeados abaixo |
| 2 | Geometria de campo | Campo vetorial de bobinas circulares e toróide; toro geométrico 3D. A projeção de um campo em dimensões extras exige equações e coordenadas que o pôster não define |
| 3 | Funcionamento | Cinco etapas operacionais convencionais rastreadas na seção 4; estado do vácuo e ressonância quântica permanecem sem mecanismo fornecido |
| 4 | Equações fundamentais | Maxwell/Biot–Savart, Faraday e impedância complexa implementáveis. Métrica, campos adicionais e potencial do pôster exigem especificação para virar problema numérico |
| 5 | Matriz de acoplamento | Matriz elétrica mensurável L/M/R/C. Não identificar essa matriz com os blocos simbólicos de geometria, informação e vácuo do pôster |
| 6 | Ausente na imagem | Nenhuma peça ou função inventada para preencher a numeração |
| 7 | Modelos de aplicação | Potência indutiva para carga é testável. Propulsão sem reação, wormholes, manipulação do espaço-tempo e controle de matéria não possuem previsão ou implementação definida |
| 8 | Estrutura em escalas | Bancada na escala de engenharia; dimensões atômicas, quânticas e macroscópicas são ilustrações de escalas, sem simulação multiescala validada |
| 9 | Ciclo operacional | Inicializar, excitar, carregar receptor, avaliar controle em ensaio DC separado, observar estabilidade térmica; ver seção 4 |
| 10 | Mapa espaço-tempo e energia | Mapas reais de B e de densidade magnética B²/(2µ0). Superfície deformada da arte pode ser ilustração; não é uma métrica gravitacional solucionada |
| 11 | Assinatura matemática | Conservação elétrica, matriz L positiva e estabilidade do controlador especificado. Determinante positivo e sinais de autovalores do pôster não são teste universal de estabilidade |
| 12 | Visão artística | Materiais luminosos, feixe e decoração aparecem apenas como visualização; não entram na medição como plasma, energia livre ou curvatura |
| 13 | Potencial e impacto | Registro de hipóteses de pesquisa; o desempenho entregue só pode ser descrito depois dos ensaios e da análise de incerteza |

## 3. Os oito componentes nomeados na imagem

| Nome original | Módulos CAD / interface | Equivalente testável e limite |
|---|---|---|
| Anel de Confinamento | upper_frame | Fixação mecânica da bobina; não há confinamento quântico definido |
| Campo Magnético Superior | upper_coil | Campo de 50 espiras excitadas por fonte AC independente |
| Câmara de Interferência | column, receiver | Região de superposição clássica de campo, com sonda e receptor |
| Núcleo de Vácuo Estável | column | Coluna transparente aberta ao ar; não foi projetado um estado de vácuo quântico nem uma câmara evacuada |
| Rede de Campo Quântico | toroid | Enrolamento toroidal clássico; propriedades extras exigem Hamiltoniano, estado, acoplamentos e observáveis |
| Matriz de Conversão | receiver, control | Bobina captadora, carga resistiva e instrumentação; potência fornecida pelas fontes |
| Campo Magnético Inferior | lower_coil | Campo da segunda bobina axial de 50 espiras |
| Anel de Estabilização | lower_frame, supports, thermal | Fixação e supervisão térmica; ensaio eletrônico de controle é clássico e separado |

Os módulos base, supports e thermal completam as necessidades de uma bancada real mesmo sem rótulo próprio no pôster. O cadastro modulos.json mantém a correspondência para a seleção no visualizador. `calculavel` significa que há uma grandeza e um modelo; `experimental` significa montagem/ensaio proposto; `ilustrativo` significa geometria ou efeito visual; `hipotese_sem_modelo` significa que faltam definições para produzir uma previsão. Nenhum estado equivale a aprovação física já obtida.

## 4. As cinco etapas e o ciclo de operação

| Passo | Quadro 3 / quadro 9 | Procedimento concreto proposto | Dado que decide o resultado |
|---|---|---|---|
| 1 | Geração de vácuo controlado / Inicialização | Inspecionar montagem e calibrar zero; manter coluna ao ar; fontes OFF; medir geometria e fundo | Cotas, R/L/C, zeros, temperatura e registro de instrumentos. Não existe comando de vácuo implementado |
| 2 | Ressonância toroidal / Ressonância | Excitar ramos axiais com fase conhecida, varrer frequência; ensaiar toróide separadamente | Corrente, fase, B e resposta I/V. Ressonância demonstrada será elétrica clássica |
| 3 | Conversão de energia / Conversão | Ligar receptor a carga medida; observar alteração das correntes das fontes | Potência útil, perdas e soma de entrada assinada; não atribuir energia à animação |
| 4 | Estabilização / Estabilização | Ensaio separado de PI de corrente RL DC, com capacitores contornados e receptor desconectado; caracterizar sensor, atraso e limites | Erro, overshoot, acomodação e limites na planta DC. Não é controle do circuito AC nem leitura de coerência quântica |
| 5 | Saída de campo / Operação contínua | Manter ponto de operação conservador por tempo registrado | Campo e potência estáveis, deriva, temperaturas e parada; aplicações extraordinárias seguem sem modelo |

Executar o circuito AC sem feedback, para medir correntes e verificar o modelo. O PI digital entregue pertence a uma planta RL DC separada; o ciclo visual não conecta automaticamente esse PI à matriz AC. Um futuro controlador AC exigiria sensores RMS, filtros, planta e testes próprios.

## 5. Modelo mensurável das bobinas acopladas

Usar metros, segundos, volts, ampères, tesla, henry, farad e ohm nas fórmulas. Fasores são RMS e adotam e^(jωt). Polaridades são fixadas pelo mesmo sentido visto ao longo de +z. Definir três ramos: inferior (1), superior (2), receptor (3). O toróide fica fora da referência axial e desligado; caso seu acoplamento seja relevante, estender a matriz e incluir sua fonte/perdas.

```text
Z11 = R1_total + j(ωL1 − 1/(ωC1))
Z22 = R2_total + j(ωL2 − 1/(ωC2))
Z33 = R3_cobre + R_carga + jωL3
Zij = jωMij = Zji, i≠j
Z I = [V1, V2 exp(jφ), 0]^T

P_fonte_k = Re(Vk conj(Ik))
P_entrada = P_fonte_1 + P_fonte_2
P_carga = |I3|² R_carga
P_perdas = |I1|² R1_total + |I2|² R2_total + |I3|² R3_cobre
P_entrada = P_carga + P_perdas, regime senoidal passivo estacionário
```

Na igualdade, o limite elétrico das fontes corresponde ao mesmo R_total adotado. Se a impedância interna da fonte for incluída na matriz, a potência de entrada deve ser calculada do lado anterior a essa impedância; se a tensão for medida no terminal de saída, retire a perda interna da contabilidade desse limite. Documentar o limite no esquema de cada ensaio.

Uma das fontes pode receber energia da outra. Manter o sinal de sua potência; não somar valores absolutos. Medir as duas fontes simultaneamente. Fasores de corrente não possuem, em geral, a mesma fase dos comandos de tensão. O receptor altera as correntes dos emissores por impedância refletida, portanto não basta calcular sua tensão mantendo correntes arbitrariamente fixas. Ao abrir a carga, resolver I3=0 e calcular a tensão induzida; não representar circuito aberto por R=0.

L é uma matriz de indutâncias reais, simétrica e positiva para enrolamentos passivos. Verificar |Mij|≤√(LiLj) e os autovalores da matriz completa; o limite par a par é necessário, mas não suficiente em três ou mais bobinas. M deve ser medido ou calculado por integração de fluxo/Neumann, com sinais de polaridade explícitos. A formulação convencional de indutância e energia está em [MIT — Inductance and Magnetic Energy](https://web.mit.edu/viz/guide/Chapter-11-Inductance%20and%20Magnetic%20Energy.pdf).

No eixo, para bobinas finas:

```text
Bz(z) = Σk μ0 Nk Ik Rk² / {2 [Rk²+(z−zk)²]^(3/2)}
μ0 ≈ 4π×10^−7 H/m, aproximação de engenharia
```

No ponto z=125 mm, com correntes iguais em fase, Bz/I≈396,2 µT/A. Isso prevê cerca de 79,2 µT RMS para 0,20 A RMS em cada bobina. É verificação geométrica aproximada, não resultado medido. Distribuir as espiras reais no pacote de enrolamento para reduzir erro de bobina fina. No mapa 3D, integrar segmentos ou usar solução analítica compatível; excluir pontos dentro do fio e declarar a resolução. Não calcular campo finito sobre um filamento ideal singular.

No toróide de seção pequena, Bφ(r)≈µ0 N I/(2πr), no interior; L≈µ0 N² A/(2πR_maior), A=π a². Os parâmetros escolhidos dão Bφ(R)/I≈71,11 µT/A e L≈0,6863 µH, apenas aproximações de projeto. O campo ideal é azimutal, não o feixe axial do pôster; o campo externo de um enrolamento finito depende da disposição e dos cabos. O suporte toroidal não deve ser confundido com uma bobina circular cujo fio corre apenas ao redor do grande aro. A geometria de enrolamento e as aproximações são discutidas em [MIT — Practical MQS systems](https://ocw.mit.edu/courses/6-007-electromagnetic-energy-from-motors-to-lasers-spring-2011/resources/mit6_007s11_lec08/).

L e C medidos determinam as frequências. Para duas bobinas idênticas sem carga e sem perdas, os modos simétrico/antissimétrico têm L_eff=L±M e f±=1/(2π√((L±M)C)). Com perdas, receptor e fontes reais, obter pico de I/V numericamente da matriz completa. Não fixar um único pico para toda fase ou chamar o pico de ressonância quântica.

Na faixa 100–5000 Hz e dimensões inferiores a um metro, adota-se aproximação quase estática. Resistência AC, ESR, cabos e impedância das fontes precisam ser caracterizados; aquecimento pode tornar R dependente da condição. O modelo linear não inclui saturação, plasma, material ferromagnético, correntes induzidas nos suportes metálicos, potência das luzes nem propagação relativística macroscópica. Material não magnético ainda pode ser condutor. Usar gabarito isolante para a sonda e comparar a presença/ausência de metal próximo antes de interpretar desvios de campo; incluir essas perdas num modelo ampliado se forem relevantes.

## 6. Alimentação e instrumentos que faltam para fabricar

O projeto mecânico e a simulação não substituem os instrumentos externos. Selecionar dois canais de excitação senoidal sincronizados, cuja capacidade de corrente, tensão, dissipação e isolamento seja comprovada sob essa carga. Um gerador comum com saída de 50 Ω pode não fornecer a corrente necessária; pode ser preciso um amplificador de laboratório com proteção e capacidade de receber energia de outro canal, ou isolamento adequado projetado por profissional de eletrônica. Usar módulos/equipamentos protegidos de baixa tensão; não há aqui projeto de ligação à rede elétrica.

Cada canal começa com 2 V RMS e sobe somente após medições; comando ≤5 V RMS e I≤0,50 A RMS, com parada acessível. Confirmar que o equipamento não entra em clipping ou proteção ao inverter fase. Resistor 10 Ω/10 W: a 0,50 A dissipa 2,5 W, antes das demais perdas, e depende da montagem térmica especificada. Capacitor inicial 10 µF não polarizado deve ter tensão AC, corrente RMS, ESR e frequência de trabalho adequadas no catálogo; nominal ≥100 VDC é apenas referência inicial e não garante operação AC. Monitorar V_C=I/(ωC), inclusive transientes.

Medir tensão e corrente simultaneamente, com sondas compatíveis com a topologia das saídas. Aterramentos comuns de osciloscópio podem curto-circuitar saída em ponte; verificar o circuito do equipamento antes de conectar. Equipamentos de bancada e a montagem elétrica final devem ser selecionados e montados por pessoa qualificada. A coluna óptica não precisa ser evacuada; pressão controlada e câmara apropriada seriam um projeto separado, sem equivalência automática a vácuo quântico.

| Instrumento | Requisito mínimo de projeto / propósito |
|---|---|
| Paquímetro/régua e gabarito não magnético | Posição relativa conhecida na ordem de 0,5–1 mm; medir raio médio e plano central |
| Medidor LCR | R/L/C/ESR na faixa relevante, incluindo frequência de medição; estimativa de incerteza ≤2% para L/C após calibração |
| Osciloscópio/DAQ sincronizado | Canais suficientes para v/i das duas fontes e carga, ou aquisição faseada validada; ≥200 kS/s no teto de 5 kHz, sincronismo e correção de fase |
| Shunts/resistores de referência | R medida; não indutivos; corrente obtida por v/R com resposta de frequência conhecida |
| Sensor de campo DC/AC | Resposta calibrada até 5 kHz quando usado em AC; resolução desejada ≤1 µT; orientação conhecida |
| Bobina de medição alternativa | Área, N, alinhamento e transferência calibrados; tensão mede derivada do fluxo, não B diretamente |
| Multímetro true RMS | Banda e fator de crista especificados; medição de apoio, sem substituir potência simultânea com fase |
| Sensor térmico | Contato seguro; incerteza alvo ≤1 °C; enrolamentos e resistores monitorados |

Estas são metas de seleção, não especificações de equipamentos já comprados. Registrar fabricante/modelo, número de série, data de calibração, faixa e certificado. Um celular não fornece resposta AC calibrada a 5 kHz só por mostrar um magnetômetro.

## 7. Plano dos ensaios e controles

Todos os ensaios abaixo estão **pendentes de montagem física**. Registrar ao menos três séries em dias ou remontagens independentes, mantendo os dados brutos e a ordem das condições. Recalcular o modelo com valores medidos antes de comparar resultados.

| ID | Ensaio / sequência | Resultado convencional previsto | Critério e controle |
|---|---|---|---|
| P01 | Inspeção: cotas, contagem de voltas, polaridades, terminais e acesso da sonda | Geometria corresponde ao CAD; nenhuma espira solta ou curto | Registrar desvios; alvos iniciais: centro ±1 mm, raio médio ±1 mm, coaxialidade ≤1 mm; atualizar modelo com desvio real |
| P02 | R/L/C/ESR isolados; M por tensão induzida e por medição de ligação série aditiva/oposta | M recíproco, matriz L positiva | Comparar métodos dentro de 2u_c; medição L+/L− só é válida com montagem, frequência e convenção iguais |
| P03 | DC, capacitor removido do ramo de ensaio: 0; ±0,05; ±0,10; ±0,15; ±0,20 A, uma bobina e par | B linear com corrente; soma/subtração ao inverter | Estimar [B(+I)−B(−I)]/2; comparar inclinação e perfil, sem alterar R geométrico para forçar ajuste |
| P04 | Mapa axial z=25…225 mm em passos de 10 mm, e radial 0/20/40 mm no plano z=125; AC 1000 Hz inicial | Distribuição de B calculada; componentes e fases distintas fora do eixo | Comparar a mesma componente RMS/complexa; fonte OFF, somente inferior, somente superior, 0°/90°/180°; alternar ordem |
| P05 | Varrer 100–5000 Hz; malha fina perto dos picos; carga aberta e 100 Ω; fases 0°/90°/180° | Modos e resposta I/V da matriz acoplada; carga muda correntes | Medir tensão terminal real e THD; ponto fora do limite do amplificador não valida o modelo linear |
| P06 | Potência simultânea das duas fontes, carga e dissipações; captura de número inteiro de ciclos | Entrada assinada igual a carga+perdas estacionárias | Comparar resíduo a 2u_c e controle resistivo; incluir energia armazenada durante transientes |
| P07 | Toróide isolado: OFF e excitação limitada, medir L/campo interno/fuga, depois medir interferência no conjunto | Campo azimutal interno e fuga limitada pela geometria real | Não inferir campo toroidal de Bz central; não atribuir fuga ou cabos a dimensão extra; incluir fonte auxiliar no balanço se ligada |
| P08 | Planta RL DC separada, capacitores contornados, receptor desconectado: degrau de corrente +10%, retorno e pequena mudança de resistência | PI de corrente clássico, limitado e estável; não é malha da simulação AC | Metas iniciais: acomodação ≤2 s, overshoot <10%, erro final <2% onde U permite; revisar ganhos com hardware e atrasos medidos |
| P09 | Operação no ponto de referência por 30 min, log 1 Hz | Deriva lenta ligada ao aquecimento; dissipação convencional | Parar a 45 °C em suporte/enrolamento ou limite menor do fabricante; avaliar deriva após regime térmico |
| P10 | Remover/remontar conjunto, repetir condições selecionadas e análise independente | Resultado reproduzível dentro da incerteza | Comparar três séries e documentar alterações; não escolher apenas a série favorável |

Para anular uma fonte, preferir desconectar fisicamente seu ramo durante o teste de bobina única. Colocar o comando em zero com um amplificador ainda conectado pode criar uma carga passiva adicional; é outra condição e deve ser modelada. Na condição 180°, o campo central só cancela se correntes reais, geometria e receptor forem simétricos. Ajustar comandos apenas conforme o protocolo e registrar correntes resultantes.

Controle passivo de potência: substituir a bobina/receptor por uma rede resistiva medida e repetir aquisição v/i, incluindo sinais de fase. Conferir que a cadeia reproduz P=V²/R dentro da incerteza. Depois usar carga aberta/fechada, fontes OFF, ramo único, inversão de fase, inversão de sondas e toróide OFF. Registrar iluminação/desenho separado: se luzes forem alimentadas, medir essa entrada ou desligá-las no balanço da bancada.

## 8. Incerteza e critérios numéricos

Antes de medir, definir a grandeza (componente Bz, amplitude RMS, fase ou potência), janela de integração, temperatura e posição. Dados mínimos por linha: data/hora, versão do modelo, configuração, f, V1/I1/fase1, V2/I2/fase2, V3/I3, Bx/By/Bz ou componente da sonda, posição, temperatura, valores R/L/C/M, estado do toróide, calibrações e observações. Armazenar as formas de onda que originam potência; CSV de valores finais sozinho não permite auditar erro de fase.

Avaliar repetição (tipo A) e calibração/especificação/resolução/geometria (tipo B). Para y=f(x), calcular u_c²(y)=J Cov(x) Jᵀ; se não linear, variar os parâmetros numericamente e usar Monte Carlo com distribuições documentadas. Reportar U=k u_c e justificar k; k=2 é uma escolha de cobertura aproximada sob hipóteses adequadas, não uma garantia automática. Esses procedimentos seguem [NIST — incerteza combinada](https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-5-combined-standard-uncertainty) e [NIST — incerteza expandida](https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-6-expanded-uncertainty).

Para campo: propagar corrente, sensor/offset, posição/orientação, raio, separação, dimensões do pacote e discretização. Para ressonância: L, C, M, perdas, carga, malha de frequências e incerteza do pico. Para potência: ganho de cada canal, shunt, sincronismo/fase, ruído, distorção, temperatura e correlação entre canais. A aproximação geométrica não pode ser escondida dentro do erro do sensor.

Metas iniciais de projeto: U(I)/I≤2%, U(B)/B≤3% onde o sinal >10 vezes o ruído, U(f_pico)/f_pico≤2%, e U(P_entrada)/P_entrada≤3% nas condições em que P_entrada não está próxima de zero por cancelamento. Se o sistema disponível não atingir a meta, registrar a incerteza maior e melhorar o ensaio; não declarar concordância só porque o intervalo é enorme. Perto de zeros, usar incerteza absoluta.

Definir resíduo r=y_medido−y_modelo e incerteza combinada u_r, incluindo o modelo. Uma meta de concordância é |r|≤2u_r para pontos previamente escolhidos, sem ajustar parâmetros livres depois de olhar os dados. Muitos pontos exigem avaliar resíduos conjuntos/covariância e corrigir a decisão para multiplicidade; não interpretar um único ponto fora de 2u como física nova.

No cancelamento central, o resultado deve ser compatível com zero dentro de U absoluto; objetivo adicional de engenharia: resíduo ≤5% do campo em fase com correntes reais comparáveis. Uma tolerância de 5% é escolhida para a bancada, não uma lei da natureza.

Para potência estacionária, r_P=P_entrada−P_carga−P_perdas. Exigir |r_P|≤2u_c(r_P), controlando deriva e número de ciclos. Num ensaio de eventual excesso, ε=P_carga+P_perdas−P_entrada: ε>2u_c é um sinal para auditar primeiro ganho, fase, entradas omitidas e energia armazenada. Investigação extraordinária só prossegue após repetição, controles, previsão independente e demonstração de que a diferença não decorre da cadeia de medição. Não há ε experimental nesta entrega.

## 9. Modelo PI separado e sua implementação futura

O ensaio PI usa planta RL DC: L dI/dt=V−RI. Capacitores ficam contornados e o receptor desconectado. Usar e[k]=I_ref−I_medido e comando V[k]=sat(V0+Kp e[k]+Ki Ts Σe[k]). Definir unidades Kp em V/A e Ki em V/(A·s), período de amostragem e atraso. Implementar anti-windup, limites de tensão/corrente/temperatura e parada. Consultar os parâmetros concretos do código do modelo; metas abaixo pertencem ao ensaio físico futuro.

Os parâmetros PI não são determinados pela imagem. Medir R/L e atraso da planta, escolher resposta alvo e validar com degraus pequenos. O registro numérico de PI demonstra apenas comportamento daquela planta RL idealizada. A implementação física depende dos sensores, DAC e amplificador DC escolhidos. Para dx/dt=A x, estabilidade assintótica linear exige Re(λ(A))<0; autovalores positivos de uma matriz de energia representam outra condição. Esse esclarecimento evita a ambiguidade do quadro 11. Controle de amplitude AC não foi implementado por esse teste e necessitaria de projeto próprio.

## 10. Vácuo e gravidade: que observável faltaria

Reduzir gás numa câmara corresponde a medir pressão em pascal; mesmo métodos que usam átomos frios medem densidade/pressão de gás residual, como descreve [NIST — padrão de pressão de vácuo](https://www.nist.gov/news-events/news/2022/07/primary-standard-measuring-vacuum). O estado de vácuo em QFT é definido no espaço de estados e pela teoria dos campos, não pelo desenho de uma coluna ou leitura de manômetro; ver [Cambridge — Quantum Field Theory, seção 2.3](https://www.damtp.cam.ac.uk/user/tong/qft/qfthtml/S2.html). Para experimentar um efeito específico, é necessário definir preparação, Hamiltoniano, fronteiras, observável e diferença esperada em relação ao modelo convencional.

Em SI, Gμν+Λgμν=(8πG/c⁴)Tμν, quando T representa energia-momento-tensões. O c⁴ mostrado no pôster é apropriado nessa convenção. A dificuldade é especificar T, condições de contorno e resolver a métrica; [MIT — guia de relatividade geral, aula 12](https://web.mit.edu/sahughes/www/8.962/SP2020/lecture_guide.pdf) apresenta a relação e seu limite de unidades.

Uma escala dimensional local para a contribuição magnética é κu_B, com κ=8πG/c⁴ e u_B=B²/(2µ0). Por exemplo, B=100 µT corresponde a u_B≈3,98×10⁻³ J/m³ e κu_B≈8,3×10⁻⁴⁶ m⁻². Esta é uma estimativa de ordem de grandeza de componentes de fonte/curvatura, não solução gravitacional, força medida, mapa de R ou prova de controle do espaço-tempo. O tensor eletromagnético clássico em quatro dimensões tem traço nulo; para fonte exclusivamente EM e Λ=0, a equação implica escalar de Ricci R=0, embora o tensor de Ricci possa ser não nulo. O traço do tensor EM e sua relação com a fonte gravitacional são apresentados em [David Tong — Electromagnetism, seção 5.6.2, página impressa 131](https://davidtong.org/pdfs/teaching/electromagnetism/electro.pdf). Matéria dos suportes e campo elétrico também entram num problema gravitacional completo. Não chamar κu_B de escalar de Ricci calculado.

Propulsão precisa especificar força e fluxo de momento de todo o sistema, incluindo cabos, ar, suportes e radiação. Alteração de matéria precisa especificar amostra, estado inicial, observável e efeito previsto. Comunicação quântica precisa especificar estados, preparação, canal e medidas. Para wormholes, faltam solução da métrica, fonte requerida, condições de energia, estabilidade e mecanismo físico; uma superfície desenhada não define esses itens. O inventário de lacunas detalha o caminho de cada hipótese.

## 11. Fases de desenvolvimento e entregas futuras

1. **Digital:** revisar montagem 3D, cotas, enrolamentos, matriz acoplada, balanço de potência e convergência numérica. O relatório de testes do software deve nomear o que foi executado; não preencher resultados físicos a partir dele.
2. **Mecânica:** fabricar apenas suportes e gabaritos; conferir tolerâncias e acesso aos sensores; ajustar CAD conforme medidas.
3. **Elétrica:** enrolar e caracterizar bobinas; selecionar instrumentos externos; montar ramo único de baixa tensão e medir, depois incluir segundo ramo e receptor.
4. **Caracterização:** executar P01–P07 e P09–P10; guardar dados, ajustar somente parâmetros medidos e publicar resíduos/instrumentação.
5. **Controle separado:** implementar PI RL DC no hardware selecionado e executar P08 com limites e registro; decidir depois se é necessário desenvolver uma malha AC própria.
6. **Pesquisa adicional:** escolher uma alegação extraordinária e formular previsão independente mensurável antes de comprar instrumentos ou desenhar sua implementação. Comparar com Maxwell, térmica, acústica e efeitos de cabos, e reproduzir com outro arranjo.

Ao concluir ensaios, preencher um relatório por hipótese com previsão anterior, observações, incerteza, controles e decisão: compatível, incompatível ou inconclusivo. O termo **comprovado** não deve ser usado para funções do pôster que não tenham modelo operacional e medição própria.

## Referências e autoria do material

As fontes primárias citadas sustentam métodos convencionais; nenhuma demonstra o aparelho extraordinário da imagem. As dimensões, metas, sequência de ensaios e divisão dos módulos são escolhas deste projeto. O Atlas fornecido atribui a Adilson Oliveira — 7dsolv a autoria editorial e dos materiais, distingue os seus testes de experimento e corrige os pôsteres preliminares no Apêndice G. Essas declarações foram lidas como conteúdo de referência, sem transformá-las em instruções de execução.
