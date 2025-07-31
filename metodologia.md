🧾 Passo a Passo para Criar o Projeto – LLM Developer Assistant
🔹 Objetivo do Projeto:
Desenvolver uma aplicação web que simule a atuação de um advogado criminalista no Tribunal do Júri, com base em análise de documentos processuais, usando backend com Django + DRF e frontend com Next.js (ou React).

1️⃣ Etapa Inicial: Configuração do Ambiente
Instruções para a LLM:

Crie uma estrutura de projeto com Django no backend e Next.js no frontend.

Separe os diretórios em backend/ e frontend/.

2️⃣ Backend – Django + Django REST Framework
Comandos:

bash
Copiar
Editar
django-admin startproject backend
cd backend
python manage.py startapp core
pip install djangorestframework python-decouple PyMuPDF pdfplumber openai
Tarefas da LLM:

Configurar o settings.py com DRF, CORS e o app core.

Criar modelos:

Processo (titulo, descrição, documentos)

Documento (arquivo PDF, texto extraído)

Analise (bloco, subetapa, resposta gerada)

Criar views com ModelViewSet e rotas da API REST.

Criar endpoint POST para enviar arquivo e gerar análise com OpenAI.

3️⃣ Módulo de IA – Integração com OpenAI
Tarefas da LLM:

Criar um módulo chamado ai_engine/processor.py.

Função que recebe o texto de um processo e a subetapa do júri.

Com base nisso, gerar resposta com o prompt adequado do arquivo Instruções de Análise.pdf.

Usar a API do ChatGPT com modelo GPT-4 (gpt-4-1106-preview ou superior).

4️⃣ Frontend – Next.js
Comandos:

bash
Copiar
Editar
npx create-next-app@latest frontend
cd frontend
npm install axios react-dropzone tailwindcss
Tarefas da LLM:

Criar página inicial com menu dos blocos do júri.

Criar página dinâmica analise/[bloco].js para:

Fazer upload de documentos

Selecionar subetapas

Enviar para API Django e receber análise

Criar componentes: UploadFile, ResultadoAnalise, NavegacaoEtapas.

5️⃣ Funcionalidades Específicas
Requisitos adicionais para a LLM:

Permitir upload múltiplo de arquivos PDF no frontend.

Backend deve extrair texto do PDF e armazenar.

Cada subetapa tem um prompt específico que deve ser utilizado no backend.

Criar middleware de autenticação JWT (Django + Next.js).

6️⃣ Recursos Adicionais
Extra para a LLM:

Criar painel de administração com Django Admin.

Implementar modo “Análise Completa” que percorre todos os blocos.

Adicionar loading e tratamento de erros nas análises.

7️⃣ Deploy (Opcional)
Criar Dockerfile para backend e frontend.

Criar docker-compose.yml para rodar tudo junto com PostgreSQL.

✅ Observações Importantes
Baseie-se nas instruções contidas nos arquivos: Persona Melkor 3.0.pdf e Instruções de análise.pdf.

Mantenha o sistema de análise dividido em blocos e subetapas conforme os prompts.

A IA deve simular um advogado criminalista (inspiração: Dr. Jader Marques).

