# finance/views.py - VERSÃO COMPLETA COM ALERTAS
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Transacao, MetaFinanceira
from .forms import TransacaoForm, CustomUserCreationForm, MetaFinanceiraForm
from .insights import FinancialInsights  # Se você tem este arquivo
from .alerts import AlertasInteligentes  # 🆕 NOVO IMPORT
from .reports import RelatorioFinanceiro 


def index(request):
    """Página inicial"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'finance/index.html')

def login_view(request):
    """View de login"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, 'finance/login.html')

def register_view(request):
    """View de registro"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Conta criada com sucesso! Faça login.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'finance/register.html', {'form': form})

def logout_view(request):
    """View de logout"""
    logout(request)
    return redirect('index')

@login_required
def dashboard(request):
    """Dashboard principal com IA integrada"""
    from django.utils import timezone
    from .ai_engine import FluxAIEngine, FluxAIInsights
    
    # Buscar metas do usuário
    metas_raw = MetaFinanceira.objects.filter(usuario=request.user).order_by('-data_criacao')
    
    # Processar cada meta para garantir que os dados chegam corretos
    metas = []
    for meta in metas_raw:
        # Calcular percentual manualmente
        if meta.valor_objetivo > 0:
            percentual = float((meta.valor_atual / meta.valor_objetivo) * 100)
        else:
            percentual = 0
            
        # Calcular dias restantes
        if meta.data_prazo:
            dias_restantes = max(0, (meta.data_prazo - timezone.now().date()).days)
        else:
            dias_restantes = 0
            
        # Determinar cor da barra baseado no percentual
        if percentual >= 75:
            cor_barra = 'success'
        elif percentual >= 50:
            cor_barra = 'info'
        elif percentual >= 25:
            cor_barra = 'warning'
        else:
            cor_barra = 'danger'
            
        # Criar objeto processado
        meta_processada = {
            'id': meta.id,
            'titulo': meta.titulo,
            'descricao': meta.descricao,
            'tipo': meta.tipo,
            'get_tipo_display': meta.get_tipo_display(),
            'valor_atual': meta.valor_atual,
            'valor_objetivo': meta.valor_objetivo,
            'data_prazo': meta.data_prazo,
            'status': meta.status,
            'get_status_display': meta.get_status_display(),
            'percentual_concluido': round(percentual, 1),
            'dias_restantes': dias_restantes,
            'status_progresso': {'cor': cor_barra},
            'meta_original': meta  # Para casos que precisem do objeto original
        }
        
        metas.append(meta_processada)
    
    # Buscar transações
    transacoes_raw = Transacao.objects.filter(usuario=request.user).order_by('-data')
    
    # Processar transações para gráficos
    gastos_categoria_raw = Transacao.objects.filter(
        usuario=request.user, 
        tipo='despesa'
    ).values('categoria').annotate(total=Sum('valor')).order_by('-total')
    
    # Converter códigos para nomes bonitos
    gastos_categoria = []
    for item in gastos_categoria_raw:
        codigo_categoria = item['categoria']
        nome_categoria = dict(Transacao.CATEGORIAS)[codigo_categoria]
        gastos_categoria.append({
            'categoria': nome_categoria,
            'total': item['total']
        })
    
    # Cálculos financeiros básicos
    receitas = Transacao.objects.filter(usuario=request.user, tipo='receita').aggregate(Sum('valor'))['valor__sum'] or 0
    despesas = Transacao.objects.filter(usuario=request.user, tipo='despesa').aggregate(Sum('valor'))['valor__sum'] or 0
    saldo = receitas - despesas
    
    # 🤖 NOVA SEÇÃO: IA INTEGRADA
    try:
        print(f"🤖 Inicializando IA para {request.user.username}...")
        
        # Inicializar engine de IA
        ai_engine = FluxAIEngine(request.user)
        ai_insights = FluxAIInsights(request.user)
        
        # Gerar insights para o dashboard
        insights_ia = ai_insights.get_insights_dashboard()
        
        # Análise de padrões completa
        padroes_gastos = ai_engine.analisar_padroes_gastos()
        
        # Previsões futuras
        previsao_30_dias = ai_engine.prever_gastos_futuros(30)
        
        # Score financeiro
        score_financeiro = ai_engine.calcular_score_financeiro()
        
        # Alertas inteligentes
        alertas_ia = ai_engine.gerar_alertas_inteligentes()
        
        print(f"✅ IA processada com sucesso! Score: {score_financeiro['score']}/100")
        
    except Exception as e:
        print(f"❌ Erro na IA: {e}")
        # Valores padrão em caso de erro
        insights_ia = []
        padroes_gastos = {'status': 'erro'}
        previsao_30_dias = {'status': 'erro'}
        score_financeiro = {'score': 0, 'classificacao': 'Sem dados', 'cor': 'secondary'}
        alertas_ia = []
    
    # Formulário para nova transação
    if request.method == 'POST':
        form = TransacaoForm(request.POST)
        if form.is_valid():
            transacao = form.save(commit=False)
            transacao.usuario = request.user
            transacao.save()
            messages.success(request, 'Transação adicionada com sucesso!')
            return redirect('dashboard')
    else:
        form = TransacaoForm()
    
    # Preparar dados de previsão para o template
    previsao_template = None
    if previsao_30_dias['status'] == 'sucesso':
        previsao_template = {
            'previsao_total': previsao_30_dias['previsao_total'],
            'gasto_atual': despesas,
            'dias_restantes': 30 - timezone.now().date().day,  # Dias restantes do mês
            'media_diaria': previsao_30_dias['media_diaria_historica'],
            'tendencia': previsao_30_dias['tendencia_percentual']
        }
    
    context = {
        # Dados básicos (já existiam)
        'transacoes': transacoes_raw,
        'form': form,
        'receitas': receitas,
        'despesas': despesas,
        'saldo': saldo,
        'gastos_categoria': gastos_categoria,
        'metas': metas,
        
        # 🤖 NOVOS DADOS DA IA
        'insights_ia': insights_ia,
        'padroes_gastos': padroes_gastos,
        'previsao': previsao_template,
        'score_financeiro': score_financeiro,
        'alertas_ia': alertas_ia,
        
        # Estatísticas da IA para cards
        'ai_ativo': True,
        'total_insights': len(insights_ia),
        'total_alertas': len(alertas_ia),
    }
    
    return render(request, 'finance/dashboard.html', context)

@login_required
def editar_transacao(request, transacao_id):
    """Editar transação existente"""
    transacao = get_object_or_404(Transacao, id=transacao_id, usuario=request.user)
    
    if request.method == 'POST':
        form = TransacaoForm(request.POST, instance=transacao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transação atualizada com sucesso!')
            return redirect('dashboard')
    else:
        form = TransacaoForm(instance=transacao)
    
    return render(request, 'finance/editar_transacao.html', {
        'form': form,
        'transacao': transacao
    })

@login_required
def excluir_transacao(request, transacao_id):
    """Excluir transação"""
    transacao = get_object_or_404(Transacao, id=transacao_id, usuario=request.user)
    
    if request.method == 'POST':
        transacao.delete()
        messages.success(request, 'Transação excluída com sucesso!')
        return redirect('dashboard')
    
    return render(request, 'finance/confirmar_exclusao.html', {
        'transacao': transacao
    })

# 🎯 SISTEMA DE METAS FINANCEIRAS COM ALERTAS

@login_required
def metas_dashboard(request):
    """Dashboard principal das metas com alertas inteligentes"""
    from django.utils import timezone
    from datetime import timedelta
    
    # Buscar metas do usuário
    metas_raw = MetaFinanceira.objects.filter(usuario=request.user).order_by('-data_criacao')
    
    # Processar cada meta para garantir que os dados chegam corretos
    metas = []
    for meta in metas_raw:
        # Calcular percentual manualmente
        if meta.valor_objetivo > 0:
            percentual = float((meta.valor_atual / meta.valor_objetivo) * 100)
        else:
            percentual = 0
            
        # Calcular dias restantes
        if meta.data_prazo:
            dias_restantes = max(0, (meta.data_prazo - timezone.now().date()).days)
        else:
            dias_restantes = 0
            
        # Determinar cor da barra baseado no percentual
        if percentual >= 75:
            cor_barra = 'success'
        elif percentual >= 50:
            cor_barra = 'info'
        elif percentual >= 25:
            cor_barra = 'warning'
        else:
            cor_barra = 'danger'
            
        # Criar objeto processado
        meta_processada = {
            'id': meta.id,
            'titulo': meta.titulo,
            'descricao': meta.descricao,
            'tipo': meta.tipo,
            'get_tipo_display': meta.get_tipo_display(),
            'valor_atual': meta.valor_atual,
            'valor_objetivo': meta.valor_objetivo,
            'data_prazo': meta.data_prazo,
            'status': meta.status,
            'get_status_display': meta.get_status_display(),
            'percentual_concluido': round(percentual, 1),
            'dias_restantes': dias_restantes,
            'status_progresso': {'cor': cor_barra},
            'meta_original': meta  # Para casos que precisem do objeto original
        }
        
        metas.append(meta_processada)
    
    # Estatísticas
    total_metas = metas_raw.count()
    metas_ativas = metas_raw.filter(status='ativa').count()
    metas_concluidas = metas_raw.filter(status='concluida').count()
    metas_urgentes = metas_raw.filter(
        status='ativa',
        data_prazo__lte=timezone.now().date() + timedelta(days=30)
    ).count()
    
    # Alertas (simplificado por enquanto)
    alertas = []
    
    context = {
        'metas': metas,
        'total_metas': total_metas,
        'metas_ativas': metas_ativas,
        'metas_concluidas': metas_concluidas,
        'metas_urgentes': metas_urgentes,
        'alertas': alertas,
        'total_alertas': len(alertas),
        'alertas_urgentes': 0,
    }
    
    return render(request, 'finance/metas_dashboard.html', context)

@login_required
def criar_meta(request):
    """Criar nova meta financeira"""
    if request.method == 'POST':
        form = MetaFinanceiraForm(request.POST)
        if form.is_valid():
            meta = form.save(commit=False)
            meta.usuario = request.user
            
            # Calcular valor mensal sugerido - VERSÃO SEGURA
            try:
                hoje = datetime.now().date()
                dias_restantes = (meta.data_prazo - hoje).days
                
                if dias_restantes > 0:
                    meses_restantes = max(1, dias_restantes / 30.0)
                    valor_mensal = float(meta.valor_objetivo) / meses_restantes
                    meta.valor_mensal_sugerido = Decimal(str(round(valor_mensal, 2)))
            except:
                # Se der qualquer erro, apenas salva sem o cálculo
                pass
            
            meta.save()
            messages.success(request, f'🎯 Meta "{meta.titulo}" criada com sucesso!')
            return redirect('metas_dashboard')
        else:
            messages.error(request, 'Verifique os dados informados.')
    else:
        form = MetaFinanceiraForm()
    
    return render(request, 'finance/criar_meta.html', {'form': form})

@login_required
def detalhes_meta(request, meta_id):
    """Detalhes da meta com progresso"""
    meta = get_object_or_404(MetaFinanceira, id=meta_id, usuario=request.user)
    
    # Adicionar progresso
    if request.method == 'POST':
        valor = request.POST.get('valor')
        if valor:
            try:
                from decimal import Decimal
                valor_decimal = Decimal(str(valor))
                if valor_decimal > 0:
                    meta.adicionar_progresso(valor_decimal)
                    messages.success(request, f'💰 R$ {valor_decimal:.2f} adicionado ao progresso!')
                    return redirect('detalhes_meta', meta_id=meta.id)
            except ValueError:
                messages.error(request, 'Valor inválido!')
    
    # Insights da IA
    insights = meta.get_sugestoes_ia()
    
    context = {
        'meta': meta,
        'insights': insights,
        'valor_restante': meta.valor_restante,
        'dias_restantes': meta.dias_restantes,
        'valor_diario_necessario': meta.valor_diario_necessario,
        'percentual_concluido': meta.percentual_concluido,
    }
    
    return render(request, 'finance/detalhes_meta.html', context)

@login_required
def editar_meta(request, meta_id):
    """Editar meta existente"""
    meta = get_object_or_404(MetaFinanceira, id=meta_id, usuario=request.user)
    
    if request.method == 'POST':
        form = MetaFinanceiraForm(request.POST, instance=meta)
        if form.is_valid():
            form.save()
            messages.success(request, f'✏️ Meta "{meta.titulo}" atualizada!')
            return redirect('detalhes_meta', meta_id=meta.id)
    else:
        form = MetaFinanceiraForm(instance=meta)
    
    return render(request, 'finance/criar_meta.html', {
        'form': form,
        'meta': meta,
        'editando': True
    })

@login_required
def pausar_meta(request, meta_id):
    """Pausar/Ativar meta"""
    meta = get_object_or_404(MetaFinanceira, id=meta_id, usuario=request.user)
    
    if meta.status == 'ativa':
        meta.status = 'pausada'
        messages.info(request, f'⏸️ Meta "{meta.titulo}" pausada.')
    elif meta.status == 'pausada':
        meta.status = 'ativa'
        messages.success(request, f'▶️ Meta "{meta.titulo}" reativada!')
    
    meta.save()
    return redirect('metas_dashboard')

@login_required
def excluir_meta(request, meta_id):
    """Excluir meta"""
    meta = get_object_or_404(MetaFinanceira, id=meta_id, usuario=request.user)
    
    if request.method == 'POST':
        titulo = meta.titulo
        meta.delete()
        messages.success(request, f'🗑️ Meta "{titulo}" excluída.')
        return redirect('metas_dashboard')
    
    return render(request, 'finance/confirmar_exclusao_meta.html', {'meta': meta})

# 🚨 NOVA VIEW: Página de alertas
@login_required
def alertas_view(request):
    """Página dedicada aos alertas"""
    sistema_alertas = AlertasInteligentes(request.user)
    alertas = sistema_alertas.gerar_todos_alertas()
    
    # Organizar alertas por tipo
    alertas_por_tipo = {
        'urgentes': sistema_alertas.get_alertas_por_tipo('urgente'),
        'atrasadas': sistema_alertas.get_alertas_por_tipo('atrasada'),
        'sucesso': sistema_alertas.get_alertas_por_tipo('sucesso'),
        'motivacao': sistema_alertas.get_alertas_por_tipo('motivacao'),
        'outros': [a for a in alertas if a['tipo'] not in ['urgente', 'atrasada', 'sucesso', 'motivacao']]
    }
    
    context = {
        'alertas': alertas,
        'alertas_por_tipo': alertas_por_tipo,
        'total_alertas': len(alertas),
    }
    
    return render(request, 'finance/alertas.html', context)

# 🚀 Gerar relatório financeiro em PDF
@login_required
def gerar_relatorio_pdf(request):
    """Gerar relatório financeiro em PDF"""
    gerador = RelatorioFinanceiro(request.user)
    return gerador.gerar_relatorio_completo()