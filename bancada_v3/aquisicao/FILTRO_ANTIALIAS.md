# Filtro analógico proposto para aquisição V3

**Estado: calculado, ainda não construído, caracterizado ou certificado.** A aquisição proposta usa 1 MSps por canal, confirmado pelo driver. Um filtro externo concreto melhora a rejeição fora da banda; nenhum filtro com queda finita elimina aliasing ou dispensa medir a cadeia real.

O conjunto tem cinco caminhos elétricos iguais, mais dois caminhos opcionais para `Vout` e `Vref` do sensor de campo e um para LM35H de temperatura. Cada caminho usa **um OPA4277PA DIP-14, quatro R de 3,16 kΩ ±1%, quatro C de 1 nF ±1% C0G/NP0 e quatro seguidores**, alimentados em ±12 V. A relação de peças com quantidades para cinco, sete e oito canais está em [filtro_componentes.csv](filtro_componentes.csv); o esquema funcional com todos os pinos está em [filtro.svg](filtro.svg). Não há PCB roteada ou Gerber validado neste pacote.

## Referência primária e limites do componente

O [datasheet oficial TI OPAx277 SBOS079C](https://www.ti.com/lit/gpn/OPA4277), páginas 5, 8–9 e 20–21, confirma a pinagem e estabilidade em ganho unitário. A alimentação recomendada vai de ±2 a ±18 V. GBW de 1 MHz e slew rate de 0,8 V/µs são **típicos**, sem mínimo garantido declarado nas respectivas linhas. O grau **OPA4277PA** tem limites diferentes dos graus P/U: na tabela a 25 °C, offset até ±50 µV e bias até ±2,8 nA. Não aplicar ao PA o destaque genérico de 1 nA. A TI recomenda desacoplamento cerâmico local de 100 nF por alimentação. [Página do produto e arquivos de simulação do fabricante](https://www.ti.com/product/OPA4277).

Não usar os valores típicos como certificado de margem, ruído, distorção ou rejeição de alias. Macromodelo SPICE do fabricante, resposta à carga/cabo e ensaio real complementam este cálculo; o script não executa SPICE.

## Conexão completa por canal

Usar índice `n=1…5` para A–E; `n=6/7` para F/G opcionais e `n=8` para H de temperatura. O escopo tem entradas com terra comum; todos os C de sinal, blindagens e retornos da placa vão ao mesmo SGND em estrela da bancada. Os filtros medem os nós já referenciados a SGND; não tornam as entradas diferenciais ou isoladas.

| Estágio | Entrada do RC | Nó após R e C para SGND | Entrada + do Uₙ | Saída e realimentação |
|---|---|---|---|---|
| 1 | Jₙ1 centro → Rₙ1 | Rₙ1 → Cₙ1 → SGND | Pino 3 | Pino 1 ligado diretamente ao 2 |
| 2 | Pino 1 → Rₙ2 | Rₙ2 → Cₙ2 → SGND | Pino 5 | Pino 7 ligado diretamente ao 6 |
| 3 | Pino 7 → Rₙ3 | Rₙ3 → Cₙ3 → SGND | Pino 10 | Pino 8 ligado diretamente ao 9 |
| 4 | Pino 8 → Rₙ4 | Rₙ4 → Cₙ4 → SGND | Pino 12 | Pino 14 ligado diretamente ao 13 |

Cada C conecta **o nó após seu R** a SGND; não está em série com a entrada. Os buffers evitam que um RC carregue diretamente o anterior. Ligar pino 14 a Rₙ5 de 47 Ω e então ao centro de Jₙ2/BNC do ADC. A realimentação pino 14→13 fica **antes** dos 47 Ω. Usar entrada ADC de 1 MΩ, sem terminador de 50 Ω. O resistor de saída reduz a interação com capacitância do cabo, mas não prova estabilidade: medir degrau, overshoot e oscilação com o cabo real.

Pino 4 recebe +12 V e pino 11 recebe −12 V. Em cada CI, colocar 100 nF cerâmico entre pino 4/SGND e entre pino 11/SGND, junto aos terminais. Adicionar 10 µF/25 V locais em cada trilho. No bulk positivo, positivo em +12 V e negativo em SGND. No bulk negativo, **positivo em SGND e negativo em −12 V**. Conferir o entalhe e a vista superior da peça antes de ligar. Alimentar pela fonte de bancada protegida da V3; o filtro não fornece intertravamento ou proteção de entrada contra conexão em nó errado.

No sinal de 5 Vrms, pico de 7,071 V, há folga calculada em relação aos trilhos ±12 V. A folga real deve considerar common-mode, carga, ruído e partidas; não testar alta amplitude com a placa desenergizada. Resistores dissipam menos de 8 mW no limite ideal de entrada de 5 Vrms para frequência muito alta, mas qualquer falha de conexão exige revisão. Posicionar as placas perto do nó medido, separar entrada/saída, evitar protoboard sem caracterização e manter cabos curtos. Medir capacitância do cabo mais ADC; 100 pF no script é apenas hipótese.

| Filtro | Entrada real | Destino ADC |
|---|---|---|
| U1 | Saída OPA548EVM 1 | A / `v_source1_v` |
| U2 | Topo do R série 1 | B / `v_series1_v` |
| U3 | Saída OPA548EVM 2 | C / `v_source2_v` |
| U4 | Topo do R série 2 | D / `v_series2_v` |
| U5 | Topo da carga receptora | E / `v_load_v` |
| U6 opcional | DRV425EVM Vout | F bruto |
| U7 opcional | DRV425EVM Vref | G bruto |
| U8 opcional | LM35H saída | H bruto |

Os filtros não substituem a calibração dos sensores. A resposta interna, sensibilidade medida, offset e orientação do DRV425EVM são adicionais. A banda de 47 kHz indicada na [tabela do DRV425, página 5](https://www.ti.com/lit/gpn/DRV425) para Rshunt=22 Ω não é automaticamente a banda da montagem com 100 Ω. Preservar F/G brutos; um `field_t` calculado por sensibilidade nominal não é automaticamente um campo calibrado. Para LM35H, preservar H bruto e documentar sensibilidade/offset/temperatura de referência da cadeia; o filtro tem ganho DC próximo de 1 e não corrige deriva ou instalação térmica.

## Transferência, taxa e erro entre canais

Ignorando não idealidades, `τ=RC=3,16 µs`, `fc=1/(2πRC)=50.365,488 Hz` e:

```text
HRC(f) = (1 + j f/fc)^(-4)
|HRC| = [1 + (f/fc)^2]^(-2)
faseRC = -4 atan(f/fc)
```

Os quatro polos coincidem; isto **não é um Butterworth de quarta ordem**. O corte global de −3 dB é aproximadamente 21,91 kHz. Em `f=fc`, cada estágio tem amplitude 1/√2, portanto a cascata tem amplitude 1/4, **−12,0412 dB** e fase desenrolada −180°. Em DC, ganho RC ideal é 1.

| Frequência | Atenuação RC ideal | Ganho / fase relevantes |
|---|---|---|
| 5 kHz | 0,17037 dB | 0,9805768 / −22,6777° |
| Nyquist de 100 kSps: 50 kHz | 11,9151 dB | **Rejeitar esta taxa para este projeto de filtro** |
| Nyquist de 500 kSps: 250 kHz | 56,3557 dB | Taxa degradada; exige novo orçamento espectral |
| Nyquist de 1 MSps: 500 kHz | 79,9223 dB | Padrão proposto; exige caracterização física |

O projeto adota 70 dB **ideais** em Nyquist como critério interno de seleção de taxa, não como certificação de alias. Isso exige ao menos 748.629 S/s nominais, ou 763.829 S/s no canto R/C mais rápido de ±1%. Assim, o padrão de 1 MSps atende ao critério calculado; 500 kSps e 100 kSps não atendem. O campo de metadados `antialias_cutoff_hz` não torna uma taxa inadequada válida. Um polo de 50,365 kHz já fica acima de Nyquist a 100 kSps; a aquisição deve ser refeita ou o filtro reprojetado. Estes arquivos não alteram automaticamente a configuração do capturador.

O script também calcula quatro seguidores como polos de 1 MHz, baseados somente no GBW típico, mais 47 Ω com ADC de 1 MΩ e capacitância total **assumida** de 100 pF. A 5 kHz, essa aproximação completa dá ganho 0,9804817 e fase −23,8321°. O modelo ignora ganho aberto finito, outros polos, capacitâncias de entrada, dinâmica de saída, acoplamento, PSRR, dispersão térmica e slew não linear. Nunca usar sua rejeição adicional como garantia.

Para 5 Vrms a 5 kHz, `SRnecessário=2π f sqrt(2) Vrms=0,222144 V/µs`. A razão entre slew típico e necessidade é 3,60, **sem margem mínima garantida**. Medir distorção e a maior amplitude no primeiro estágio, que vê o maior sinal.

O script enumera 256 cantos independentes de quatro R e quatro C ±1%. A 5 kHz, o ganho RC pode ir de 0,9798001 a 0,9813314, a fase de −23,13046° a −22,22926°; dois canais nos cantos opostos diferem até **0,156284% em ganho e 0,901195° em fase**, antes da dispersão dos amplificadores/cabos. Perto de potência em quadratura, menos de um grau já pode ser relevante. Isso precisa entrar no orçamento de fase; aplicar o mesmo ganho nominal aos canais não corrige sua diferença.

Uma senoide de interferência de 5 Vrms junto a 500 kHz ainda poderia produzir aproximadamente 0,5 mVrms após atenuação ideal de 80 dB. O erro admissível depende da amplitude do sinal útil; existem várias bandas que podem dobrar para a banda medida. É necessário medir/limitar espectro de entrada fora da banda e respostas reais, inclusive pickup após o último filtro e clipping dos buffers. **Atenuação em Nyquist isolada não limita o erro de alias de um espectro desconhecido.**

## Carregamento e balanço de potência

O primeiro RC carrega o nó mesmo que o opamp tenha alta impedância. Ignorando bias/parasitismo, a admitância vista é:

```text
Yin(f) = 1 / [3160 + 1/(j 2π f 1nF)]
Iin = Yin * Vnó
PentradaRC = |Vnó,rms|^2 Re(Yin)
```

Em 5 kHz, `|Zin|=31.987,46 Ω`; em 1400 Hz, 113.726,01 Ω. Um nó de 5 Vrms fornece 156,31 µArms ao RC de entrada a 5 kHz, com 77,21 µW de potência real. O carregamento complexo relativo `|R*Yin|` vale **0,031262% para 10 Ω e 0,312623% para 100 Ω** em 5 kHz. Para fonte de Thévenin resistiva, `Vcom/Vsem=1/(1+R*Yin)`: no caso 10 Ω, módulo 0,9999691 e fase −0,017824°; em 100 Ω, módulo 0,9996864 e fase −0,178188°. Estes são exemplos de carregamento, não uma solução nova do sistema acoplado inteiro.

A corrente do filtro ligado ao shunt **não atravessa o resistor de 10 Ω**. A corrente de ramo correta, por harmônico, é `Iramo=Vshunt/Rshunt + Yin_shunt*Vshunt`. A corrente da porta do amplificador também inclui `Yin_source*Vsource`. Portanto `mean(Vsource*Vshunt/Rshunt)` não mede sozinho toda a potência saindo do amplificador quando estes filtros estão conectados. Em 5 kHz, Vsource≤5 Vrms e Vshunt≤5 Vrms, a contribuição omitida do filtro do shunt tem limite conservador `|Vsource|*|Iin_shunt|≤0,78156 mW` por ramo; o RC conectado à própria fonte acrescenta até 0,07721 mW reais. O carregamento da carga receptora também deve entrar no modelo físico como admitância em paralelo; `Vload²/Rload` continua sendo somente a potência no resistor de carga.

Estas contribuições pequenas são **potência de instrumentação**, não energia anômala. Incorporar admitâncias complexas ao modelo de medição ou incluí-las explicitamente nos limites de erro. O analisador atual de cinco canais assume resistor puro para corrente; não recebe essa correção automaticamente. Se o orçamento não cobre o efeito, a comparação deve permanecer inconclusiva. O consumo DC dos quads e da instrumentação pertence a uma fronteira de alimentação separada da potência RLC.

## Calibração obrigatória da cadeia completa

Medir cada caminho com sua placa, cabo, faixa ADC, fonte e aterramento reais, incluindo ganho/offset e fase. Calibrar na frequência fundamental e nos harmônicos utilizados, documentando incerteza, temperatura, ruído, clipping e fonte de referência. Valores típicos e tolerâncias de compra não são certificados de calibração.

Para fasores, `Vnó(f)=VADC(f)/Hmedido(f)`. Para campo, `(F/HF − G/HG)/Ssensor(f)` só é aplicável se todas essas respostas tiverem sido medidas com referências compatíveis. Preservar arquivos brutos e salvar qualquer transformação em novos arquivos com hashes/proveniência. Uma multiplicação por `gain` na forma de onda não remove atraso de fase, nem corrige igualmente todos os harmônicos. O analisador aceita limites residuais de fase/banda; não deconvolve este filtro por conta própria. Sem orçamento de correção/cobertura suficiente, declarar `INCONCLUSIVE`.

Antes de considerar aliasing caracterizado: medir ganho/fase na banda útil, comparar canais, varrer frequências através de Nyquist e além dele, limitar o espectro de entrada, verificar estabilidade com cabo real, confirmar a taxa efetiva e repetir com amplitude/temperatura extremas permitidas. Rejeição de 79,92 dB neste documento é **resultado de equações**, não medição da placa. A banda nominal de um sensor também não substitui os filtros ou a calibração da diferença F−G.

## Reproduzir os cálculos

```powershell
py -B bancada_v3/aquisicao/filtro.py --output "$env:TEMP/nucleo_filtro_calculado.json"
```

O script usa biblioteca padrão, recusa sobrescrever a saída e executa 14 verificações independentes de identidades, extremos de tolerância, slew e seleção de taxa. O JSON identifica `origin=CALCULATED` e `PROPOSED_NOT_BUILT_NOT_MEASURED_NOT_CERTIFIED`. Nenhum resultado sintético é gravado como ensaio experimental e nenhum parâmetro dos instrumentos é alterado.
