from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.urls import reverse
from django.core.files.storage import default_storage

from core.models import Processo, Documento, Usuario, SessaoAnalise, ResultadoAnalise
from ai_engine.processor import KermartinProcessor
from ai_engine.security import SecurityValidator

@require_http_methods(["GET"])  # Página inicial simples
def home(request):
    if request.user.is_authenticated:
        return redirect('webui:dashboard')
    return redirect('webui:login')

@require_http_methods(["GET", "POST"])  # Login
def login_view(request):
    if request.user.is_authenticated:
        return redirect('webui:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # garantir perfil Usuario
            Usuario.objects.get_or_create(user=user, defaults={
                'nome_completo': user.username,
                'oab_numero': '000000',
                'oab_estado': 'RS'
            })
            return redirect('webui:dashboard')
        messages.error(request, 'Credenciais inválidas')
    return render(request, 'webui/login.html')

@login_required
@require_http_methods(["POST"])  # Logout
def logout_view(request):
    logout(request)
    return redirect('webui:login')

@login_required
@require_http_methods(["GET"])  # Dashboard com processos e menu
def dashboard(request):
    usuario = Usuario.objects.filter(user=request.user).first()
    processos = Processo.objects.filter(usuario=usuario).order_by('-created_at') if usuario else []
    return render(request, 'webui/dashboard.html', {
        'processos': processos,
    })

@login_required
@require_http_methods(["POST"])  # Criar novo processo
def novo_processo(request):
    usuario = Usuario.objects.get(user=request.user)
    titulo = request.POST.get('titulo') or 'Processo sem título'
    processo = Processo.objects.create(usuario=usuario, titulo=titulo)
    messages.success(request, 'Processo criado com sucesso')
    return redirect('webui:upload_documento', processo_id=processo.id)

@login_required
@require_http_methods(["GET", "POST"])  # Upload de documento
def upload_documento(request, processo_id):
    processo = get_object_or_404(Processo, id=processo_id, usuario__user=request.user)

    if request.method == 'POST':
        arquivo = request.FILES.get('arquivo')
        tipo = request.POST.get('tipo_documento') or 'inquerito'
        if not arquivo:
            messages.error(request, 'Selecione um arquivo PDF')
            return redirect(request.path)

        # Validações de segurança
        sec = SecurityValidator()
        v = sec.validate_file_upload(arquivo)
        if not v['valid']:
            messages.error(request, 'Arquivo inválido: ' + ', '.join(v['errors']))
            return redirect(request.path)

        doc = Documento.objects.create(
            processo=processo,
            nome_arquivo=arquivo.name,
            arquivo_original=arquivo,
            tipo_documento=tipo,
        )

        # Tentar extrair texto (não bloqueante)
        from ai_engine.document_processor import DocumentProcessor
        try:
            processor = DocumentProcessor()
            texto = processor.extract_text_from_pdf(doc.arquivo_original.path)
            doc.texto_extraido = texto
            doc.tamanho_arquivo = doc.arquivo_original.size or 0
            doc.save()
            messages.success(request, 'Documento enviado e processado com sucesso')
        except Exception as e:
            messages.warning(request, f'Documento salvo, mas falha ao processar: {e}')

        return redirect('webui:iniciar_analise', processo_id=processo.id)

    return render(request, 'webui/upload.html', {
        'processo': processo,
    })

@login_required
@require_http_methods(["GET", "POST"])  # Menu de blocos e subetapas e iniciar análise
def iniciar_analise(request, processo_id):
    processo = get_object_or_404(Processo, id=processo_id, usuario__user=request.user)

    if request.method == 'POST':
        modo = request.POST.get('modo')  # individual | completa
        bloco = int(request.POST.get('bloco') or 1)
        subetapa = int(request.POST.get('subetapa') or 1)

        # Verificar se há documentos com texto
        if not processo.documentos.filter(texto_extraido__isnull=False).exists():
            messages.error(request, 'Nenhum documento processado neste processo')
            return redirect(request.path)

        # Criar sessão
        sessao = SessaoAnalise.objects.create(
            processo=processo,
            modo_analise='individual' if modo == 'individual' else 'completa',
            blocos_selecionados=[bloco] if modo == 'individual' else [1, 2, 3, 4],
        )

        proc = KermartinProcessor()
        try:
            if modo == 'individual':
                documento = processo.documentos.filter(texto_extraido__isnull=False).first()
                proc.analyze_document(documento, bloco, subetapa, sessao)
            else:
                docs = list(processo.documentos.filter(texto_extraido__isnull=False))
                proc.analyze_complete_process(docs, sessao)
            messages.success(request, 'Análise iniciada com sucesso')
            return redirect('webui:ver_resultado', sessao_id=sessao.id)
        except Exception as e:
            messages.error(request, f'Erro na análise: {e}')
            return redirect(request.path)

    # Menu: blocos e subetapas
    blocos = {
        1: list(range(1, 7)),
        2: list(range(1, 6)),
        3: list(range(1, 6)),
        4: list(range(1, 6)),
    }

    return render(request, 'webui/menu.html', {
        'processo': processo,
        'blocos': blocos,
    })

@login_required
@require_http_methods(["GET"])  # Ver resultado resumido
def ver_resultado(request, sessao_id):
    sessao = get_object_or_404(SessaoAnalise, id=sessao_id, processo__usuario__user=request.user)
    resultados = ResultadoAnalise.objects.filter(sessao=sessao).order_by('bloco', 'subetapa')

    return render(request, 'webui/resultado.html', {
        'sessao': sessao,
        'resultados': resultados,
    })

