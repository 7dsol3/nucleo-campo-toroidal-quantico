# Ligações e pinagem

## Redes da bancada AC

| Rede | Ligações |
|---|---|
| P12 | HMPCH1positivo; AVDD dos doisEVM; topoRB+4.7Ω |
| SGND | HMPCH1negativo=CH2positivo; GND dos EVM; retornoR1/R2; negativosBNCgerador e todos DAQ; baseRB+ e topoRB−; referênciareceptor |
| N12 | HMPCH2negativo; AVSS dos doisEVM; baseRB−4.7Ω |
| VIN1/2 | DGCH1/2 centroBNC→entrada não inversora correspondenteEVM; cabo≤0.5m |
| OUT1/2 | Saída potênciaEVM→C1/2; senseKelvinA/C no próprio borneOUT |
| CAP1/2 | Outro terminalC1/2→início pontuado bobinaL1/2 |
| SH1/2 | Fim bobinaL1/2→topoR1/2; senseKelvinB/D neste ponto |
| RX | Início pontuadoreceptor→topocarga100Ω→E; fimreceptor/basecarga→SGND |

R1/R2 retornam individualmente ao pontoestrelaSGND; os cabosBNC não conduzem corrente da bobina. Usarpares trançados naida/retorno, fio≥0.75mm² no circuitoAC e≥1.5mm² nosrails/sangrias, bornes protegidos≥10A/30VDC, conexão firme. Comprimento de potência até0.5m; semprototipagem em breadboard para osrails/OPA/resistores. Não usarPE como retorno deliberado; verificar a relaçãoSGND–PE dos instrumentos e manter um único ponto de ligação deliberada.

OsBNC do Pico têm referência comum; não colocar garra de terra no capacitor, topo de bobina, P12 ouN12. Medir tensão de capacitor subtraindo canais referenciados aSGND ou com sonda diferencial adequada, não movendo a terraBNC.

## OPA548EVM

O chipOPA548 tem1=IN+,2=IN−,3=ILIM,4=V−,5=V+,6=OUT,7=E/S. EVM não é adaptador pino-a-pino; usar bornes/testpoints e os esquemasSBOU132.

- JP6 na seleçãoAVSS para alimentação bipolar; JP5GND.
- Configuração não inversora: JP1 ladoGND, JP2 caminhoVIN+, JP3/JP4 fora; conferir continuidade no esquema/revisão da placa. JP7 aberto habilita; fechado desabilita.
- PreservarR2=R5=R7=RF1=10kΩ eRiso/Rhcp=0Ω; manterRL/RF+ não instalados. R5/R7 atenuam1/2, RF1/R2 amplificam2. RemoverR7 duplicaria o ganho total: **não removerR7**.
- TrocarR8/Rcl14.7kΩ original por82kΩ1%0.25W. Nunca usarRcloriginal2.5A nessa bancada.
- Entrada não inversora: conector de sinal identificadoVIN+ (J5 na seção3.2/figura4); a tabela4 mencionaJ6. Por essa inconsistência de identificação no manual, **confirmar continuidade do conectorVIN+ viaR5 para chipIN+ antes de conectar**, sem assumir número deconector.
- Saída: usar borne de potênciaOUT e GND; BNCOUT é monitor. Confirmar borneOUT→chip6 porRiso/Rhcp.
- ContatosSTOP1/2 fechamE/S (TP correspondente)→AVSS/V− da sua placa. Contatos separados entre as placas, semGPIO. Não unirE/S aSGND.

## PI DC: Pico + MCP4725

Usar **RaspberryPiPicoRP2040** e móduloMCP4725 de referência **Adafruit4725/935** alimentado3.3V (confirmar que os pull-ups I²C também vão a3.3V). O DAC precisa inicializar em0V, memóriaEEPROM pré-configurada0 e botão físicoSTOP fechado até firmware pronto. Não alimentar a entradaOPA por PWM bruto.

| Pico | Destino |
|---|---|
| pino 36,3V3OUT | VDDMCP4725, pull-upsSDA/SCL4.7kΩse inexistentes |
| pino 38GND | GND MCP4725→SGNDestrela |
| GP4,pino 6 | SDAMCP4725,I2C0 |
| GP5,pino 7 | SCLMCP4725,I2C0 |
| GP26/ADC0,pino 31 | NóADC protegido, exclusivamente DC |
| AGND,pino 33 | ReferênciaADC→SGND pelo cabeamento de medição |
| GP15,pino 20 | Botãohold-to-run paraGND; pull-up firmware; semcontroleE/S |

MCP4725A0 emGND resulta0x60 na varianteAdafruit usual; confirmar comscannerI²C, pois outras variantes têmendereços diferentes. DAC OUT→resistor 100Ω→entradaVIN+ OPA1. Capacitor100nF juntoVDD DAC. A impedância de20kΩ nominal deentradaEVM, somada100Ω, resulta ganho≈0.9950; **calibrar o ganho realDAC→OUT e usar nofirmware**. CargaDACmínima20kΩ adequada à aplicação; saída máximaDAC2.5V não é garantia exataOUT2.5V.

SH1→RADCtop10kΩ→nóADC→RADCbottom10kΩ→SGND. NóADC→10nF→AGND eGP26. DiodoSchottkyBAS70 duplo/clamps discretos: anodo ADC/catodo3.3V eanodoSGND/catodo ADC. Razão0.5 nominal, tau≈50µs; firmwareI=2·Vadc/Rshunt, calibradooffset/ganho. Corrente DC normal0–0.2A gera0–1V no ADC. DivisorcarregaRshunt10Ω por20kΩ: efetivo9.995Ω; medir/corrigir. EmAC, desconectar fisicamente o ramoADC eDAC; tensõesnegativas não sãoentradaadmissível do Pico. Não energizar DC comPico/desligado; clamps não são isolação de entrada nem circuito de segurança.

DC: bypassC1 comjumper removível identificadoDC; desconectarDG, segundo OPA eRX; VIN+ somenteDAC. DesfazerDCcomPSUdesligada para voltarAC. A montagem por chicotes exclusivos elimina a necessidade de comutador multipolar de especificação incerta. Se usar seletorAC/OFF/DC, deve serbreak-before-make com posiçãoOFF e intertravamento mecânico que desconecteADC emAC eDAC/gerador alternadamente; verificar todososcontatos antes dehabilitar.

## DC com duas bobinas para comparar o mapa FEM

É um modo distinto do PI de uma bobina. Com fonte desligada/STOP, retirar DG, DAC/ADC e receptor (circuito aberto), bypassar ambos C1/C2 e manter OPA1/2 ativos. A saída **3V3 OUT do Pico, pino 36**, alimenta dois potenciômetros multivoltas **Bourns3590S-2-103L**,10kΩ: terminal 1 aSGND,3 a3.3V,2wiper→100Ω→VIN+ OPA correspondente. Confirmar pinagem/movimento na ficha do componente; ajuste inicia no extremo0V. Adicionar100kΩ de cada wiper paraSGND reduz flutuação se contato abrir, mas não éproteção contra todasfalhas. O Pico deve estar alimentado por USB; não ligar VSYS em paralelo ao USB como alimentação improvisada. Consumo dos dois potenciômetros é inferior a1mA.

Habilitar manualmente e subir lentamente até VSH1/R1=VSH2/R2=**0.150ADC**, no mesmo sentido axial. Saída OPA requerida≈0.15×Rtotal≈1.605V; wipers precisam ajuste pela medição, porque o EVM carrega o potenciômetro e o ganho varia com posição. Não ajustar apenas pela posição angular. Receptor/toróide OFF; aguardar transiente DC decair. Medir F/G do DRV425 e H do LM35 com **HMP CH3 em5.00V/0.10A**, referência SGND; DAC fica desconectado no modo DC2. CH3 somente pode alimentar o auxiliar toroidal3.3V em outro ensaio, sem sensores5V conectados.

Registrar duas correntesDCe temperatura em cada pontodocampo. Esse caso deexcitação correspondeao FEM estático comduasbobinas0.15Acada; oPIlegado/firmwarede umabobina não gera automaticamenteessemapa.

## Toróide auxiliarDC

HMPCH3 ajustado3.30V, limite0.20A, habilitado somente em ensaio separado: positivo→chaveTAUX→Raux22Ω5W→enrolamento48espiras→negativo. Diodo1N5819 em paralelo aoenrolamento (catodono ladoRaux, anodono retorno) oferece caminho de recirculação ao abrirchave. O circuito não usaGPIOcomofonte. Corrente máxima nominal3.3/22=0.150A, realmenorpor resistência docobre; potênciaRaux≤0.495W. Para0.150A exatos, medir ecompensar resistência sem ultrapassar0.20A. Esse ensaio deve contabilizarVaux·Iaux àentrada; emoperação simultânea isso soma àfronteiraenergética. ParaACnão usar essediodo emparalelo; terceirodriverAC não está implementado.

## Fronteiras de potência

No núcleoAC: Pentrada=mean(vOUT1·vSH1/R1)+mean(vOUT2·vSH2/R2). Pcarga=mean(vRX²/Rload). R1/R2 e perdasdecobre fazem parte dafronteira experimental. DoisvaloresRMSmultiplicados não calculam potênciareal semfase. Se uma portaabsorve potência, manterseusinalnegativo e somarambas; eficiência contra apenas umafonte cria resultadomistificado.

Na bancada inteira: somar potênciaDCdos railsPSU e auxiliar, incluir sangrias, drivers, gerador/DAQ/controle conforme fronteira declarada. Potênciacargamuito pequena (~24µW nominal) não cobre os≈62Wdasangria; a eficiência do núcleo modelado não é eficiência de tomada. MediçõesDCPSU lentas não substituem capturaACsimultânea dasportas. Desconectarenergia antes de alterar qualquer fio.
