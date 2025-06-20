from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum
from .models import Transacao
from .forms import TransacaoForm

def home(request):
    # Processar formulário se for POST
    if request.method == 'POST':
        form = TransacaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Transação adicionada com sucesso!')
            return redirect('home')
    else:
        form = TransacaoForm()
    
    # Buscar todas as transações
    transacoes = Transacao.objects.all().order_by('-data')
    
    # Calcular totais
    receitas = sum([t.valor for t in transacoes if t.tipo == 'receita'])
    despesas = sum([t.valor for t in transacoes if t.tipo == 'despesa'])
    saldo = receitas - despesas
    
    # NOVO: Dados para gráfico - gastos por categoria
    gastos_categoria = (
        Transacao.objects
        .filter(tipo='despesa')
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
        'gastos_categoria': gastos_categoria,  # ← NOVO!
    }
    
    return render(request, 'finance/home.html', context)