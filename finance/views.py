# finance/views.py - VERSÃO FINAL COMPLETA
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Transacao
from .forms import TransacaoForm, CustomUserCreationForm

# View pública - página inicial/login
def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'finance/index.html')

# Cadastro de usuário
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}! Faça login.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'finance/register.html', {'form': form})

# Login personalizado
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    return render(request, 'finance/login.html')

# Dashboard (página principal - só logado)
@login_required
def dashboard(request):
    # Processar formulário se for POST
    if request.method == 'POST':
        form = TransacaoForm(request.POST)
        if form.is_valid():
            transacao = form.save(commit=False)
            transacao.usuario = request.user  # ✅ AGORA FUNCIONA!
            transacao.save()
            messages.success(request, '✅ Transação adicionada com sucesso!')
            return redirect('dashboard')
    else:
        form = TransacaoForm()
    
    # ✅ Buscar apenas transações do usuário logado
    transacoes = Transacao.objects.filter(usuario=request.user).order_by('-data')
    
    # Calcular totais
    receitas = sum([t.valor for t in transacoes if t.tipo == 'receita'])
    despesas = sum([t.valor for t in transacoes if t.tipo == 'despesa'])
    saldo = receitas - despesas
    
    # Dados para gráfico - gastos por categoria do usuário
    gastos_categoria = (
        Transacao.objects
        .filter(tipo='despesa', usuario=request.user)
        .values('categoria')
        .annotate(total=Sum('valor'))
        .order_by('-total')
    )
    
    context = {
        'transacoes': transacoes,
        'receitas': receitas,
        'despesas': despesas,
        'saldo': saldo,
        'form': form,
        'gastos_categoria': gastos_categoria,
    }
    
    return render(request, 'finance/dashboard.html', context)

# ✅ EDITAR TRANSAÇÃO
@login_required
def editar_transacao(request, transacao_id):
    # Buscar transação do usuário logado
    transacao = get_object_or_404(Transacao, id=transacao_id, usuario=request.user)
    
    if request.method == 'POST':
        form = TransacaoForm(request.POST, instance=transacao)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Transação editada com sucesso!')
            return redirect('dashboard')
    else:
        form = TransacaoForm(instance=transacao)
    
    context = {
        'form': form,
        'transacao': transacao,
        'titulo': 'Editar Transação'
    }
    return render(request, 'finance/editar_transacao.html', context)

# ✅ EXCLUIR TRANSAÇÃO
@login_required
def excluir_transacao(request, transacao_id):
    # Buscar transação do usuário logado
    transacao = get_object_or_404(Transacao, id=transacao_id, usuario=request.user)
    
    if request.method == 'POST':
        transacao.delete()
        messages.success(request, '🗑️ Transação excluída com sucesso!')
        return redirect('dashboard')
    
    context = {
        'transacao': transacao
    }
    return render(request, 'finance/confirmar_exclusao.html', context)

# Logout
def logout_view(request):
    logout(request)
    messages.info(request, 'Logout realizado com sucesso!')
    return redirect('index')