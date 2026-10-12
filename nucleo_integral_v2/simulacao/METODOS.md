# Modelo eletromagnético integral V2

Este pacote transforma a geometria ilustrada em um protótipo de bancada clássico. A previsão numérica não comprova o funcionamento de um aparelho físico nem fornece mecanismos para extrair energia do vácuo, alterar matéria, sustentar wormholes, produzir propulsão sem reação ou controlar o espaço-tempo. As etiquetas da referência visual são uma lista de hipóteses; elas não definem leis físicas ou componentes existentes.

## Referência geométrica e unidades

Tudo usa SI; z = 0 é o plano de base do CAD. As duas bobinas circulares têm raio médio 0,100 m, centros z = 0,065 e 0,185 m e 50 espiras cada. Cada pacote contém cinco camadas radiais e dez posições axiais. O cobre tem diâmetro 1,0 mm e o passo isolado é 1,1 mm. Os raios dos filamentos são 97,8; 98,9; 100,0; 101,1; 102,2 mm. Os centros axiais vão de −4,95 a +4,95 mm em relação a cada centro, com passo 1,1 mm. A dimensão externa nominal do pacote é 5,5 × 11,0 mm, incluindo o passo isolado.

O receptor no plano z = 0,125 m tem 20 espiras, raio médio 35 mm e carga de 100 Ω. Sua autoindutância usa um pacote de quatro camadas × cinco espiras, de dimensão externa 4,4 × 5,5 mm e cobre de 1 mm. Para campo e indutância mútua o receptor é aproximado por vinte filamentos coincidentes no raio médio. Essa aproximação deve ser substituída por geometria distribuída e comparação com FEM/medição para melhorar a precisão perto do receptor. Os campos dentro do envelope do receptor são excluídos. Os condutores de ligação contam na resistência, mas seus campos, capacitâncias e indutâncias não são calculados.

Há também um enrolamento verdadeiramente toroidal auxiliar: 48 espiras poloidais em torno de um anel no plano z = 0,125 m, com raio maior R = 135 mm e raio menor r = 8 mm, medidos até o centro do fio. Esse enrolamento está desligado no cenário inicial. Sua alimentação é uma terceira fonte de corrente especificada separadamente; a interface não fornece o projeto de um amplificador de potência.

## Circuito passivo com duas fontes e receptor real

Cada bobina principal tem uma porta senoidal independente, resistor em série de 10 Ω e capacitor em série de 10 µF. As fontes iniciais são 2 V RMS a 1.400 Hz e fase igual. O limite especificado é 5 V RMS e 0,5 A RMS em cada porta. Use saídas isoladas e amplitude efetivamente medida sob carga. Um gerador rotulado para carga de 50 Ω pode entregar outra tensão em alta impedância; a indicação do painel não substitui medição. O circuito proposto não é uma placa ou driver já fabricado.

O resistor de cada porta é especificado em 10 W. O capacitor selecionado tem especificação nominal de pelo menos 100 VDC, mas precisa ter a tensão, corrente e frequência de operação em CA verificadas na documentação do fabricante. O programa compara o pico √2·V_RMS com o limite nominal de 100 V; essa comparação isolada não valida a capacidade de operação em CA. A carga do receptor é 100 Ω/0,25 W. Esses são requisitos elétricos; o modelo não simula aumento de temperatura, ventilação ou falhas.

A autoindutância é uma **estimativa de Wheeler multicamada**:

`L[µH] = 0,8 · a² · N² / (6a + 9b + 10c)`

onde a é o raio médio, b o comprimento axial, c a profundidade radial, em polegadas. Espessura finita, passo helicoidal, ligações e tolerâncias introduzem erro. Meça L e R antes de ajustar a frequência real de ressonância.

A mútua entre dois filamentos circulares coaxiais é a integral de Neumann reduzida:

`M = (µ0 R1 R2 / 2) ∫[0,2π] cos δ / √(R1² + R2² − 2R1R2 cos δ + d²) dδ`.

O programa soma todos os 50 × 50 pares de espiras das bobinas principais, sem substituí-las por um único anel. Para acoplamento ao receptor soma 50 filamentos principais × 20 espiras equivalentes no raio médio do receptor. A quadratura angular usa pontos médios periódicos; 512 e 1.024 pontos são comparados na validação. A matriz L deve ser simétrica e positiva definida; a validação de Cholesky rejeita parâmetros incompatíveis com energia magnética positiva.

Usando fasores RMS e `i(t) = √2 Re[I exp(jωt)]`, o sistema é:

`[R1 + j(ωL1 − 1/(ωC1)), jωM12, jωM1r] [I1]   [V1]`

`[jωM12, R2 + j(ωL2 − 1/(ωC2)), jωM2r]   [I2] = [V2]`

`[jωM1r, jωM2r, Rr + Rload + jωLr]        [Ir]   [ 0]`

Aqui R1 e R2 incluem 10 Ω e resistência do cobre. A terceira linha é removida quando o receptor está desconectado. Inverter os terminais de uma bobina multiplica as suas mútuas pelo sinal da orientação. As correntes físicas usadas no campo são `Iphysical = orientation × Iport`. Alterar a fase da fonte e inverter o enrolamento são operações distintas, explicitamente implementadas.

O balanço é `Pfontes = Σ Re[V I*] = Σ R |I|²`. A potência entregue à carga é `Pload = Rload |Ir|²`, sempre incluída no balanço. A carga absorve energia proveniente das fontes. Alguns ajustes de fase podem exigir que uma fonte absorva potência da outra; uma fonte unidirecional não realiza esse ponto de operação sem circuito de proteção/absorção adequado. O programa assinala esse caso. Ele não recorta artificialmente a corrente: se o ponto ultrapassa os limites, a solução linear é marcada como inválida para uma fonte que sature.

As ressonâncias sem receptor para o par simétrico são `f+ = 1/[2π√((L+M)C)]` e `f− = 1/[2π√((L−M)C)]`. Com carga, a impedância do receptor também altera a resposta. Não há ganho de energia por ressonância. A frequência de máximo campo ou corrente pode diferir de uma estimativa de ressonância ideal devido a perdas e carga.

## Campo vetorial, fase e toroide

Para cada filamento aplica-se Biot–Savart:

`B(r) = µ0/(4π) ∮ I dℓ × (r − r') / |r − r'|³`.

As bobinas principais usam as cinquenta espiras em suas posições reais. No eixo o programa usa a expressão analítica `Bz/I = µ0 R²/[2(R²+z²)^(3/2)]`. Fora do eixo usa 128 elementos tangenciais por espira. O campo de filamento é singular sobre o fio; pontos dentro do cobre ou do envelope equivalente do receptor são excluídos. Os campos muito próximos do fio exigem quadratura mais fina ou solver com seção real. A interface não deve apresentar esses pontos como previsões exatas.

A soma é feita em fasores vetoriais, preservando a fase de cada componente. O módulo RMS é `√(|Bx|²+|By|²+|Bz|²)`; ele não é o comprimento instantâneo de uma seta. Quando as componentes estão defasadas, a ponta do vetor descreve uma elipse. Com `q = Bx² + By² + Bz²` e `s = |Bx|²+|By|²+|Bz|²`, os semieixos de pico são `√(s+|q|)` e `√(s−|q|)`. Linhas de campo desenhadas a partir da fase zero representam um instante ou uma escolha de fase, não todas as fases ao mesmo tempo.

No enrolamento toroidal auxiliar cada espira tem posição:

`r'(θ,φk) = ((R+r cos θ) cos φk, (R+r cos θ) sin φk, z0−r sin θ)`.

`φk = 2πk/N`, com 64 elementos de fio por espira. Esse sentido gera campo principal +eφ. O programa integra essas espiras fechadas no espaço; não usa linhas decorativas como campo. A aproximação ideal de volume dá `Bφ ≈ µ0 N I/(2πρ)` e `L ≈ µ0 N²r²/(2R)`, apenas longe dos fios e com enrolamento suficientemente distribuído. Com 48 espiras e essa geometria há ondulação azimutal apreciável: a 0,15 A RMS, o campo no centro da seção é aproximadamente 13,85 µT sob uma espira e 7,94 µT entre espiras, enquanto a fórmula ideal dá 10,67 µT. A validação verifica o valor médio pela lei de Ampère, em vez de exigir campo uniforme fictício.

O toroide é excitado por corrente ideal independente. Sua tensão necessária e L são estimativas ideais, e sua perda de cobre aparece separadamente. O balanço das duas fontes principais e do receptor não inclui a terceira fonte toroidal. Nas geometrias ideais perfeitamente coaxiais, a mútua entre uma espira circular axial e uma espira poloidal é zero por simetria: o campo da espira axial está no plano meridional da espira poloidal, perpendicular à sua normal. Fios de ligação, assimetrias e montagem real podem produzir acoplamento parasita e não foram calculados. Nenhum receptor coaxial de campo axial pode ser presumido capaz de extrair energia de um campo toroidal confinado.

## Estabilização mensurável

`controle_cc.csv` mostra um ensaio separado de controle de corrente contínua: capacitores desviados, receptor desconectado e as duas bobinas alimentadas igualmente com orientação aditiva. A dinâmica de cada porta é `(L+M) dI/dt + R I = U`. O controle usa feedforward `R Ialvo`, PI e anti-windup por integração condicional. A saída U é limitada de 0 a 5 V. A corrente não é recortada. A simulação introduz mais 1 Ω em t = 0,2 s e continua até 0,4 s para mostrar recuperação. O passo é 1 µs, comparado com 0,5 µs. Esse ensaio CC não equivale a um controlador CA do circuito RLC e não constitui feedback quântico.

## Ordem gravitacional clássica

A densidade média de energia magnética é `uB = |B_RMS|²/(2µ0)`. O arquivo calcula a escala dimensional `(8πG/c⁴)uB` como ordem local de componentes do tensor de Einstein associados à energia magnética clássica. Isso não resolve uma métrica, não prevê wormhole e não é o escalar de Ricci. O tensor de energia-momento eletromagnético tem traço zero: em eletrovácuo e com Λ = 0, o escalar R é zero. Energia elétrica, material, suportes e tensões mecânicas não estão nessa estimativa local.

## Reproduzir e validar

Na pasta `simulacao`:

```powershell
py modelo_integral.py --output outputs
py validar.py
py validar.py --browser
```

O cálculo e os testes físicos básicos usam apenas a biblioteca padrão de Python 3. O teste `--browser` exige Playwright Python e Chrome instalado em `C:\Program Files\Google\Chrome\Application\chrome.exe`; ele executa o motor JavaScript offline em Chrome real. Cada configuração deve ser preservada junto com as medições futuras. Os arquivos CSV resultantes são **previsões**, não medições.

`baseline.json` reúne configuração, indutâncias, resistências, correntes, fases, energia e potência. `testvectors.json` traz cinco casos de fase/orientação/receptor. `campo_eixo.csv` e `campo_plano_xz.csv` usam metros e tesla RMS. `field_basis.json` guarda vetores de campo por ampere para a geometria inicial, permitindo recombinar correntes de forma rápida. `varredura_frequencia.csv` cobre 100 a 6.000 Hz. `controle_cc.csv` é o ensaio CC separado. `validacao_modelo.json` lista as verificações e seu alcance. Não substitua as medições futuras por esses arquivos calculados.

## API do visualizador offline

O arquivo `modelo_browser.js` expõe `window.NucleoPhysics`, sem rede. A geometria é fixa e idêntica ao CAD. O objeto incorporado contém a referência `baseline` e a `config`. `solve(input)` aceita:

```javascript
{ frequency_hz:1400, voltage_lower:2, voltage_upper:2,
  phase_upper_deg:0, orientation_upper:1, receiver_enabled:true,
  load_ohm:100, temperature_c:20, toroid_enabled:false,
  toroid_current_rms_a:0.15, toroid_phase_deg:0 }
```

Ele retorna `currents`, `physical_currents`, `capacitor_voltages`, `power`, `energy`, `validity` e `parameters`. Cada fasor possui `{re, im, rms, phase_deg}`. `fieldAt([x,y,z], input, optionalSolveResult)` retorna vetores `real`, `imag`, módulo `rms_norm_t`, componentes `components_t` e semieixos da elipse. `torusFieldAt(point,input)` retorna somente a contribuição toroidal. Entradas de ponto sobre o cobre lançam `FIELD_IN_WIRE_EXCLUDED` ou `FIELD_IN_RECEIVER_ENVELOPE_EXCLUDED`; a interface deve ocultar o ponto e explicar a exclusão. `clearCache()` limpa os caches de vetores unitários.

O JSON de referência é incorporado ao início do motor JavaScript. Ao executar `modelo_integral.py`, o programa regenera os resultados e sincroniza automaticamente esse objeto incorporado; os testes de paridade detectam diferença entre os motores. Alterações de raio, número de espiras ou posição exigem regenerar o modelo/CAD e não são parâmetros da interface atual.
