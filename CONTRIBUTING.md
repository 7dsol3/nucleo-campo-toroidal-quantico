# Contribuir para o laboratório

As contribuições devem melhorar a reprodução dos cálculos, a consistência do CAD, o uso do laboratório ou a qualidade do protocolo experimental. Preserve a distinção entre hipótese, previsão numérica e medição física.

## Relatar um problema

Inclua o arquivo/versão afetado, os passos de reprodução, o comportamento observado e o comportamento esperado. Para resultados numéricos, anexe a configuração, as unidades, a saída relevante e a aproximação envolvida. Para CAD, indique peça, interface e cotas. Para o visualizador, informe sistema, navegador e mensagem de erro, quando houver.

## Propor uma alteração

1. Trabalhe em uma branch com propósito definido.
2. Explique qual problema a alteração resolve e como reproduzir o resultado.
3. Execute as verificações adequadas: testes numéricos para mudanças no solver, paridade Python/JavaScript para mudanças em ambos os motores, revisão geométrica para mudanças no CAD e testes de navegador para mudanças nas interações.
4. Atualize os documentos e os artefatos dependentes. O CAD e o solver não possuem sincronização automática de geometria; conferir essa consistência faz parte da alteração.
5. Registre no pull request os comandos, resultados e limites da validação realizada.

Não misture parâmetros da bancada V1 com os da montagem integral V2. Scripts de ajuste da produção original não são um fluxo de atualização idempotente; altere as fontes finais ou use os geradores documentados.

## Dados experimentais

Medições devem vir acompanhadas de configuração física real, instrumentos, calibração, data, unidades, fase, temperatura, fronteiras do balanço de potência e incerteza. Preserve os dados brutos e explique qualquer transformação. Arquivos sintéticos usados para testes precisam ser identificados como tal e não devem preencher o conjunto de medições reais.

Uma divergência com o modelo deve ser examinada primeiro quanto a geometria, tolerâncias, resposta dos sensores, acoplamento parasita, perdas, saturação e erros de medição. Uma alegação de fenômeno novo exige uma previsão quantitativa própria e controles capazes de distingui-la do eletromagnetismo convencional.

## Linguagem e atribuição

Não apresente uma verificação digital como comprovação de um aparelho físico, nem reclassifique as hipóteses extraordinárias como funcionalidades implementadas. Cite a origem das fórmulas e mantenha a atribuição dos materiais de referência. O nome artístico do projeto não transforma o solver clássico em um modelo quântico validado.

## Direitos dos materiais

Não acrescente uma licença ou redistribua material de terceiros sem autorização do titular. Qualquer mudança nos termos de uso dos arquivos deve ser aprovada pelo responsável pelo repositório. A publicação atual não concede uma licença de código aberto.
