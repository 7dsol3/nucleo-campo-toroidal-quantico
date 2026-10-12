# Da entrega digital V3 ao ensaio físico

A [bancada V3](bancada_v3/README.md) já inclui equipamentos de referência, circuito com componentes e ligações, estudo de tolerâncias, FEM 3D executado, captura PicoScope, análise CA/CC e controle PI. A montagem física, a calibração e a coleta experimental **não foram realizadas**. O [manual consolidado](bancada_v3/Manual_Bancada_V3.pdf) reúne os procedimentos e os limites.

## 1. Construir e caracterizar a montagem

Usar as [peças e medidas CAD V2](nucleo_integral_v2/cad/LEIA-ME_CAD.md), a [BOM elétrica V3](bancada_v3/eletronica/BOM.csv), as [ligações](bancada_v3/eletronica/LIGACOES.md) e a [BOM do filtro](bancada_v3/aquisicao/filtro_componentes.csv). Os equipamentos comerciais de referência já estão selecionados; alternativas precisam satisfazer os mesmos requisitos verificados.

Começar por uma bobina e seu suporte. Medir geometria, número de espiras, resistência, indutância e temperatura. Caracterizar a segunda bobina, o receptor e as indutâncias mútuas antes do ensaio conjunto. Registrar valores, instrumentos, calibração e incertezas. Atualizar o modelo e o CAD quando a geometria construída diferir da proposta.

A coluna central aberta ao ar não é uma câmara de vácuo. Os desenhos mecânicos representam uma proposta de fabricação; a adequação dos materiais e a montagem precisam de inspeção física.

## 2. Qualificar eletrônica, sensores e aquisição

Executar a [qualificação elétrica e térmica](bancada_v3/eletronica/QUALIFICACAO.md), inicialmente com cargas de referência. Conferir o limite de corrente real de cada OPA548EVM, ganho, offset, distorção, retorno de energia e temperaturas. A STOP física atua nos amplificadores independentemente do programa; não é um sistema de parada certificado.

Construir e medir a resposta do [filtro de aquisição](bancada_v3/aquisicao/FILTRO_ANTIALIAS.md), calibrar shunts, sensor de campo e temperatura. Registrar ganho, offset, fase, skew e faixa útil da cadeia completa. A faixa recomendada de 4,70 V RMS vem de uma grade de cálculo; liberar cada ponto de operação a partir das verificações reais.

Instalar o PicoSDK e usar o [adaptador de captura](bancada_v3/aquisicao/README.md). Neste ambiente o driver não foi encontrado e não houve captura. Arquivar CSV brutos, registro de aquisição, configurações e certificados em uma pasta de campanha separada. Os templates publicados continuam vazios.

## 3. Comparar os mesmos ensaios

| Ensaio | Configuração | Comparação preparada |
|---|---|---|
| CA principal | Duas fontes sincronizadas, capacitores em série, receptor carregado; começar em 2 V RMS, 1.400 Hz, fase 0° | [Análise CA](bancada_v3/medicoes/analisar.py): RMS, fase, harmônicos e potência assinada contra o circuito V2 |
| CC / FEM | Duas correntes medidas próximas de 0,150 A, capacitores contornados, receptor aberto e toroide desligado | [Análise CC](bancada_v3/medicoes/analisar_cc.py): corrente e campo com fundo subtraído contra Biot–Savart; FEM central somente quando as condições coincidirem |
| PI CC | Uma bobina, segunda fonte e receptor desconectados | [Firmware](bancada_v3/controle/README.md): calibrar ADC/DAC, conferir zero, resposta transitória e parada física antes de habilitar o controle |
| Toroide auxiliar | Alimentação CC própria, corrente limitada e contabilizada separadamente | Caracterização convencional do enrolamento; excitação CA simultânea exigiria um terceiro driver qualificado |

Reconfigurar somente desenergizado. Não comparar a corrente CC do caso FEM com a referência CA de 2 V RMS. O PI de uma bobina também é um ensaio diferente do FEM das duas bobinas.

Repetir os ensaios com controles de fundo, polaridade invertida e instrumentos independentes. Aceitar concordância somente dentro da incerteza e da faixa de validade declaradas. Se houver divergência, investigar conexões, instrumentos, parâmetros, perdas e aproximações antes de propor um efeito novo. Os analisadores devolvem resultado inconclusivo quando faltam os requisitos de evidência.

## 4. Manter a publicação reproduzível

O [laboratório online](https://7dsol3.github.io/nucleo-campo-toroidal-quantico/) e os pacotes ZIP permitem consultar o projeto. O GitHub Actions verifica integridade, modelos, ferramentas V3 e o navegador antes de publicar o site. Identificar commit, configuração construída e arquivos brutos em cada campanha; testes digitais não substituem medições.

## 5. Investigar as hipóteses da imagem

Energia do vácuo, feedback quântico, propulsão sem reação e manipulação do espaço-tempo não possuem implementação demonstrada neste projeto. Cada hipótese ainda precisa de equações completas com unidades, parâmetros e condições de contorno, um observável previsto e controles que distingam o efeito proposto do eletromagnetismo convencional.

Consultar a [auditoria científica](auditoria_cientifica.md) e o [inventário de lacunas](nucleo_integral_v2/pesquisa/INVENTARIO_LACUNAS.md). Renderização 3D, correspondência visual e aprovação de testes de software não demonstram essas hipóteses.
