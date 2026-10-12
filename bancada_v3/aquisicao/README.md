# Aquisição real com PicoScope 4824/4824A

`capturar_pico.py` usa a biblioteca oficial `ps4000a` por ctypes para abrir, identificar, configurar entradas e capturar um bloco simultâneo. Não gera sinais de exemplo, não liga fontes e não comanda saídas do instrumento. Sem driver/dispositivo, termina com `captured=false` e não cria dados de campanha.

Instalar o [PicoSDK oficial](https://www.picotech.com/downloads) compatível com a arquitetura do Python. As assinaturas e enumerações foram conferidas no [guia ps4000a](https://www.picotech.com/helpfiles/4000a-api/index.html) e no [wrapper oficial](https://github.com/picotech/picosdk-python-wrappers/blob/master/picosdk/ps4000a.py). Não é preciso instalar o wrapper Python para usar este adaptador.

## Entradas e filtro

Todas as pontas são **1:1** e todos os retornos BNC vão a SGND em estrela, conforme o esquema V3. Os canais não são diferenciais. Medem o topo dos resistores de retorno e as saídas das fontes, nunca um nó flutuante. Ligar a ponta de terra a outro nó altera ou curto-circuita a montagem.

| Canal | Grandeza | Faixa configurada |
|---|---|---|
| A | Fonte 1, antes do capacitor | ±10 V |
| B | Shunt/resistor série 1 | ±10 V |
| C | Fonte 2, antes do capacitor | ±10 V |
| D | Shunt/resistor série 2 | ±10 V |
| E | Tensão da carga receptora | ±0,2 V |
| F opcional | VOUT do DRV425EVM | ±5 V |
| G opcional | VREF do DRV425EVM | ±5 V |
| H opcional | VOUT do LM35 | ±1 V |

Inserir os filtros e documentar sua resposta conforme [FILTRO_ANTIALIAS.md](FILTRO_ANTIALIAS.md). A banda de 20 MHz do osciloscópio sozinha não evita aliasing a 1 MS/s. Filtragem, sensor, cabos, shunts e instrumentos fazem parte da calibração composta.

O software solicita 1 MS/s por canal e 0,1 s por padrão. Obtém intervalo e capacidade reais com `GetTimebase2`, escala com `MaximumValue`, usa os mesmos índices dos canais e recusa overflow, códigos no limite ADC, bloco incompleto ou timeout. O relógio comum não certifica por si só skew e fase da cadeia completa. A duração nominal corresponde a 140 ciclos a 1.400 Hz.

## Comandos

```powershell
py -B bancada_v3/aquisicao/capturar_pico.py --diagnostico
py -B bancada_v3/aquisicao/capturar_pico.py --output C:/campanha_nucleo/ensaio_001
```

Para oito canais com campo e temperatura, informar as sensibilidades explicitamente:

```powershell
py -B bancada_v3/aquisicao/capturar_pico.py --sensores --field-sensitivity 4880 --temperature-sensitivity 0.01 --output C:/campanha_nucleo/ensaio_002
```

**4880 V/T e 0,01 V/°C são valores nominais**, não certificados. Substituí-los e corrigir ganho/offset/fase conforme a caracterização da cadeia construída. A conversão usa `B=(VOUT−VREF)/sensibilidade` e `T=VH/sensibilidade`; o resultado não deve ser interpretado como calibrado somente porque tem unidade física. Fundo/orientação do campo e contato térmico precisam de registro próprio.

Cada pasta nova recebe `formas_onda.csv` (vírgulas), `captura.json` com origem, serial, relógio e SHA-256. Com sensores, recebe também `canais_sensores_brutos.csv` para preservar F/G/H. O programa não sobrescreve pastas existentes. Os volts brutos são escalados pela faixa e máximo ADC reportado, antes das correções de calibração.

O registro de captura não substitui `medicoes/metadados_pendente.json`. Copiar e preencher esse template com configuração construída, valores medidos, certificados, controles e incerteza antes de executar `medicoes/analisar.py`. A saída `captured=true` confirma uma chamada de aquisição concluída; não confirma conexões, calibração ou funcionamento físico do núcleo. O hardware não foi testado nesta entrega.

```powershell
py -B bancada_v3/medicoes/analisar.py C:/campanha_nucleo/ensaio_002/formas_onda.csv C:/campanha_nucleo/metadados_002.json --config nucleo_integral_v2/simulacao/configuracao.json --output C:/campanha_nucleo/analise_002.json --summary-csv C:/campanha_nucleo/resumo_002.csv
```

O analisador CA exige janela coerente e metadados. Para o caso FEM CC, capturar primeiro as bobinas desligadas e depois energizadas, com o sensor na mesma posição e orientação. **Manter a bobina receptora aberta e desconectar a entrada do filtro E do receptor; ligar somente essa entrada do filtro E a SGND.** O adaptador mantém A–E habilitados: deixar E flutuante pode saturar o filtro e invalidar toda a captura. Aterrar essa entrada de medição não significa curto-circuitar a bobina receptora. Preencher `medicoes/metadados_cc_pendente.json` com a geometria construída, calibração, controles e limites de erro. A análise CC usa as médias das correntes medidas e subtrai o campo de fundo:

```powershell
py -B bancada_v3/medicoes/analisar_cc.py C:/campanha_nucleo/cc_ligado/formas_onda.csv C:/campanha_nucleo/cc_fundo/formas_onda.csv C:/campanha_nucleo/metadados_cc.json --output C:/campanha_nucleo/analise_cc.json
```

Os campos `model_config_path` e `fem_results_path` dos metadados apontam para os arquivos da configuração V2 e dos resultados FEM; caminhos relativos são resolvidos a partir da pasta do JSON de metadados. Ajustá-los ao copiar o template para a campanha. Conferir as opções e o significado do resultado no [procedimento CC](../medicoes/README.md). O FEM central só é escalado quando geometria, correntes e conexões são compatíveis com o caso calculado. Não comparar os 0,15 A CC do FEM com os 2 V RMS CA da referência V2.

No relatório CC, `temperature_mean_c` é a média da coluna exportada; esse analisador não corrige nem valida automaticamente o sensor de temperatura. Corrigir sua conversão a montante e preservar o canal H bruto e a documentação de calibração. A média nominal não libera um ensaio térmico.
