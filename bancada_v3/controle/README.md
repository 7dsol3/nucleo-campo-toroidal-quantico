# Controle PI CC — firmware e ensaio separado

Firmware MicroPython para **Raspberry Pi Pico RP2040**, MCP4725 e uma bobina V2. A montagem usa o amplificador OPA548EVM e resistor de retorno 10 Ω documentados na eletrônica V3. O firmware foi escrito e seu controlador testado numericamente; **não foi instalado ou verificado num microcontrolador físico**.

| Conexão Pico | Destino |
|---|---|
| GP4, pino físico 6 | MCP4725 SDA, pull-up 4,7 kΩ a 3,3 V |
| GP5, pino físico 7 | MCP4725 SCL, pull-up 4,7 kΩ a 3,3 V |
| 3V3 OUT, pino 36 | MCP4725 VDD e pull-ups; não alimentar DAC em 5 V |
| GND, pino 38 | SGND no ponto estrela |
| GP26/ADC0, pino 31 | Divisor do shunt: 10 kΩ do topo do shunt até ADC, 10 kΩ ADC→SGND, 10 nF ADC→SGND |
| GP15, pino 20 | Botão momentâneo para SGND; segurar para habilitar comando de corrente |
| MCP4725 A0 | SGND, endereço 0x60 |
| MCP4725 VOUT | Entrada positiva do OPA548EVM no modo CC, ganho total calibrado aproximadamente 1 |

Usar a pinagem do módulo efetivamente comprado, desacoplamento e ligações conforme seu datasheet. Não conectar GP26 ao shunt no modo CA: o divisor não adapta tensões negativas para o ADC. A entrada E/S do OPA é referenciada a V− e **não se conecta diretamente ao Pico**.

Desenergizado: contornar capacitor, desconectar gerador, receptor e segundo amplificador; conectar o modo CC. Copiar `main.py` e `controlador.py` para a placa com MicroPython apropriado. Conferir as [ligações elétricas](../eletronica/LIGACOES.md), a parada física e a [qualificação](../eletronica/QUALIFICACAO.md) antes da operação.

O padrão `CALIBRATION_CONFIRMED=False` mantém comando zero. Antes de habilitar, substituir pelos valores medidos a referência ADC, relação do divisor, offset, resistência do shunt, resistência total, referência DAC e ganho do driver. Confirmar a faixa de conversão com correntes conhecidas. O alvo é 0,150 A, máximo configurável nesta versão 0,200 A; comando limitado a 2,5 V; falha latente quando corrente calculada excede 0,250 A, sensor inválido ou período ultrapassa 25 ms.

O PI usa feedforward R·Iref, Kp=2 V/A, Ki=20 V/(A·s), anti-windup por integração condicional. É diferente do ensaio contínuo idealizado e passo de 1 µs da V2. A espera nominal de 5 ms soma processamento, I²C e impressão: **200 Hz não é uma frequência garantida**. O código usa o dt observado; medir jitter, latência, ruído, degrau e aquecimento antes de aceitar desempenho.

Soltar o botão zera o comando e integrador; uma falha exige reinicialização deliberada, depois de corrigir sua causa. O watchdog reinicia o Pico em travamento, mas **o MCP4725 pode manter a última tensão enquanto o Pico reinicia ou perde comunicação**. O software não substitui a limitação de corrente física ou a chave RUN/STOP independente. A parada manual da V3 não é certificada como função industrial com falha segura.

O mapa FEM usa **duas bobinas CC**, cada uma com 0,150 A: operar esse caso com os dois comandos CC independentes documentados, não com este firmware de uma bobina. O firmware não controla o circuito CA, não mede coerência quântica e não liga automaticamente fontes externas.

Referências primárias: [pinagem Pico](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf), [MicroPython RP2](https://docs.micropython.org/en/latest/rp2/quickref.html), [MCP4725](https://www.microchip.com/en-us/product/mcp4725), [OPA548EVM](https://www.ti.com/tool/OPA548EVM).

```powershell
py -B -m unittest discover -s bancada_v3/controle -p "test_*.py"
```

Esses testes usam planta RL com atualização exata de retenção de ordem zero, verificam erro de resistência, saturação, desarme e prazos. Não exercitam ADC, DAC, I²C ou tempos de hardware.
