# Eletrônica de bancada V3

O pacote define os componentes, ligações, medições e cálculos para montar uma bancada eletromagnética clássica. **A montagem física, calibração, estabilidade, dissipação e proteção ainda precisam ser ensaiadas.** A geometria e o modelo V2 foram preservados; a imagem conceitual não é evidência de funções quânticas.

Arquivos: [esquema SVG](esquema.svg), [BOM](BOM.csv), [ligações](LIGACOES.md), [qualificação](QUALIFICACAO.md), [sensores](SENSOR_CAMPO.md), [fontes oficiais](FONTES.md), [cálculos](calculos.py), [relatório JSON](relatorio_dimensionamento.json) e [envelope CSV](envelope_operacao.csv).

## Componentes selecionados

- **RIGOL DG1022Z:** duas saídas senoidais sincronizadas, 100–5000 Hz, indicação de carga High Z e offset de 0 V. A amplitude válida é a medida nos bornes de saída dos amplificadores.
- **Dois TI OPA548EVM:** configuração não inversora padrão. O divisor R5/R7 atenua por 2 e a realimentação RF1/R2 amplifica por 2; o ganho total é aproximadamente 1. Preservar R2, R5, R7 e RF1 de 10 kΩ. Trocar apenas Rcl/R8 por 82 kΩ, 1%. O limite nominal é 0,744 A de pico; exigir qualificação entre 0,72 e 1,00 A de pico, nos dois sentidos, frio e quente. A tolerância publicada para 2,5 A não garante precisão nesse novo ponto.
- **R&S HMP2030:** CH1 e CH2 isolados, cada um em 12,00 V e limite de 4,8 A; ponto médio em SGND. Rails medidos dentro de 11,88–12,12 V. O instrumento oferece 80 W por canal e 188 W no total. CH3 fica em 5 V para os sensores, ou em 3,3 V para o toróide auxiliar em outro ensaio.
- **Ramos AC:** saída OPA → capacitor TDK B32754C2106K000 de 10 µF, ±10%, filme MKP → bobina de 50 espiras → resistor não indutivo Vishay NH02510R00FE02 de 10 Ω, 1%, 25 W → SGND. O resistor de 10 Ω também é o shunt Kelvin. Sua impedância e fase precisam de calibração; não adicionar outro shunt à série sem alterar o modelo.
- **Receptor:** 20 espiras, raio médio de 35 mm e carga de 100 Ω, 0,1%, 0,25 W. Uma extremidade vai a SGND para referenciar a aquisição.
- **PicoScope 4824A:** A=fonte1, B=shunt1, C=fonte2, D=shunt2, E=carga. Canais F/G opcionais registram saída/referência do DRV425EVM; H registra LM35DZ. Todos os BNC têm terra comum em SGND. Amostragem pretendida de 1 MS/s por canal, confirmada pelo SDK. A resolução física é de 12 bits.

## Envelope de operação

Primeiro ponto: **2,00 Vrms por fonte, 1400 Hz, fase relativa de 0°, toróide desligado**. A previsão V2 é de aproximadamente 0,18545 Arms em cada ramo e 24,05 µW na carga receptora.

O comando pode chegar a 5 Vrms, mas esse valor é **condicional à corrente real ≤0,50 Arms**. A varredura com L±15%, C±10%, R±1% e cobre entre 20–60 °C encontrou limite conservador de 0,51902 Arms em certas combinações. Usar **4,70 Vrms como teto recomendado para explorar todas as fases nessa varredura** reduz o limite a 0,48788 Arms. A grade de 25 Hz não prova o comportamento em todo o contínuo; cada ponto deve ser qualificado por medição sem recorte ou oscilações.

Parar se a corrente exceder 0,50 Arms ou 0,7071 A de pico senoidal, capacitor exceder 30 V de pico, bobina/suporte chegar a **45 °C**, dissipador OPA passar de 60 °C, resistor/chassi passar de 70 °C, rail sair de ±1% ou qualquer proteção atuar. O limite interno de pico é proteção contra falha, não controle RMS.

## Retorno de energia e dissipação

Cada rail recebe uma sangria **RH1004R700FE01, 4,7 Ω, 1%, 100 W**, entre o rail e SGND. A corrente mínima é de 2,5026 A, superior ao retorno combinado de dois drivers qualificados em até 1,00 A de pico cada. A corrente máxima conservadora debitada por rail é de 4,685 A, incluindo 80 mA auxiliares; permanece abaixo do ajuste de 4,8 A. Cada sangria pode dissipar 31,57 W: montar em dissipador separado de até 0,8 °C/W, com barreira contra toque e respeitando a curva de redução de potência do fabricante. A fonte não é presumida capaz de absorver corrente.

O estágio AB do OPA normalmente dissipa a energia reativa. Os diodos de saída para os rails e as sangrias precisam estar corretamente montados; não operar sem sangria. Para cada OPA, o limite térmico conservador calculado é de aproximadamente 8,44 W, incluindo potência real negativa na porta. Com ambiente de até 30 °C, interface de até 0,5 °C/W, dissipador de até 3 °C/W e resistência junção–case conservadora de 2,5 °C/W, a estimativa de junção fica abaixo de 81 °C. O dissipador original do EVM precisa ser medido e, se necessário, ampliado. A tab pode estar em V−: isolar de chassis e terra. A proteção térmica interna não serve de regulador.

## Modos e parada

Comutador manual RUN/STOP com dois contatos isolados: em STOP, fechar E/S de cada OPA para o seu próprio V−. Não ligar E/S a GPIO, SGND ou 3,3 V. Depois desabilitar ambas as saídas da fonte. Esse comutador não é uma parada de emergência certificada com falha segura. Para uma E-stop industrial, o circuito de relé, rearme e falhas precisa de projeto próprio.

**AC:** dois ramos RLC e receptor, gerador sincronizado; ADC/DAC do PI desconectados fisicamente.

**DC2 para mapa FEM:** ambos os capacitores contornados, receptor aberto, dois OPA com corrente de 0,15 ADC cada. Dois potenciômetros Bourns 3590S-2-103L de 10 kΩ recebem 3,3 V do Pico e controlam as entradas; ajustar pela corrente medida. Toróide desligado. É diferente do ensaio PI de uma bobina.

**PI DC:** uma bobina, capacitor contornado, segundo OPA e receptor desconectados. Pico + MCP4725 fornecem comando analógico; ADC lê o shunt por divisor de 0,5. Alvo de 0,15 A, teto de 0,20 A, comando de até 2,5 V e botão hold-to-run. A malha não regula AC. Firmware e montagem precisam de calibração e ensaio próprios.

**Toróide auxiliar DC:** fonte separada em 3,3 V, limite de 0,20 A, resistor de 22 Ω/5 W e diodo de recirculação; corrente nominal de até 0,15 A. A potência desse ramo entra no balanço global. AC auxiliar simultâneo requer um terceiro driver. Em ensaio separado, OPA2 pode ser requalificado para o toróide após desconectar as duas bobinas axiais; isso não reproduz três excitações simultâneas.

Toda troca de modo exige fonte desligada, STOP ativo, capacitores descarregados e conferência dos cabos. As ligações exclusivas de cada modo estão em LIGACOES.md.

## Reproduzir o dimensionamento

```powershell
py -B bancada_v3/eletronica/calculos.py
```

Usa apenas a biblioteca padrão e os parâmetros V2. Resolve a matriz de admitância, calcula limites para qualquer fase em 12805 combinações de frequência/tolerância/temperatura e verifica balanço de energia, corrente, headroom, slew rate, rails, sangrias e temperatura estimada. **Os 12 critérios analíticos passaram; isso não certifica o hardware.** Nenhum componente foi comprado ou montado por esta execução.
