# Próximos passos: da simulação à bancada

O projeto possui uma simulação clássica reproduzível e arquivos de construção propostos. Não há protótipo físico medido. O objetivo da próxima etapa é comparar previsões com observações, registrar divergências e corrigir o modelo quando necessário.

## 1. Manter o laboratório acessível e verificável

- Usar o [laboratório online](https://7dsol3.github.io/nucleo-campo-toroidal-quantico/) ou extrair o pacote ZIP para uso offline.
- Fazer mudanças em uma branch, abrir uma pull request e conferir os resultados de integridade, modelo e navegador no GitHub Actions.
- Conferir a publicação em Pages após mudanças na `main`. A publicação automática testa o site antes de disponibilizá-lo.
- Identificar o commit e a configuração usados em cada comparação. Os testes digitais não substituem a medição.

## 2. Fechar a eletrônica e a instrumentação

O circuito funcional da simulação não é um projeto completo de PCB/driver. Antes de comprar ou montar, selecionar e documentar fontes, estágios de saída, limites de corrente, resistores, capacitores e instrumentos compatíveis com o [circuito V2](nucleo_integral_v2/circuito_integral.svg).

As duas portas principais precisam de sinais sincronizados e fase conhecida. Alguns cenários calculados transferem potência de uma fonte para a outra; verificar a capacidade real de cada estágio para esse comportamento. O ensaio PI em corrente contínua é separado do circuito ressonante em corrente alternada.

Critério para avançar: esquema revisado com valores, tolerâncias, conexões de medição e limites de operação explícitos. Não assumir que duas saídas de um gerador comum realizam automaticamente o comportamento das fontes ideais.

## 3. Fabricar e caracterizar um subconjunto

Começar por uma bobina e seu suporte, seguindo as [instruções CAD](nucleo_integral_v2/cad/LEIA-ME_CAD.md). Medir dimensões reais, número de espiras, resistência, indutância e capacitância. Depois caracterizar a segunda bobina, o receptor e o acoplamento entre conjuntos.

Registrar instrumentos, calibração, temperatura, frequência de medição, tolerâncias e incertezas. Confrontar os valores obtidos com `simulacao/configuracao.json`. Mudanças de geometria exigem atualizar tanto o modelo quanto o CAD e regenerar os arquivos correspondentes.

Critério para avançar: montagem e parâmetros medidos documentados; conexões e limites de componentes conferidos. A coluna aberta ao ar não é uma câmara de vácuo.

## 4. Executar os ensaios e comparar

Seguir o [protocolo P01–P10](nucleo_integral_v2/pesquisa/PROTOCOLO_COMPLETO.md): começar pelo ramo único, depois par sincronizado e receptor, variando frequência, fase e carga. Manter a mesma configuração ao comparar simulação e medida.

Medir tensão e corrente com a fase correspondente para obter potência com sinal correto; registrar o balanço de energia, aquecimento e condições de controle. Guardar os dados brutos e sua incerteza, além dos resultados processados. Usar o [modelo CSV vazio](nucleo_integral_v2/Modelo_Medicoes.csv) para importar os dados no laboratório; o CSV não comporta sozinho todos os metadados do ensaio.

Critério para aceitar uma previsão: concordância dentro da incerteza e da faixa de validade declarada, em ensaios repetidos. Se houver divergência, investigar instrumentos, parâmetros, perdas e aproximações antes de atribuir um efeito novo.

## 5. Investigar as hipóteses da imagem separadamente

Energia do vácuo, feedback quântico, propulsão sem reação e manipulação do espaço-tempo não possuem implementação validada neste projeto. Para testar cada hipótese, ainda é necessário formular equações completas com unidades e parâmetros, definir condições iniciais/de contorno, prever um observável e estabelecer controles que distingam o efeito proposto do eletromagnetismo convencional.

Consultar a [auditoria científica](auditoria_cientifica.md) e o [inventário de lacunas](nucleo_integral_v2/pesquisa/INVENTARIO_LACUNAS.md). Aparência semelhante à imagem, renderização 3D e testes aprovados não demonstram essas hipóteses.
