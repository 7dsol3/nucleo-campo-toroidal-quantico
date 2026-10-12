# Auditoria científica e protocolo de validação — bancada de campos e ressonância

Data: 12/10/2026. Material examinado: pôster **Núcleo de Campo Toroidal Quântico** e PDF **Atlas das Estruturas Fundamentais**, edição 1.0. Os números abaixo são previsões de projeto; nenhum ensaio físico da bancada foi realizado nesta entrega.

É possível construir um modelo 3D da aparência do pôster e uma bancada que realmente produza um campo magnético e apresente ressonância elétrica. O primeiro valida a geometria desenhada; o segundo permite testar eletromagnetismo conhecido. Esses resultados não comprovam geração de energia do vácuo, controle da gravidade, propulsão sem reação ou wormholes. Para investigar uma dessas alegações, falta uma hipótese física quantitativa própria e um experimento capaz de distinguir sua previsão das explicações convencionais.

## 1. O que o Atlas efetivamente sustenta

| Página do PDF | Evidência apresentada | Consequência para este projeto |
|---|---|---|
| 3 | Declaração de autoria editorial e 37 verificações locais de identidades/modelos; distingue explicitamente esses testes de comprovação experimental ou unificação. | Usar o Atlas como material de estudo e auditoria matemática. O número 37/37 é uma afirmação do documento; os arquivos originais desses testes não foram fornecidos nem reexecutados aqui. |
| 22 | Explica o alcance de um PASS, mostra o fator de Einstein em SI e analisa amortecimento no modelo linear autônomo. | Não transferir uma aprovação algébrica para um aparelho novo. No sistema apresentado ali, os autovalores que produzem decaimento têm parte real negativa. |
| 23 | Enumera problemas ainda abertos e exige hipótese, parâmetros observáveis e comparação quantitativa com medições. | Formular uma previsão mensurável antes de atribuir um efeito novo ao dispositivo. |
| 28 | Apêndice G rejeita unificação por justaposição de equações, conservação automática de tensores, testes completos por aprovação algébrica e arte como evidência. | A imagem deve ser rotulada como conceito artístico, não como engenharia experimental demonstrada. |

O Atlas já contém ressalvas que corrigem a interpretação mais forte do pôster. Não há no material fornecido um conjunto de medições de um núcleo físico operando.

## 2. Auditoria das expressões do pôster

1. **Equação de Einstein.** O pôster mostra `8πG/c⁴`, que corresponde ao fator usual quando `Tμν` é expresso como energia/momento/tensão em SI. Esse fator não é o problema central. A equação exige uma fonte `Tμν` definida e uma solução da métrica com condições de contorno; colocar nomes de fontes entre parênteses não calcula a curvatura gerada. [MIT — Einstein's Field Equations](https://ocw.mit.edu/courses/8-033-relativity-fall-2006/02415213222b845bbec6e734c64d1718_fieldeqs.pdf).
2. **Número de coordenadas e geometria.** Na métrica desenhada aparecem `t, r, θ, φ, ψ`. Se forem independentes, são cinco coordenadas, apesar do texto mencionar quatro dimensões. Se `ψ` for auxiliar ou dependente, isso precisa ser definido. Termos com coordenadas esféricas e uma coordenada adicional não bastam, sozinhos, para demonstrar uma topologia toroidal específica.
3. **Campos e acoplamentos indefinidos.** `Bμ`, `Cμ`, `κ`, `χ`, `λ`, o potencial `V`, os termos de informação e a matriz de acoplamento não têm unidades, valores, lei de evolução, estado inicial ou ligação com um sensor/material. Também falta a ação da qual derivariam as equações e o tensor de energia e momento. Sem essas definições, não existe um problema numérico fechado para simular.
4. **Conservação.** Escrever `∇μTμν = 0` é uma condição a satisfazer; não demonstra que o tensor proposto a satisfaz. São necessárias equações derivadas de uma ação consistente ou outra construção justificada, mais verificação das identidades e das condições de contorno. O próprio Atlas alerta para isso nas páginas 13 e 28.
5. **Estabilidade.** `det(M)>0` não garante estabilidade. Se `M` for a matriz dinâmica de `dx/dt=Mx`, o decaimento exige `Re(λ)<0` para todos os modos, no sistema linear autônomo. Exemplo: `M=diag(1,1)` tem determinante positivo e soluções que crescem como `eᵗ`. Uma matriz de energia positiva pode usar autovalores positivos, mas ela não é automaticamente a matriz de evolução. O pôster não define qual dos casos se aplica. O Atlas, página 22, usa corretamente partes reais negativas no seu exemplo de amortecimento.
6. **Escala visual.** A legenda artística de 10 m não fornece tolerâncias, materiais, circuitos, tensão, corrente ou mecanismos internos. Não é possível deduzir um aparelho de 10 m funcional dessa legenda. A bancada de 200 mm proposta é uma nova escolha de engenharia para testes acessíveis.

## 3. Hipóteses testáveis da primeira bancada

**H1 — campo magnético clássico:** duas bobinas circulares coaxiais, ligadas de modo que os campos se somem, produzem `B∝I` e a distribuição espacial calculada por Biot–Savart. Na aproximação de bobinas finas, separação igual ao raio gera a configuração de Helmholtz, com primeira e segunda derivadas axiais nulas no centro. [MIT — exemplo 6, páginas 9–10](https://web.mit.edu/8.02-esg/Spring03/www/8.02ch30we.pdf).

**H2 — ressonância elétrica clássica:** com capacitor e resistência em série, existe uma frequência em que as reatâncias se cancelam e a corrente por volt aplicado atinge o máximo. O pico depende de perdas, indutância e capacitância; não demonstra um efeito quântico. As equações RLC e a potência média estão nos materiais de [MIT — AC Circuits](https://ocw.mit.edu/courses/8-02t-electricity-and-magnetism-spring-2005/resources/cha12ac_circuits/).

Modelo básico da bancada, com grandezas em SI:

```text
Rraio = 0,100 m; s = 0,100 m; N = 50 voltas por bobina
z das bobinas = −s/2 e +s/2
Bz(z) = μ0 N I Rraio²/2 × {
  [Rraio²+(z−s/2)²]^(−3/2) + [Rraio²+(z+s/2)²]^(−3/2)
}
Bz(0) = (4/5)^(3/2) μ0 N I/Rraio, quando s=Rraio

Lpar = L1 + L2 + 2M, ligação que soma os campos
Z(ω) = Rtotal + j[ωLpar − 1/(ωC)]
I_rms = V_rms / |Z|
f0 = 1/(2π√(Lpar C))
Pentrada = média temporal de v(t)i(t)
Pentrada = V_rms I_rms cos(φ) = I_rms² Rtotal, modelo linear senoidal
```

Use `μ0≈4π×10⁻⁷ H/m` como aproximação de engenharia, e não como constante atualmente exata por definição. A simulação espacial deve somar as 100 espiras reais, distribuídas no pacote, ou declarar que usa o raio médio. O campo de um filamento ideal é singular no próprio filamento: pontos dentro do fio devem ser excluídos ou tratados com um modelo de seção finita. Em 100–5000 Hz e dimensões de 0,2 m, a aproximação quase estática é adequada para esta primeira previsão; perdas AC, conexões e resposta do sensor ainda exigem medição.

## 4. Parâmetros e resultados previstos

| Grandeza | Valor de projeto | Natureza/limite |
|---|---|---|
| Raio médio | 100 mm | Medir o raio médio efetivamente enrolado. |
| Separação entre planos médios | 100 mm | Não confundir com distância entre faces dos suportes. |
| Voltas | 50 em cada bobina | Contagem verificável; mesma corrente em série. |
| Fio | cobre, 1,0 mm nu; 1,1 mm com isolação, nominal | Confirmar diâmetro externo real antes de fabricar o canal. |
| Pacote de enrolamento | 5 camadas radiais × 10 voltas axiais; aproximadamente 5,5 × 11 mm | Folga de fabricação e diâmetro real podem alterar o pacote. |
| Corrente máxima | 0,50 A RMS em AC; 0,50 A em DC | Em senoide, 0,50 A RMS corresponde a 0,707 A de pico. |
| Campo central ideal | 224,8 µT a 0,50 A DC, ou 224,8 µT RMS em AC | Campo AC de pico ≈318 µT; somar/subtrair ambiente nas medições DC. |
| Comprimento de cobre | 62,83 m nas duas bobinas, antes de terminais/cabos | Reservar comprimento adicional documentado. |
| Resistência do cobre | aproximadamente 1,38 Ω a 20 °C, antes dos cabos | Estimativa por resistividade; medir resistência real e temperatura. |
| Dissipação no cobre | aproximadamente 0,345 W no par a 0,50 A | Não inclui resistores, amplificador, cabos e perdas AC. |
| Frequências | 100–5000 Hz; ponto inicial 1000 Hz | A ressonância depende de L/C reais; não é necessariamente 1000 Hz. |
| Capacitor inicial | 10 µF ±5%, polipropileno, nominal ≥100 VDC | Conferir no fabricante tensão AC permitida e corrente na frequência de trabalho. |
| Resistor em série | 10 Ω, 10 W, não indutivo | Atua como amortecimento e referência de corrente por sua tensão medida. |
| Fonte AC externa | 2 V RMS inicial; ajuste limitado a 5 V RMS | Amplificador senoidal isolado, protegido e instrumentado; hardware ainda a selecionar. |

Não fixar a indutância apenas pelo desenho. A ligação e a distância alteram a indutância mútua. Medir `Lpar` com o conjunto montado e com indicação da frequência de ensaio. A estimativa inicial Wheeler/Neumann de aproximadamente 2,335 mH, com C=10 µF, prevê ressonância perto de 1042 Hz. É uma aproximação de projeto, não uma medição. Um valor exato de 1000 Hz exigiria ajustar C a L medida. A energia magnética máxima, no modelo nominal, será aproximadamente 0,584 mJ a 0,50 A RMS, proveniente da fonte elétrica.

Com resistência idealizada de 10+1,38=11,38 Ω, 2 V RMS na ressonância produz cerca de 0,176 A RMS e 79 µT RMS no centro; 5 V RMS produz cerca de 0,439 A RMS e 198 µT RMS. Cabos e perdas reais reduzem esses valores. Portanto, 0,50 A é um teto de projeto, não uma corrente alcançável garantida com o limite de 5 V RMS.

## 5. Alimentação, instrumentos e orçamento de potência

- Fonte DC isolada de baixa tensão e limitada em corrente para o ensaio estático; o capacitor série deve ser retirado/contornado nesse ensaio.
- Gerador senoidal de 100–5000 Hz e amplificador adequado à carga para o ensaio AC. Um gerador comum de 50 Ω não entrega automaticamente 0,5 A. Registrar impedância de saída, limite de tensão, distorção e aquecimento.
- Capacitor inicial de polipropileno não polarizado, 10 µF ±5%, nominal ≥100 VDC, com capacitância medida, ESR e corrente admissível verificada na frequência de trabalho. A classificação em VDC não garante serviço AC. Conferir `V_C,rms=I_rms/(ωC)`, picos/transientes e corrente RMS no catálogo do fabricante. A 0,50 A RMS e 1000 Hz, o modelo dá aproximadamente 7,96 V RMS no capacitor; o valor nominal final depende de sua classificação AC e margem de projeto. Capacitor eletrolítico polarizado comum não é substituição direta.
- Resistor não indutivo de 10 Ω/10 W em série, com resistência medida, para obter `I=V_resistor/R` e amortecer o circuito; não é necessário outro shunt no modelo inicial. Multímetro true RMS com largura de banda adequada, medidor LCR e osciloscópio para corrente, tensão e fase. Sonda diferencial/isolada quando a saída do amplificador for em ponte: conectar terras de osciloscópio sem verificar a topologia pode curto-circuitar a saída.
- Magnetômetro ou sonda Hall calibrada para DC; para AC, sensor calibrado com largura de banda comprovada até 5 kHz, ou bobina de captura com área/voltas conhecidas e integração calibrada. Um magnetômetro de celular não é instrumento de validação dessa faixa AC.
- Régua/paquímetro, suporte de posicionamento não magnético e sensor de temperatura.

Dimensionar resistores e fonte pelo circuito final. Se `Rtotal=Rcobre+Rcabos+R10Ω+Rsaída+ESR`, cada elemento dissipa aproximadamente `I_rms²Ri`. A 0,50 A, o resistor de 10 Ω dissipa 2,5 W; sua classificação de 10 W oferece margem apenas quando a montagem térmica respeita o fabricante. No modelo nominal em ressonância, 2 V RMS entregam aproximadamente 0,351 W ao circuito; 5 V RMS entregam aproximadamente 2,20 W. Uma fonte de 12 V DC não implica 12 V RMS senoidais disponíveis na carga: isso depende do amplificador.

A alimentação de 12 V e a capacidade de saída de até 5 V RMS são requisitos para seleção de um equipamento externo protegido. Nenhuma placa completa de amplificador, esquema eletrônico final, layout ou certificação de equipamento foi entregue nesta etapa. Usar apenas um instrumento cuja saída senoidal, isolamento, proteção e corrente admissível tenham sido verificados para esta carga.

No pico de ressonância, tensão no indutor/capacitor pode superar a tensão terminal dependendo do fator de qualidade. Começar com sinal baixo, observar tensões e temperatura e só então elevar a amplitude. Limite de corrente/fusível, terminais isolados e parada acessível integram a bancada. Para suportes impressos, adotar um limite inicial conservador de 45 °C no enrolamento e pausar antes de ultrapassá-lo; revisar o limite conforme material e medição térmica. Essas escolhas pertencem ao teste proposto, não são um certificado de segurança de um equipamento pronto.

## 6. Protocolo antes de declarar funcionamento

1. **Inspeção:** fotografar montagem, contar voltas, medir raio, pacote, separação, resistência, L e C. Registrar materiais, instrumentos, calibrações, tolerâncias, temperatura e versão do modelo. Manter peças ferromagnéticas afastadas da região de medição ou incluir sua influência.
2. **Campo DC:** com a geometria fixa, medir no centro em `I=0; ±0,1; ±0,2; ±0,3; ±0,4; ±0,5 A`. Calcular `[B(+I)−B(−I)]/2` na mesma orientação para reduzir o campo ambiente e o offset estático. Ajustar inclinação `B/I` sem modificar o raio para forçar concordância.
3. **Mapa:** medir `z` de −80 a +80 mm em passos de 10 mm, com corrente conhecida, e pontos fora do eixo. Comparar a componente medida com a mesma componente simulada, não magnitude vetorial com uma componente axial.
4. **Controles:** repetir com fonte desligada, uma única bobina e uma bobina invertida. Na ligação de campos opostos, o campo axial central ideal deve cancelar. Uma alteração deliberada de separação permite verificar a dependência geométrica. Recalcular L e limitar corrente ao mudar ligação.
5. **Ressonância AC:** varrer 100–5000 Hz, com mais pontos perto do pico. Usar amplitude terminal conhecida, sem saturação/limitação de corrente. Registrar simultaneamente `f, V_rms, I_rms, φ, B_rms, temperatura`. Se a tensão variar com a carga, usar `I_rms/V_rms` para analisar a resposta. Uma corrente imposta constante não exibirá o mesmo pico de corrente de uma fonte de tensão.
6. **Energia:** medir `v(t)` e `i(t)` no mesmo limite do sistema e integrar por número inteiro de períodos. Separar entrada DC do amplificador, entrada AC da bancada, perdas e saída a uma carga de teste. Com distorção, usar `média[vi]`, não apenas produto RMS. Durante transientes, incluir variação de energia armazenada em L e C.
7. **Repetibilidade:** executar pelo menos três séries independentes, repetir após desmontar/remontar e usar ordem alternada de correntes/frequências para identificar deriva térmica. Guardar CSV bruto, formas de onda, incertezas e fotos.

Critérios iniciais propostos, a registrar antes das medições: campo central e perfil compatíveis com o modelo dentro da incerteza combinada; erro relativo do campo inferior a 5% apenas onde o sinal superar claramente o ruído; frequência do pico dentro de 5% da previsão com L/C medidos; ausência de saturação ou deriva térmica significativa. O limiar de 5% é uma meta de engenharia escolhida para esta bancada, não um critério universal de verdade física. Se a incerteza do instrumento já superar a meta, melhorar a medição antes de interpretar uma discrepância.

## 7. Incerteza e interpretação

Registrar componentes estatísticas (repetições) e componentes obtidas por especificação/calibração: corrente, sensibilidade/offset do sensor, posição e orientação, raio, separação, frequência, L, C, temperatura e fundo magnético. Combinar as incertezas por propagação, incluindo covariâncias quando necessárias, e reportar `u_c` ou `U=k u_c` com o fator `k` utilizado. Esses princípios de apresentação seguem a [NIST TN 1297 — incerteza combinada](https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-5-combined-standard-uncertainty) e [NIST — comunicação da incerteza](https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-7-reporting-uncertainty).

Meta inicial de instrumentação: corrente com incerteza de aproximadamente 1%, posicionamento da sonda e distância com aproximadamente 1 mm, resolução de campo na ordem de 1 µT e sensibilidade calibrada. São requisitos desejados; não são incertezas já obtidas. Separar erro do instrumento de erro da aproximação de bobina fina. Quando a propagação linear não for adequada, variar numericamente os parâmetros medidos e examinar a distribuição das previsões.

Uma medição diferente do modelo não estabelece automaticamente física nova: primeiro investigar orientação, campo ambiente, metal próximo, resposta de frequência, L dependente da montagem, ESR, efeito pelicular/proximidade, aquecimento, aterramento, clipping e erro de fase. Uma alegação de energia excedente exige que a diferença exceda a incerteza completa e persista com controles e reprodução independente. Nenhum desses resultados foi obtido no material fornecido.

## 8. O que ainda é necessário para testar a alegação extraordinária

Definir uma única alegação, por exemplo: “com a mesma potência de entrada, esta configuração produz um observável X que excede a previsão de Maxwell em ΔX”. É preciso especificar a ação/equações, unidades dos campos, acoplamentos e valores, estado inicial, contornos, materiais, fonte de energia, mecanismo de leitura e tamanho previsto do efeito. Depois vêm revisão de consistência dimensional, conservação, estabilidade com o operador adequado, limites conhecidos e análise de sensibilidade.

Só então selecionar instrumentos cujo ruído esteja abaixo de ΔX, escrever controles e limites de exclusão e realizar um experimento independente. Um mapa colorido de campo magnético não mede curvatura do espaço-tempo; um pico RLC não mede extração de energia do vácuo; uma animação luminosa não mede plasma. Nesta versão, as partes comprováveis são desenho/dimensões, montagem, campo magnético, resposta elétrica e balanço de potência convencional.

## Referências consultadas

- Documento fornecido: *Atlas das Estruturas Fundamentais*, Adilson Oliveira — 7dsolv, edição 1.0, páginas 3, 13, 22, 23 e 28.
- MIT: [campo de bobinas de Helmholtz — exemplo 6](https://web.mit.edu/8.02-esg/Spring03/www/8.02ch30we.pdf).
- MIT OpenCourseWare: [circuitos AC, ressonância RLC e potência](https://ocw.mit.edu/courses/8-02t-electricity-and-magnetism-spring-2005/resources/cha12ac_circuits/).
- MIT OpenCourseWare: [equações de campo de Einstein](https://ocw.mit.edu/courses/8-033-relativity-fall-2006/02415213222b845bbec6e734c64d1718_fieldeqs.pdf).
- NIST: [Technical Note 1297](https://www.nist.gov/pml/nist-technical-note-1297).

As fórmulas convencionais têm suporte nas referências acima; dimensões, corrente, metas de aceitação e organização do protocolo são escolhas propostas para esta bancada. Nenhuma referência citada demonstra o aparelho quântico/gravitacional imaginado no pôster.
