# Medição de campo DC/AC

Selecionado **TexasInstrumentsDRV425EVM**, fluxgate deum eixo, semcompra ouensaio realizado. Fontes oficiais consultadas12-10-2026: [placa](https://www.ti.com/tool/DRV425EVM), [manualSLOU410B](https://www.ti.com/lit/ug/slou410b/slou410b.pdf), [datasheetSBOS729B](https://www.ti.com/lit/ds/symlink/drv425.pdf). O chip mede DC/AC; banda32/47kHz é especificada com Rshunt22Ω. **O valor exato da resposta em frequência com100ΩdaEVM precisa ser calibrado**, não deduzir precisão5kHz somente da banda47kHz do chip.

Alimentação regulada5.00V/limite0.10A: HMPCH3quandoaux/potenciômetros nãoousam, oufonteauxisolada5V100mAreferenciadaSGND. EVMJ1: **1=VREF,2=VOUT,3=GND,4=VDD**, validarcontinuidade com esquemafigura6 antes deenergizar. Há um erro de repetição depino 2 na seção3.3 do manual; o pino dereferência é1conforme esquema. Não cortar trilha do VREFinterno e não injetar tensão no pino 1naconfiguraçãopadrão.

Pico 4824A: **F=J1.2VOUT, G=J1.1VREF** contraSGND; terrasF/GemJ1.3. Faixa inicial±5V em ambos, acoplamentoDC, mesmaaquisição das fontesA–E; Pico suporta7canais, conferir taxareal retornadaSDK. O código de5canais precisa habilitarF/Gexplicitamente para medircampo; com apenas5canais conectados, essecampo nãoestá capturado. H pode monitorarflag porinterfaceadequada; /ER e /ORdevem estar normais e sãoactive-low com pull-ups5V, semGPIOPico3.3Vdireto.

ConfiguraçãopadrãoR1=100Ω, BSELalto, referênciaVDD/2. Sensibilidade nominalS=4·12.2·100=**4880V/T =4.88mV/µT**:

`B_T = (VOUT - VREF - offset_calibrado_V) / S_calibrada_V_por_T`

Sinais do eixo e polaridade precisamser registrados. Em73.4837µTrms a componente ACesperada é0.35860Vrms acima/abaixo dareferência; VREF≈2.5V. ±500µT é faixa aproximadadaEVMem5V, dependente deheadroom; EarthDC/camposlocais e offsettambémocupamfaixa. NãoalterarR1para aumentar sensibilidade semrefazerfaixa/calibração. Precisãoanunciada do sensor nãoé precisão da cadeiaPico+fiação+posição.

Eixo sensível é paralelo àface do chip, entre seuspinos2e14. ParaBz do núcleo, orientar **eixo sensível** aolongoz; colocarplaca “deitada” horizontal normalmente mede outra componente. Usarsuporte nãoferromagnético queposicione ocentrosensor, nãoabordaPCB, nascoordenadas de comparação. Cabosdealimentação devemtrançados e afastadosdo sensor; dissipadores,sangrias e potenciaiscorrentes retornantes ficamlongedaáreadocampo.

## Calibração e comparação quantitativa

1. Aquecer deacordocommanual, zero/baselinecombobinas desligadas mantendo posição. ParaAC, subtrairbaseline DC e estimara componenteàfrequênciadeexcitação; conservarcampo DCambiente como registro separado. Não zerar o campo ligado arbitrariamente.
2. Calibrar ganho/offsetDC com campo de referência independente. Uma bobinaHelmholtzdecalibraçãodedicada épossível: R50mm,N20porbobina, distânciaentrecentros50mm, corrente DC±0.1Amedida atravésdeshuntcalibrado. Fórmula centralideal `B=(4/5)^(3/2)*mu0*N*I/R`, resultando±35.97µT. Essa bobina de referência **não está fabricada neste pacote**; medirR,centros,seção eI e calcularincerteza ecorreçãogeométrica antes de chamá-lacalibrador. Não usar a própria previsãoV2como“campo certificado” para validarV2.
3. CalibrarrespostaACmódulo e fase100–5000Hz com a mesma bobinade referência e corrente ACmedida simultaneamente. CalcularBatravésda geometriareal e amplitude/fase dacorrente, independente datensãodecomando. Exigir ruído,resíduofit,clip eflagsnormais; salvar correçãocomplexaS(f) eincerteza em cada ponto. Condições fora da calibraçãoficam“inconclusivas”.
4. Na bancadaDC2, comL1=L2=0.15ADC eRXaberto, comparar `Bz_medida - Bz_baseline` comFEMestático eBiot–Savart nasmesmascoordenadas e correntes. NoAC, compararfasorBzmedido comprevisãoV2nasmesmasfases/correntes. Não compararRMSACaovalorDC doFEM.
5. Incluir erro de ganho/offset/fase dos dois canais F/G, tolerância/calibraçãoR1sensor, ruído,posição eorientação, e erro dacorrente de referência. O Pico especificaDC±1%fullscale±300µV; com±5Vsemcalibração erroabsoluto pode exceder10µT porcanal. Isso exige calibração diferencial para comparaçõespercentuaisestritas, não promessa de0.1% noresultadofinal.

## Temperatura: LM35DZ/NOPB no canal H

Selecionado **TI LM35DZ/NOPB, TO-92**, faixa0..100°C. [Datasheet oficial SNIS159H](https://www.ti.com/lit/ds/symlink/lm35.pdf), seção5, consultado12-10-2026: **pino 1=+VS, pino 2=VOUT, pino 3=GND**. A figura TO-92 é vista por baixo; identificar os pinos com o desenho do encapsulamento, sem inverter por comparação visual com TO-220.

Pino1→HMPCH3+5.00V, pino 3→SGND, pino 2→resistor 100Ω junto ao sensor→PicoH; shellH→SGND. Capacitor100nF entre pinos1/3 perto do sensor. CanalH inicialmente±1V, acoplamentoDC. Conversão nominal **temperatura°C=100·VOUT**, de0.2V em20°C a0.8V em80°C. Caso use condicionador/filtro, contabilizar ganho e offset. Não colocar capacitor grande diretamente em VOUT; o resistor isola carga capacitiva do cabo.

Fixar eletricamente isolado em contato térmico com a bobina selecionada, deixando a posição registrada. Calibrar com termômetro de referência em25,50e70°C e aguardar equilíbrio; o encapsulamento pode acompanhar parcialmente a temperatura do ar, então leitura nominal não representa automaticamente a temperatura interna do cobre. Uma unidade não monitora simultaneamente as duas bobinas, os dois amplificadores e as sangrias. Os demais pontos exigem termômetro de contato independente; não inferir temperatura de todas as peças pelo canalH.

O canal H é registro de temperatura; o computador e o LM35 não substituem parada física ou limitador térmico independente. Leituras fora da faixa/calibração, sensor desconectado ou temperatura de contato inadequada invalidam uma aprovação automática.

Uma sonda fluxgate mede indução magnética clássica; resultados não demonstram curvatura espacial, vácuo quântico ou energia excedente.
