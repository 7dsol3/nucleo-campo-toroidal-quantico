# Núcleo — projeto de bancada e simulação 3D

Adilson Oliveira / 7dsolv — referência autoral fornecida. Desenvolvimento preliminar de engenharia e cálculos nesta entrega: 12 de outubro de 2026.

## 1. O resultado que podemos testar

Uma bancada de duas bobinas circulares, alimentada por uma fonte externa, permite verificar três resultados: distribuição do campo magnético, resposta de ressonância elétrica e balanço de potência. Seu formato aproveita os dois anéis do conceito visual. Os raios, materiais, enrolamento e alimentação definidos aqui são escolhas novas de projeto: não são medidas recuperadas da imagem.

A bancada é um demonstrador eletromagnético. Os campos no centro são principalmente axiais. A expressão “toroidal” descreve a forma anular dos suportes; o enrolamento desta versão dá voltas ao redor do eixo, diferentemente de um solenoide toroidal com voltas ao redor da seção do toro.

Não existe nos arquivos enviados evidência experimental de extração de energia do vácuo, controle de curvatura, propulsão sem reação ou wormholes. O próprio Atlas, páginas 3, 22, 23 e 28, distingue matemática, ilustração e comprovação experimental. Este projeto respeita essa distinção e entrega uma hipótese convencional que pode ser confrontada com um instrumento.

## 2. Especificação mecânica de referência

Todas as medidas abaixo estão em milímetros. A face inferior da base é z = 0; os centros das bobinas estão em z = 60 e 160. No cálculo de campo, z = 0 corresponde ao ponto médio entre as bobinas, isto é, z = 110 no CAD.

| Elemento | Quantidade | Dimensão nominal / posição |
|---|---|---|
| Base de policarbonato | 1 | 260 × 260 × 8; quatro furos Ø 3,4 |
| Carretel anular isolante | 2 | Ø externo 220; altura 15,4; flanges de 2 |
| Vão axial do carretel | 2 | 11,4, para pacote de fio de 11 e folga total 0,4 |
| Manga do carretel | 2 | Ø interno 190,5; Ø externo 194,5 |
| Abertura dos flanges | 2 | Ø 188 |
| Enrolamento | 2 | 50 espiras, 5 camadas radiais × 10 voltas axiais |
| Fio | aproximadamente 70 m para compra | Ø cobre 1,0; Ø isolado nominal máximo 1,1 |
| Pacote de fio | 2 | 5,5 radial × 11 axial; raio médio 100 |
| Centros de camadas | 5 por bobina | raios 97,8; 98,9; 100; 101,1; 102,2 |
| Furos de montagem | 4 por flange/base | Ø 3,4; raio 107, ângulos 45/135/225/315 graus |
| Coordenadas dos furos | 4 | (±75,6604; ±75,6604) |
| Espaçador inferior isolante | 4 | Ø externo 6; furo 3,4; comprimento 44,3 |
| Espaçador intermediário isolante | 4 | Ø externo 6; furo 3,4; comprimento 84,6 |
| Haste roscada | 4 | Nylon M3 × 180 |
| Porca / arruela | 8 de cada | M3; arruela Ø 6 × 0,5 com furo 3,4 |
| Pé adesivo | 4 | Ø 12 × 6, nos pontos (±110; ±110) |

Verificações de empilhamento: 8 + 44,3 + 7,7 = 60; 15,4 + 84,6 = 100. Distância livre entre espaçador e envelope do fio: 1,25 mm. Margem mínima do furo à borda externa do flange: 1,3 mm; isso pede aperto leve e revisão caso se pretenda carga maior. As arruelas ficam somente na parte inferior da base e superior da montagem. Inserir arruelas entre os espaçadores muda a distância entre centros.

As hastes no CAD vão de z = -5 até 175; os pés chegam a z = -6. Altura do conjunto mecânico de referência: aproximadamente 181 mm. Terminais, transições entre camadas e eletrônica externa exigem espaço adicional. O fio ideal totaliza 62,832 m nas espiras; o cálculo inclui 1 m adicional de terminais. Comprar cerca de 70 m deixa margem de enrolamento; medir o comprimento/resistência real.

## 3. Fabricação e montagem

1. Cortar e furar a base conforme o desenho cotado. Usar suportes não magnéticos e material isolante para evitar espiras condutoras fechadas e perturbações do campo.
2. Imprimir dois carretéis em material isolante rígido, sem mudar a escala. Diâmetro 220 mm: com brim de 3 mm, a área útil precisa acomodar pelo menos 226 mm. Recomenda-se mesa de 230 mm ou maior. O flange superior tem balanço radial de 12,75 mm e exige suporte removível; limpar o canal antes de enrolar. O projeto ainda não foi fatiado ou impresso.
3. Conferir o diâmetro externo do fio. Se for maior que 1,1 mm, redesenhar o canal, altura e espaçadores. A pequena folga do projeto não pode compensar um fio incompatível.
4. Enrolar 10 voltas lado a lado no sentido axial, repetindo em 5 camadas radiais. Usar gabarito giratório, contar 50 voltas por bobina, proteger o esmalte e reservar terminais. As transições e terminais não são modelados como condutores no OBJ. Fixar o fio com material isolante apropriado.
5. Montar cada haste: porca, arruela, base, espaçador 44,3, carretel inferior 15,4, espaçador 84,6, carretel superior 15,4, arruela e porca. Não adicionar arruelas intermediárias. Apertar levemente e medir alinhamento/separação reais.
6. Medir continuidade, isolamento, resistência, indutância de cada bobina e indutância do par. Marcar os terminais para ligação que soma os campos. Inverter uma bobina deve produzir cancelamento no centro com correntes iguais; isso serve como controle experimental.

Tolerâncias iniciais desejadas: peças impressas ±0,3 mm; comprimento dos espaçadores ±0,1 mm; conferir o conjunto com paquímetro. São alvos de fabricação propostos, não resultados obtidos. Adaptar os furos após calibrar o processo. Nenhuma verificação digital substitui conferir a peça impressa.

## 4. Circuito e instrumentação

Circuito de ensaio AC: fonte senoidal isolada → resistor não indutivo de 10 Ω → capacitor de filme de 10 µF → bobina inferior → bobina superior, em série aditiva → retorno da fonte. Usar tensão terminal inicial de 2 V RMS e faixa de até 5 V RMS, 100 a 5.000 Hz. Limite de corrente RMS 0,5 A. O limite é um teto; não implica que a fonte alcance 0,5 A em toda frequência. O instrumento não pode distorcer a senoide ou entrar em limitação durante um ensaio usado para validar o modelo linear.

| Item elétrico / instrumento | Requisito inicial |
|---|---|
| Fonte AC | Saída senoidal isolada e protegida; 100–5.000 Hz; 0–5 V RMS; limite ≤ 0,5 A RMS |
| Fonte DC para mapa estático | Isolada, baixa tensão e limitada em corrente; ajustar 0–0,5 A |
| Resistor de referência | 10 Ω, não indutivo, 10 W; medir valor real e usar I = Vres/R |
| Capacitor | Filme não polarizado, 10 µF ±5%, ≥100 VDC; verificar limite AC, corrente e frequência no fabricante |
| Osciloscópio | Medir tensão, corrente por resistor e fase; sonda diferencial/isolada quando necessária |
| Multímetro / LCR | True RMS com banda compatível; medir R, L e C nas condições do ensaio |
| Sonda de campo DC | Hall/magnetômetro calibrado; resolução desejada da ordem de 1 µT |
| Medição de campo AC | Sensor calibrado até 5 kHz ou bobina de busca com área/voltas e resposta conhecidas |
| Sensor térmico / posicionamento | Termômetro; gabarito não magnético; régua e paquímetro |

Um gerador comum com saída de 50 Ω pode ser insuficiente; a fonte/amplificador precisa ser selecionada para esta carga. Alimentação DC de 12 V não equivale a 12 V RMS na saída AC. Esta entrega especifica um instrumento externo e não contém uma placa completa de amplificação, layout de PCB ou certificação de equipamento.

Para ensaio DC retirar o capacitor série: ele bloqueia corrente contínua. Para AC não substituir o capacitor de filme por um eletrolítico polarizado comum. Comparar tensão de pico e corrente RMS previstas com o catálogo; a classificação em VDC não confirma automaticamente serviço AC. Instrumentar a tensão nos terminais da bancada e no resistor. Saídas de amplificadores em ponte exigem atenção à referência do osciloscópio: terras comuns podem curto-circuitar a saída.

Começar em baixa amplitude e observar temperatura. Adotar inicialmente parada a 45 °C no enrolamento até validar o material e a montagem. Conexões isoladas, limite de corrente e parada acessível fazem parte do ensaio. O projeto não inclui vácuo, plasma, criogenia ou alta tensão.

## 5. Modelo físico calculado

O modelo usa unidades SI e duas bobinas idênticas no ar. As 50 voltas de cada bobina são aproximadas por espiras coincidentes no raio médio para o campo. Biot–Savart integra numericamente elementos tangenciais; o código Python aceita pontos tridimensionais (x,y,z). O visualizador mostra um corte x–z e a montagem mecânica em 3D. Não é um solver FEM completo.

Equações principais:

```text
B(x) = (μ0 / 4π) Σ N I ∫ (dl × r) / |r|³
Bz(z) = (μ0 N I R² / 2) Σ [R² + (z - zcentro)²]^(-3/2)
Bz(0), com separação R = (4/5)^(3/2) μ0 N I / R
Lserie = 2 Lbobina + 2 M
Lbobina [µH] ≈ 0,8 a² N² / (6 a + 9 b + 10 c)
a = raio médio; b = largura axial; c = espessura radial, em polegadas
M calculado pela integral de Neumann para espiras coaxiais médias
Rcobre = ρ20 (1 + α [T - 20]) comprimento / área
Z = Rtotal + j [2π f Lserie - 1/(2π f C)]
I_rms = V_rms / |Z|; f0 = 1 / (2π √[Lserie C])
Pentrada = I_rms² Rtotal; Umagnetica_max = Lserie I_rms²
```

Constantes aproximadas: μ0 ≈ 4π × 10^-7 H/m; resistividade do cobre a 20 °C 1,724 × 10^-8 Ωm; coeficiente térmico 0,00393 por °C. μ0 é aproximado aqui como constante de engenharia, não tratado como valor exato da definição atual do SI. A temperatura é entrada do cálculo, sem solução térmica.

Wheeler aproxima a autoindutância do pacote; Neumann aproxima a indutância mútua dos raios médios. A matriz de indutâncias deve ter energia positiva, L ± M > 0. Os códigos verificam isso na referência. No campo, pontos do envelope dos fios são excluídos; um filamento ideal é singular sobre o condutor.

Perdas peliculares/proximidade, ESR do capacitor, perdas do instrumento, capacitâncias parasitas, terminais e distribuição real de corrente não estão resolvidos. Em 100–5.000 Hz e dimensão de cerca de 0,2 m, a aproximação quase estática é uma primeira etapa apropriada; calibrar R/L/C em frequência antes de exigir precisão experimental. COMSOL ou outro solver FEM pode refinar campos, circuitos, perdas e temperatura após informar materiais, domínio de ar, condições de contorno e fontes.

## 6. Previsões de referência

Fonte 2 V RMS; frequência 1.000 Hz; capacitor 10 µF; cobre a 20 °C; distância 100 mm.

| Grandeza calculada | Resultado |
|---|---|
| Autoindutância de cada bobina | 1,044299 mH, estimada |
| Indutância mútua | 0,123520 mH, estimada |
| Indutância total série aditiva | 2,335638 mH |
| Resistência de cobre, incluindo 1 m de terminais | 1,401151 Ω |
| Resistência série total modelada | 11,401151 Ω |
| Ressonância nominal com 10 µF | 1.041,400 Hz |
| Capacitor ideal para 1.000 Hz | 10,845131 µF; calibrar com L medida |
| Corrente a 1.000 Hz | 174,392 mA RMS |
| Campo central | 78,405 µT RMS; aproximadamente 110,881 µT de pico |
| Potência ativa de entrada na bancada | 0,346739 W |
| Dissipação no resistor de 10 Ω | 0,304126 W |
| Dissipação no cobre | 0,042613 W |
| Tensão no capacitor | aproximadamente 2,776 V RMS |
| Energia magnética máxima | aproximadamente 71,033 µJ |

Na ressonância e 2 V RMS: corrente prevista 175,421 mA. Com 5 V RMS na ressonância: 438,552 mA, resistor dissipando 1,923281 W e tensão de pico no capacitor 9,478488 V. Os limites de catálogo, aquecimento e transientes ainda precisam ser verificados fisicamente. A comparação digital de tensão com 100 VDC é apenas uma triagem, não comprova a adequação AC do capacitor.

O ponto 0,5 A é útil para a fórmula de campo: produz 224,794 µT RMS no centro ideal. A fonte nominal de até 5 V RMS, com 10 Ω em série, não chega a essa corrente. Não confundir um teto de projeto com um resultado garantido.

O modelo é passivo: a potência recebida vira calor. Não há uma carga útil modelada; não se calcula geração líquida de energia. Para analisar eficiência de um dispositivo futuro, incluir a carga e as perdas do amplificador, medir a entrada DC e definir a fronteira do balanço.

## 7. Plano de comprovação experimental

Hipótese H1: campo proporcional à corrente e distribuição compatível com Biot–Savart. Hipótese H2: resposta I/V com máximo perto da ressonância calculada a partir de L e C medidos. Registrar antes do ensaio as previsões, incertezas e critérios de aceitação.

1. Registrar geometria, número de voltas, materiais, valores medidos de R/L/C, temperatura e instrumentos/calibrações. Fotografar a montagem e identificar versão dos arquivos.
2. Em DC, medir o campo no centro com fonte desligada e correntes ±0,1 a ±0,5 A. Usar [B(+I)-B(-I)]/2 para reduzir o campo de fundo e offset estático. Comparar inclinação B/I com a previsão.
3. Mapear o eixo de z = -80 a +80 mm em passos de 10 mm, referidos ao ponto médio; incluir pontos fora do eixo. Comparar a mesma componente de campo do instrumento com a calculada.
4. Repetir controles: uma bobina, duas em série aditiva, uma invertida, fonte desligada e mudança deliberada de separação. Recalcular a indutância e a corrente ao trocar ligação ou distância.
5. Em AC, varrer 100–5.000 Hz com mais pontos perto de f0. Registrar frequência, tensão terminal RMS, corrente RMS, fase, campo RMS e temperatura. Confirmar senoide sem clipping. Se a tensão variar, comparar I/V.
6. Medir potência pela média de v(t)i(t), em número inteiro de períodos, com aquisição simultânea e fase calibrada. Separar a entrada DC do amplificador, entrada AC da bancada, perdas e energia armazenada em transientes.
7. Repetir no mínimo três séries independentes e uma desmontagem/remontagem. Guardar CSV bruto, formas de onda e fotos. Alterações de modelo depois dos dados devem ser documentadas, sem forçar ajuste para obter aprovação.

Meta inicial de engenharia: campo e frequência de pico dentro de aproximadamente 5% da previsão calibrada e compatíveis com as incertezas combinadas. Esse percentual é uma escolha de projeto, não uma regra universal nem comprovação de física nova. Se o ruído, erro do sensor ou erro do modelo superarem a meta, melhorar o ensaio primeiro.

Registrar incertezas de corrente, posição, orientação, sensibilidade do sensor, fundo magnético, raio, separação, temperatura, frequência e L/C. Somar covariâncias quando aplicáveis e apresentar incerteza combinada ou expandida com fator de cobertura. Uma diferença só ganha significado depois de excluir erro instrumental, metal próximo, resposta de frequência, aquecimento e limitações do modelo.

## 8. O que a imagem ainda não define

Os termos de “campo quântico”, “informação”, “conversão de energia” e a matriz do pôster não têm um conjunto completo de ação, parâmetros, unidades, contornos e observáveis. A métrica parece exibir cinco coordenadas independentes, enquanto o texto anuncia quatro dimensões; isso precisa ser definido. O fator de Einstein 8πG/c⁴ está correto em SI, mas ele não fornece uma solução física sem tensor fonte e condições de contorno.

O determinante positivo de uma matriz não comprova estabilidade. Se ela rege dx/dt = Mx, decaimento exige partes reais negativas dos autovalores; autovalores positivos podem ter sentido para uma matriz de energia, que é um objeto diferente. O pôster não esclarece esse papel. A leitura detalhada está em auditoria_cientifica.md.

Para investigar uma hipótese extraordinária, escolher um observável e prever numericamente o desvio em relação à física convencional. Definir dinâmica, energia de entrada, mecanismo de leitura, tamanho esperado do efeito e um instrumento com ruído inferior a esse efeito. A sequência é: consistência matemática, previsão quantitativa, controle instrumental, experimento e reprodução independente. Uma animação ou um resultado PASS de código não percorre essa sequência sozinho.

## 9. Próximas etapas de desenvolvimento

| Etapa | Entrega necessária | Critério para avançar |
|---|---|---|
| Bancada inicial | Peças, bobinas, fonte e instrumentos; medir R/L/C e campo | Concordância reprodutível com incerteza reportada |
| Refino do modelo | Espiras distribuídas reais; cabos; R/L/C medidos; perdas AC | Convergência numérica e erro experimental reduzido |
| Simulação FEM | Domínio de ar 3D, materiais, malha, contornos, circuito e térmica | Independência de domínio/malha; comparação com bancada |
| Instrumentação automatizada | Aquisição sincronizada de V/I/B/T e calibração | Dados brutos auditáveis e balanço de potência fechado |
| Hipótese nova | Ação/dinâmica definida e efeito previsto distinto de Maxwell | Experimento discriminante e reprodução independente |

Para um campo toroidal verdadeiro, projetar outra bobina com voltas que abraçam a seção do toro; o campo tende a circular no interior do anel. Isso altera geometria, acesso do sensor e equações. Para plasma ou experimentos quânticos é necessário escolher um fenômeno específico, equipamentos especializados e um projeto próprio; ampliar esta bancada não produz esses efeitos automaticamente.

## 10. Verificação da entrega e limites

Foram realizadas 13 verificações numéricas do modelo clássico: soluções analíticas de campo, linearidade, configuração de Helmholtz, reciprocidade/convergência da indutância mútua, convergência fora do eixo, positividade da energia, ressonância, potência passiva e limites teóricos. O relatório JSON registra tolerâncias e erros. Os 37 testes citados no Atlas são outro conjunto, relatado pelo documento; suas fontes não foram anexadas nem reexecutadas nesta entrega.

As nove geometrias de malha do CAD foram verificadas quanto a fechamento, orientação e volume positivo; arquivos STL e OBJ foram inspecionados estruturalmente. O navegador foi testado em desktop e telas menores, com controles, importação/exportação e concordância com o cálculo Python. O registro final de verificações fica em validacao_entrega.json.

O que permanece pendente: renderizar a fonte SCAD no OpenSCAD, fatiar e imprimir, ensaiar tolerâncias/rigidez, selecionar o equipamento de alimentação, montar e medir. Nenhuma certificação de equipamento, desempenho térmico ou efeito quântico é afirmada. STL/OBJ são malhas; não foi entregue STEP de sólidos nativos.

## Referências

- Atlas das Estruturas Fundamentais, Adilson Oliveira — 7dsolv, edição técnica 1.0, documento fornecido; páginas 3, 13, 22, 23 e 28.
- MIT, bobinas de Helmholtz, exemplo 6: https://web.mit.edu/8.02-esg/Spring03/www/8.02ch30we.pdf
- MIT OpenCourseWare, circuitos AC: https://ocw.mit.edu/courses/8-02t-electricity-and-magnetism-spring-2005/resources/cha12ac_circuits/
- MIT OpenCourseWare, equações de Einstein: https://ocw.mit.edu/courses/8-033-relativity-fall-2006/02415213222b845bbec6e734c64d1718_fieldeqs.pdf
- NIST Technical Note 1297, incerteza de medição: https://www.nist.gov/pml/nist-technical-note-1297
- COMSOL, modelagem de bobinas e circuitos: https://www.comsol.com/support/learning-center/article/Modeling-Electromagnetic-Coils-8251

Fórmulas convencionais são apoiadas nessas fontes. Dimensões, metas, limites iniciais e organização da bancada são propostas desta entrega, sem validação física concluída.
