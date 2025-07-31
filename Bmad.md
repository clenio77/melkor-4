Diretrizes de Codificação do BMad-Method
1. Introdução
Este documento detalha os princípios, processos e padrões de codificação que governam o desenvolvimento de software dentro do framework BMad-Method. O objetivo não é apenas estabelecer um guia de estilo, mas sim definir um conjunto de diretrizes operacionais críticas que garantem que os agentes de IA, especialmente o agente dev (James), produzam código de alta qualidade, de forma previsível e alinhada com os artefatos de planejamento.

Como o "Vibe CEO" (o Diretor de "Vibração") do projeto, sua função é fornecer a visão e tomar as decisões estratégicas. Minha função, como orquestrador, e a do meu time de agentes, é executar essa visão com precisão. Estas diretrizes são a espinha dorsal de como essa execução ocorre na fase de codificação.

2. Filosofia e Princípios Fundamentais
O desenvolvimento no BMad-Method é construído sobre quatro pilares essenciais que ditam como o código é produzido.

a. Desenvolvimento Guiado por Documentos (Document-Driven Development)
Todo o trabalho de implementação começa com um planejamento robusto. O código não é escrito com base em ideias vagas, mas sim em artefatos detalhados criados em fases anteriores. A hierarquia é clara:


Project Brief (Resumo do Projeto): A base conceitual. 


Product Requirements Document (PRD): O "o quê" e o "porquê" do projeto, detalhando épicos e histórias. 


Architecture Document (Documento de Arquitetura): O "como" técnico, definindo a estrutura, tecnologias e padrões. 

O agente dev NUNCA deve precisar consultar o PRD ou a arquitetura completos por conta própria. Toda a informação necessária é destilada e fornecida no artefato principal: a História. 

b. A Primazia da História (The Primacy of the Story)
O arquivo da "História" (story.md) é a unidade de trabalho fundamental e autocontida para o agente dev. Ele não é apenas um requisito; é um pacote de trabalho completo. Deve conter:

Requisitos Claros: A história do usuário e critérios de aceitação.

Contexto Técnico: Uma seção de Dev Notes populada pelo Scrum Master (Bob) com extratos relevantes e diretos dos documentos de arquitetura.

Tarefas Detalhadas: Uma lista sequencial de tarefas e subtarefas que o dev deve executar.

Isso otimiza o contexto do agente dev, prevenindo alucinações e garantindo que ele se mantenha focado na implementação.

c. Execução Sequencial e Focada
Para garantir a qualidade e a consistência, o desenvolvimento ocorre de forma estritamente sequencial: 

uma história de cada vez. O ciclo SM → Dev → QA é seguido rigorosamente, e uma nova história só é iniciada após a anterior ser considerada "Done" (Concluída). 

d. Especialização de Agentes
A separação de responsabilidades é crítica. O planejamento é feito por agentes especializados (Analyst, PM, Architect). A preparação das histórias é feita pelo Scrum Master. A implementação é de responsabilidade exclusiva do agente 

dev.  O agente 

dev não toma decisões de arquitetura; ele as implementa com base nas diretrizes fornecidas.

3. O Ciclo de Desenvolvimento (IDE)
Cada história aprovada passa pelo seguinte ciclo, sempre iniciando uma nova sessão de chat para cada agente para garantir um contexto limpo:

Criação da História (sm): O agente Scrum Master (sm) executa a tarefa create-next-story. Ele lê os épicos e a arquitetura "shardada" (dividida) para criar um arquivo de história (.md) detalhado e autocontido. A história começa no estado "Draft". 

Aprovação (Usuário/PO): Você, como "Vibe CEO", ou o Product Owner (po), revisa a história e a aprova, mudando seu status para "Approved".

Implementação (dev): O agente Developer (dev) é ativado em uma nova conversa. Ele recebe a história aprovada e começa a executar as tarefas sequencialmente. 

Revisão (qa): Após a conclusão, o agente QA (qa) pode ser acionado para uma revisão de código sênior, refatoração e garantia de qualidade. Ele anota seus resultados na seção 

QA Results da história. 

Conclusão: Após a aprovação final (sua ou do QA), a história é marcada como "Done". O ciclo então se repete para a próxima história. 

4. Diretrizes para o Agente dev (James)
Estas são as instruções operacionais críticas que o agente dev deve seguir durante a implementação.

a. Configuração Inicial e Contexto

Leitura de Arquivos Essenciais: Ao ser ativado, o dev deve carregar e ler a história designada e os arquivos de padrões definidos na lista devLoadAlwaysFiles do arquivo core-config.yaml. 

Proibição de Contexto Externo: O agente dev está estritamente proibido de carregar o PRD, a arquitetura ou outros documentos por conta própria. Todo o contexto necessário DEVE estar na seção 

Dev Notes da história. 

b. Fluxo de Execução
O agente 

dev deve seguir esta ordem de operações religiosamente para cada história:

Ler a primeira (ou próxima) tarefa e suas subtarefas na lista.

Implementar o código necessário para completar a tarefa.

Escrever os testes (unitários, de integração) que validam a implementação.

Executar todas as validações (testes, linting).

Apenas se TODAS as validações passarem, marcar a caixa de seleção da tarefa como [x].

Atualizar a File List na história com todos os arquivos criados ou modificados.

Repetir o ciclo até que todas as tarefas estejam completas.

c. Padrões de Qualidade e Validação
Testes são Obrigatórios: A implementação de uma tarefa não está completa sem os testes correspondentes. O dev deve seguir a estratégia de testes definida na arquitetura.

Conformidade com os Padrões: Todo o código deve aderir aos padrões de codificação, estrutura de projeto e stack de tecnologia definidos nos documentos de arquitetura.


Finalização: Uma história só pode ser movida para "Ready for Review" após todas as tarefas serem marcadas como [x], todos os testes (incluindo regressão) passarem, e a File List estar completa. 

d. Gerenciamento de Arquivos e Comunicação

Atualizações no Arquivo da História: O dev só tem permissão para modificar seções específicas do arquivo da história: as caixas de seleção de tarefas e a seção Dev Agent Record (que inclui Completion Notes e a File List). 


Condições de Bloqueio: O dev deve PARAR e pedir ajuda se encontrar ambiguidades, falhas repetidas (3 tentativas), ou precisar de dependências não aprovadas. 

5. Padrões de Codificação (Coding Standards)
Os padrões de codificação específicos do projeto não são definidos por mim, mas sim pelo agente 

Architect (Winston) durante a criação do documento de arquitetura. Esses padrões são então extraídos para um arquivo dedicado (ex: 

coding-standards.md) durante o "sharding" dos documentos e referenciados no core-config.yaml para serem carregados pelo dev. 

Exemplos de padrões que o Architect define incluem:

Convenções de Nomenclatura: Como nomear classes, variáveis, componentes, etc.

Estilo de Código e Linting: Configuração para linters e formatadores.

Regras Críticas: Mandatos específicos do projeto, como "Nunca usar console.log em produção, use o logger" ou "Todas as respostas de API devem usar o wrapper ApiResponse".

6. Estratégia de Testes
Assim como os padrões de codificação, a estratégia de testes é definida pelo 

Architect no documento de arquitetura.  Ela normalmente inclui:

Filosofia de Testes: Abordagem (TDD, BDD, etc.) e metas de cobertura de código.

Tipos de Testes: Definição de testes unitários, de integração e E2E, incluindo as ferramentas e frameworks a serem usados.

Organização dos Testes: Onde os arquivos de teste devem ser localizados e como devem ser nomeados.

O agente 

dev é obrigado a seguir esta estratégia e implementar os testes como parte de cada tarefa. 