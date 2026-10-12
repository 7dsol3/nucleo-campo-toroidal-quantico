# Inventário das funções do pôster e dos próximos passos

Data: 12/10/2026. Escopo: versão integral V2 de bancada inspirada na imagem. A tabela distingue um modelo disponível de um teste físico concluído. **Não houve montagem física, aquisição experimental ou validação de aparelho nesta entrega.** Os dados numéricos da simulação são previsões do modelo descrito em PROTOCOLO_COMPLETO.md.

## 1. O que já pode virar uma previsão, e o que falta

| Função ou alegação | Estado de pesquisa | Definição mensurável disponível | Próximo item concreto |
|---|---|---|---|
| Estrutura 3D com medidas | calculavel | Dimensões, quantidade de peças e posição dos enrolamentos | Fabricar suportes, medir folgas e registrar materiais; revisão estrutural conforme processo real |
| Campos magnéticos superior/inferior | calculavel | B vetorial obtido das correntes e geometria | Enrolar, caracterizar R/L/M e mapear B com sensor calibrado |
| Geometria toroidal | calculavel | Toróide clássico N48, R135 mm, a8 mm; B azimutal e L aproximados | Fabricar enrolamento sobre a seção; medir campo interno, fuga, R e L; a aproximação ideal não resolve os fios reais |
| Superposição e interferência | calculavel | Soma complexa dos campos e correntes, com fase | Adquirir correntes reais e repetir 0°/90°/180°, fonte única e fontes OFF |
| Ressonância elétrica | calculavel | Matriz RLC acoplada e resposta I/V | Medir parâmetros versus frequência, fazer varredura e verificar limitação das fontes |
| Conversão em carga | calculavel | Potência numa resistência 100 Ω alimentada por indução | Medir v/i simultâneos de todas as entradas/saída e perdas, com controle resistivo |
| Estabilização mecânica e térmica | experimental | Posição, temperatura, resistência e deriva | Montar, instrumentar e executar ensaio térmico; modelo térmico quantitativo necessita materiais e convecção reais |
| PI de corrente RL DC | calculavel | Planta DC separada L dI/dt=V−RI com capacitores contornados e receptor desligado | Desenvolver hardware/sensor/amplificador e medir resposta; não foi entregue controle da amplitude AC |
| Feixe luminoso e anéis brilhantes | ilustrativo | Aparência de interface e decoração | Se usar LEDs, selecionar circuito convencional e separar/contabilizar sua energia; não chamar luz de plasma |
| Geração de vácuo controlado | hipotese_sem_modelo | Pressão de gás seria mensurável numa câmara apropriada, mas a coluna atual está aberta ao ar | Definir qual estado quântico se pretende preparar e seu observável; uma câmara de pressão separada não define esse estado |
| Núcleo de vácuo estável | hipotese_sem_modelo | Não foi definido estado, Hamiltoniano, barreiras, preparo ou duração | Escrever o modelo, condições de contorno, estabilidade e mecanismo de leitura |
| Ressonância quântica | hipotese_sem_modelo | Não foi definido sistema de níveis, transição ou frequência quântica prevista | Identificar graus de liberdade, Hamiltoniano, estado inicial, espectro e efeito esperado acima do ruído |
| Campo de informação | hipotese_sem_modelo | Bits/entropia não estão ligados a uma variável dinâmica ou sensor no pôster | Definir significado/unidade de I, equação, acoplamento, canal e experimento distinguível de comunicação EM convencional |
| Energia do vácuo como fonte contínua | hipotese_sem_modelo | Nenhuma previsão de energia extra ou mecanismo fornecido | Definir fonte, trabalho de preparação, ciclo, entrada/saída, mudança do estado e diferença esperada do balanço passivo |
| Curvatura controlada do espaço-tempo | hipotese_sem_modelo | Estimativa dimensional κu_B é disponível; não é solução de métrica | Definir tensor total, contornos, solução, observável gravitacional e amplitude que o instrumento distinguiria |
| Propulsão sem reação convencional | hipotese_sem_modelo | Força e fluxo total de momento poderiam ser medidos após previsão | Definir mecanismo/força prevista e incluir cabos, suporte, ar, radiação, campos externos e reação do ambiente |
| Estabilização de wormholes | hipotese_sem_modelo | Nenhum objeto físico, solução da métrica ou fonte foi especificado | Resolver geometria, fonte, condições de energia, estabilidade e mecanismo de produção; não há lista de peças dedutível |
| Controle de matéria | hipotese_sem_modelo | Sem amostra ou observável, a função não tem teste fechado | Escolher material, efeito (força, magnetização, transição etc.), magnitude, dose/tempo e controles |
| Comunicação por campos quânticos | hipotese_sem_modelo | Bobinas permitem transmissão EM convencional, sem prova de protocolo quântico | Definir estados e sua preparação/medição, protocolo, taxas/erros e comparação com transmissão clássica |
| Coerência por feedback quântico | hipotese_sem_modelo | PI DC ajusta corrente, não estado quântico | Especificar sistema quântico, medida de coerência, retroação, atraso e resultado que indique o efeito |
| Escalas 10⁻³⁵ m, 10⁻¹⁰ m, 1 m e km | ilustrativo | Visualização comparativa de ordens de grandeza | Definir variáveis/equações de cada regime e uma regra de passagem validada; ampliar CAD não amplia automaticamente o efeito |

O toróide auxiliar inicialmente OFF não é uma fonte oculta. Qualquer ensaio com ele ativo deve registrar sua excitação, corrente e potência e incluir seu acoplamento real se detectado. A bobina de captura descarrega energia das fontes em uma carga; sua eficiência é calculada com as entradas assinadas e as perdas, sem criar um mecanismo extra.

## 2. Dados que a imagem não fornece

Para fechar um projeto físico extraordinário, os nomes precisam ser substituídos por definições operacionais:

1. Variáveis, unidades e simetrias de ψ, Aμ, Bμ, Cμ e do suposto campo de informação.
2. Valores e unidades dos acoplamentos q, κ, χ, λ, ξ e uma expressão para V(ψ).
3. Ação ou equações de movimento consistentes, com tensor de energia-momento e fontes de carga/corrente.
4. Estado inicial e condições de contorno, geometria e materiais, ligação com um dispositivo de preparo e um sensor.
5. Previsão de pelo menos um observável em unidades de laboratório, incluindo tamanho, frequência, dependência de energia e efeito dos controles.
6. Balanço de energia/momento, limites clássicos, estabilidade do operador correto e aproximações usadas.
7. Ruído/precisão necessários e um desenho experimental capaz de distinguir a hipótese de Maxwell, calor, vibração, campos externos ou erro instrumental.

Sem esses itens, uma simulação de física adicional produziria números escolhidos pelo programador. É possível desenhar todas as formas da arte; não há base para atribuir um resultado físico aos blocos ainda indefinidos.

## 3. Auditoria específica das expressões visíveis

| Item visível | Interpretação técnica |
|---|---|
| 8πG/c⁴ | Fator correto em SI para T de energia-momento. O problema remanescente é definir o tensor total e resolver gμν com contornos |
| Métrica com t, r, θ, φ, ψ | Se as cinco coordenadas forem independentes, são cinco dimensões. Para chamar a métrica de 4D, definir ψ como auxiliar/dependente ou reformular a coordenatização |
| “Geometria toroidal em 4 dimensões” | Um toro geométrico e um campo toroidal clássico podem ser desenhados em 3D; a expressão não define sozinho uma solução dimensional extra |
| Fμν com Bμν e Cμν | As parcelas extras não têm lei dinâmica, unidades ou mecanismo de detecção definidos. Não trocar esses símbolos pelos nomes das bobinas |
| Matriz M com G, Q, I, C, Φ, K, Σ, L, Ω | Faltam dimensões dos blocos, unidades, operador, evolução e parâmetros. A matriz L/M elétrica usada na V2 é outro objeto, mensurável |
| det(M)>0 | Não implica estabilidade. diag(1,1) tem determinante positivo e crescimento em dx/dt=Mx |
| Re(λ)>0 “estabilidade” | Para matriz de evolução dx/dt=A x, decaimento linear exige Re(λ(A))<0; para matriz de energia positiva os sinais têm outro significado. Definir qual objeto é analisado |
| ∇μTμν=0 | Condição de conservação a demonstrar com as equações adequadas; escrever a identidade não prova que o tensor arbitrário obedece a ela |
| Escala de 10 m | É anotação artística sem tolerância/material/circuito. As cotas V2 de bancada são novas escolhas para permitir testes acessíveis |

O Atlas já distingue integridade algébrica de confirmação experimental nas páginas 3 e 22 e corrige a interpretação de arte como evidência na página 28. A afirmação documental de 37/37 testes originais não é uma execução desta entrega; seus arquivos originais não foram reexecutados aqui.

## 4. Por que manômetro, potência e mapa de campo não respondem a tudo

Um manômetro mede pressão residual; métodos quânticos de metrologia também podem medir pressão sem medir extração de energia do vácuo. O [NIST — padrão de pressão de vácuo](https://www.nist.gov/news-events/news/2022/07/primary-standard-measuring-vacuum) descreve esse observável. O [curso de QFT de Cambridge, seção 2.3](https://www.damtp.cam.ac.uk/user/tong/qft/qfthtml/S2.html) define o vácuo no sistema de estados dos campos. Usar a palavra “vácuo” nas duas descrições não identifica as duas operações.

Um receptor resistivo permite fechar um balanço clássico. A indutância mútua transfere energia e as fontes fornecem o trabalho; o [MIT — Inductance and Magnetic Energy](https://web.mit.edu/viz/guide/Chapter-11-Inductance%20and%20Magnetic%20Energy.pdf) apresenta as relações. Pico de corrente ou tensão maior que a entrada em uma reatância pode ocorrer por ressonância e não indica potência extra.

Um mapa B não fornece a métrica gravitacional. O tensor de Einstein responde ao tensor total de energia/momento/tensões com fator 8πG/c⁴; ver [MIT — relatividade geral, aula 12](https://web.mit.edu/sahughes/www/8.962/SP2020/lecture_guide.pdf). A contribuição EM clássica tem traço nulo, como mostra [David Tong — Electromagnetism, seção 5.6.2](https://davidtong.org/pdfs/teaching/electromagnetism/electro.pdf). Portanto, κB²/(2µ0) só estima uma escala dimensional de componentes; para EM puro e Λ=0 não é o escalar de Ricci, que tem R=0. Não foi resolvida a gravitação do aparelho completo.

## 5. O que autoriza cada conclusão depois da montagem

| Conclusão possível | Evidência necessária |
|---|---|
| “O desenho é montável” | Peças fabricadas, encaixe, cotas reais, fotos e acesso às conexões/sensores |
| “O cálculo é reproduzível” | Código/parâmetros, testes de referências e convergência, resultados numéricos; não é experimento |
| “Campo e ressonância convencionais funcionam” | P01–P05 com parâmetros medidos, sensores calibrados, controles e resíduos dentro da incerteza |
| “O receptor entrega potência” | P06 com aquisição simultânea e limite elétrico definido; fonte de energia identificada |
| “O PI DC funciona no equipamento” | P08 no hardware, planta/atrasos medidos, erro/resposta/limites documentados |
| “Existe efeito não explicado no modelo” | Previsão anterior e discrepância reprodutível acima da incerteza, controles que eliminem artefatos; ainda requer investigação |
| “A alegação extraordinária específica foi sustentada” | Modelo físico definido e previsões próprias, dados independentes, análise de alternativas e replicação; a arte sozinha não fornece isso |

Todas essas avaliações permanecem futuras quanto ao aparelho físico. Quando um ensaio não tem sensibilidade suficiente, a decisão adequada é inconclusivo, com o limite de detecção registrado. Não preencher resultados com valores simulados como se fossem dados medidos.
