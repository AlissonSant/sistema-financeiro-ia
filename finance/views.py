from django.shortcuts import render
from .models import Transacao

def home(request):
    transacoes = Transacao.objects.all().order_by('-data')
    
    # Calcular totais
    receitas = sum([t.valor for t in transacoes if t.tipo == 'receita'])
    despesas = sum([t.valor for t in transacoes if t.tipo == 'despesa'])
    saldo = receitas - despesas
    
    context = {
        'transacoes': transacoes,
        'receitas': receitas,
        'despesas': despesas,
        'saldo': saldo,
    }
    
    return render(request, 'finance/home.html', context)