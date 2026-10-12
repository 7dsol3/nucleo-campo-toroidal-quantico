# Modelo eletromagnético e validação

Este diretório implementa um demonstrador clássico de duas bobinas circulares no ar, em série aditiva, com capacitor e resistência limitadora. Ele serve para prever um experimento reproduzível. Não prova as alegações de energia do vácuo, curvatura do espaço-tempo, wormholes ou propulsão quântica da arte de referência.

## Executar

No PowerShell, dentro deste diretório:

```powershell
py modelo.py --output resultados
py validar.py --output resultados/resultados_validacao.json
```

Python 3.12 e biblioteca padrão; não precisa instalar pacotes. Para explorar parâmetros, copie `configuracao.json`, ajuste a cópia e execute `py modelo.py --config sua_configuracao.json --output outro_resultado`. As medidas físicas do CAD precisam acompanhar qualquer alteração geométrica.

## Geometria nominal

São duas bobinas coaxiais com raio médio 100 mm, centros separados 100 mm e 50 espiras em cada bobina. Cada pacote usa cinco camadas radiais e dez espiras axiais por camada. O fio tem diâmetro de cobre 1,0 mm e diâmetro isolado nominal 1,1 mm: pacote radial 5,5 mm e axial 11 mm. O comprimento estimado é `2 × 50 × 2π × 0,100 + 1` metros, incluindo um metro adicional total de terminais. O diâmetro interno nominal do pacote é 194,5 mm; externo, 205,5 mm. Isso descreve o enrolamento, não dimensões acabadas de suporte.

O pacote real é substituído por 50 filamentos circulares coincidentes no raio médio para calcular o campo e a indutância mútua. Perto do enrolamento, essa simplificação não resolve o campo entre espiras. Pontos dentro da seção física do pacote são excluídos do mapa. Convergência numérica do filamento não equivale a precisão física de fabricação.

## Equações, unidades e aproximações

Todos os cálculos internos usam SI. `MU0 = 4π × 10⁻⁷ H/m` é a aproximação usual suficiente para este projeto. Em CA, os campos e tensões exportados indicam explicitamente RMS ou pico. RMS descreve a amplitude quadrática da senoide, não um campo constante.

Para cada bobina, Wheeler multicamada é `L[µH] = 0,8 a²N²/(6a + 9b + 10c)`, com `a` raio médio, `b` comprimento axial e `c` espessura radial, todos em polegadas. Conversão: 1 polegada = 0,0254 m. Trata-se de estimativa empírica; medir L e R no hardware é necessário para calibrar o circuito.

A indutância mútua é calculada pela integral reduzida de Neumann:

`M = µ0 N1 N2 R1 R2/2 × ∫[0,2π] cos(δ)/sqrt(R1²+R2²−2R1R2cos(δ)+d²) dδ`.

A integral usa 2.048 pontos médios periódicos. A ligação aditiva fornece `Ltotal = L1 + L2 + 2M`. O programa rejeita a combinação aproximada se `M ≥ L`, pois a matriz de indutância perderia energia positiva.

A resistência de cobre é `Rcu = ρ(T) comprimento/área`, com área `π(d_cobre/2)²` e `ρ(T) = 1,724×10⁻⁸ [1+0,00393(T−20)] Ωm`. Os 10 Ω de resistência limitadora são somados. Não há modelo térmico transiente; a temperatura do cobre é entrada, não resultado. Efeitos de pele, proximidade, ESR do capacitor, parasitas e impedância de saída do gerador são omitidos. A profundidade de penetração estimada é exportada como informação sobre esse limite. Uma saída de gerador de 50 Ω, se conectada sem estágio apropriado, muda substancialmente a previsão de corrente.

O capacitor nominal adotado é filme 10 µF/100 V. O valor ideal para exatamente 1.000 Hz também é exportado; ele não é o capacitor instalado. A fonte ideal é senoidal, com 2 V RMS no cenário inicial, frequência inicial 1.000 Hz e máximo declarado 5 V RMS. Resistência de 10 Ω/10 W e limite RMS de 0,5 A completam as entradas nominais. A especificação de 100 V é tratada como DC e comparada ao pico da senoide; aprovação real exige a ficha técnica para AC, frequência e corrente de ripple.

No regime permanente, `X = 2πfL − 1/(2πfC)`, `I_RMS = V_RMS/sqrt(R²+X²)`, `f0 = 1/(2πsqrt(LC))`, `Q = 2πf0L/R` e `Pentrada = I_RMS²R`. A potência é dissipada no cobre e na resistência. Não há carga útil neste circuito: a saída útil é zero. A energia magnética média é `LI_RMS²/2` e máxima `LI_RMS²`; a energia elétrica máxima é `CVcap_RMS²`. Na ressonância, os máximos são iguais; essas energias oscilantes não são produção líquida.

O limite de 0,5 A é uma verificação de domínio. O programa não recorta corrente nem assume que a fonte continue senoidal quando entra em limitação. Um resultado que exceda esse limite é marcado inválido para o modo de tensão ideal; a previsão linear permanece visível para mostrar o motivo.

O campo usa Biot–Savart: `B = µ0NI/(4π) ∮ dℓ × r/r³`. A discretização usa 360 elementos tangenciais por circunferência. No eixo, a referência analítica é `Bz(z)=µ0NIR²/[2(R²+(z−zc)²)^(3/2)]` por bobina. Para separação igual ao raio, o centro obedece ao limite de Helmholtz `B = (4/5)^(3/2) µ0NI/R`.

## Arquivos e interpretação

- `resultados.json`: parâmetros, ponto inicial, ressonância e cenário de 5 V RMS na ressonância; hipóteses e limites.
- `campo_eixo.csv`: 101 posições no eixo, solução numérica, referência analítica e erro relativo.
- `campo_plano_xz.csv`: 41 × 41 posições no plano y=0, campo vetorial RMS em tesla; célula vazia quando dentro do pacote.
- `campo.json`: os mesmos pontos para carregamento em visualizador.
- `varredura_frequencia.csv`: 100 a 5.000 Hz em passos de 10 Hz, mais o valor exato de f0.
- `configuracao_utilizada.json`: entradas reproduzíveis de cada execução.
- `resultados_validacao.json`: 13 verificações analíticas/numéricas e seus erros.

`validar.py` verifica o campo central e axial, limite de Helmholtz, superposição, reciprocidade de M, convergência angular, positividade da energia, ressonância, balanço de potência passivo, intercâmbio de energia e comportamento do limite de corrente. São verificações de implementação e das equações adotadas; não substituem medições, tolerâncias dos componentes, análise térmica ou teste de bancada.

## Reproduzir as fórmulas em JavaScript

Use os mesmos parâmetros SI e os mesmos 2.048 pontos angulares:

```javascript
const mu0 = 4 * Math.PI * 1e-7;
const a = radiusM / 0.0254, b = axialM / 0.0254, c = radialM / 0.0254;
const Lcoil = 1e-6 * 0.8 * a*a * turns*turns / (6*a + 9*b + 10*c);
let sum = 0;
const step = 2*Math.PI/2048;
for (let k = 0; k < 2048; k++) {
  const cosine = Math.cos((k+0.5)*step);
  sum += cosine / Math.sqrt(2*radiusM*radiusM*(1-cosine) + separationM*separationM);
}
const M = mu0*turns*turns*radiusM*radiusM/2 * step*sum;
const L = 2*Lcoil + 2*M;
const f0 = 1/(2*Math.PI*Math.sqrt(L*capacitorF));
const wireLength = 2*turns*2*Math.PI*radiusM + 1;
const Rcu = 1.724e-8*wireLength/(Math.PI*(0.001/2)**2);
const R = 10+Rcu;
const omega = 2*Math.PI*frequencyHz;
const X = omega*L - 1/(omega*capacitorF);
const Irms = sourceVrms/Math.hypot(R,X);
const BcenterRms = mu0*turns*Irms*radiusM**2/(radiusM**2+(separationM/2)**2)**1.5;
```

Esse trecho assume o fio e os terminais nominais a 20 °C. A implementação completa também valida as entradas, temperatura e limites dos componentes.
