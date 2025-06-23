# finance/insights.py - VERSÃO CORRIGIDA
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal  # 🔧 ADICIONADO
from .models import Transacao
import calendar

class FinancialInsights:
    def __init__(self, user):
        self.user = user
        self.hoje = timezone.now().date()
        self.mes_atual = self.hoje.month
        self.ano_atual = self.hoje.year
        
    def get_insights(self):
        """Retorna todos os insights financeiros do usuário"""
        insights = []
        
        # 💰 Análise de Receitas vs Despesas
        insights.extend(self._analise_receitas_despesas())
        
        # 📊 Análise por Categoria
        insights.extend(self._analise_categorias())
        
        # 📈 Comparação com Mês Anterior
        insights.extend(self._comparacao_mes_anterior())
        
        # 🎯 Sugestões de Economia
        insights.extend(self._sugestoes_economia())
        
        # 📅 Padrões de Gastos
        insights.extend(self._padroes_gastos())
        
        return insights
    
    def _analise_receitas_despesas(self):
        """Análise básica de receitas vs despesas"""
        insights = []
        
        # Dados do mês atual
        transacoes_mes = self._get_transacoes_mes_atual()
        receitas = transacoes_mes.filter(tipo='receita').aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
        despesas = transacoes_mes.filter(tipo='despesa').aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
        saldo = receitas - despesas
        
        if receitas > 0:
            percentual_gastos = (despesas / receitas) * Decimal('100')  # 🔧 CORRIGIDO
            
            if percentual_gastos > 90:
                insights.append({
                    'tipo': 'warning',
                    'icone': '⚠️',
                    'titulo': 'Atenção aos Gastos!',
                    'descricao': f'Você já gastou {float(percentual_gastos):.1f}% da sua renda este mês.',
                    'dica': 'Considere revisar seus gastos para manter o equilíbrio financeiro.'
                })
            elif percentual_gastos < 70:
                insights.append({
                    'tipo': 'success',
                    'icone': '✅',
                    'titulo': 'Parabéns! Ótimo Controle',
                    'descricao': f'Você gastou apenas {float(percentual_gastos):.1f}% da sua renda.',
                    'dica': f'Continue assim! Você economizou R$ {float(saldo):.2f} este mês.'
                })
        
        return insights
    
    def _analise_categorias(self):
        """Análise de gastos por categoria"""
        insights = []
        
        # Top 3 categorias com mais gastos
        top_categorias = (
            self._get_transacoes_mes_atual()
            .filter(tipo='despesa')
            .values('categoria')
            .annotate(total=Sum('valor'))
            .order_by('-total')[:3]
        )
        
        if top_categorias:
            categoria_top = top_categorias[0]
            categoria_nome = dict(Transacao.CATEGORIAS)[categoria_top['categoria']]
            
            insights.append({
                'tipo': 'info',
                'icone': '📊',
                'titulo': f'Maior Gasto: {categoria_nome}',
                'descricao': f'R$ {float(categoria_top["total"]):.2f} gastos nesta categoria este mês.',
                'dica': 'Analise se esses gastos estão dentro do planejado.'
            })
        
        return insights
    
    def _comparacao_mes_anterior(self):
        """Compara gastos do mês atual com o anterior"""
        insights = []
        
        # Dados mês atual
        despesas_atual = (
            self._get_transacoes_mes_atual()
            .filter(tipo='despesa')
            .aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
        )
        
        # Dados mês anterior
        mes_anterior = self.mes_atual - 1 if self.mes_atual > 1 else 12
        ano_anterior = self.ano_atual if self.mes_atual > 1 else self.ano_atual - 1
        
        despesas_anterior = (
            Transacao.objects
            .filter(
                usuario=self.user,
                tipo='despesa',
                data__year=ano_anterior,
                data__month=mes_anterior
            )
            .aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
        )
        
        if despesas_anterior > 0:
            variacao = ((despesas_atual - despesas_anterior) / despesas_anterior) * Decimal('100')  # 🔧 CORRIGIDO
            
            if variacao > 10:
                insights.append({
                    'tipo': 'warning',
                    'icone': '📈',
                    'titulo': 'Gastos Aumentaram',
                    'descricao': f'Seus gastos aumentaram {float(variacao):.1f}% comparado ao mês passado.',
                    'dica': 'Verifique onde ocorreram os maiores aumentos.'
                })
            elif variacao < -10:
                insights.append({
                    'tipo': 'success',
                    'icone': '📉',
                    'titulo': 'Economia Detectada!',
                    'descricao': f'Você reduziu seus gastos em {float(abs(variacao)):.1f}% este mês.',
                    'dica': f'Parabéns! Você economizou R$ {float(abs(despesas_atual - despesas_anterior)):.2f}.'
                })
        
        return insights
    
    def _sugestoes_economia(self):
        """Gera sugestões inteligentes de economia"""
        insights = []
        
        # Analisa categoria com mais gastos
        categoria_maior = (
            self._get_transacoes_mes_atual()
            .filter(tipo='despesa')
            .values('categoria')
            .annotate(total=Sum('valor'))
            .order_by('-total')
            .first()
        )
        
        if categoria_maior and categoria_maior['total'] > Decimal('500'):  # 🔧 CORRIGIDO
            categoria_nome = dict(Transacao.CATEGORIAS)[categoria_maior['categoria']]
            economia_10 = categoria_maior['total'] * Decimal('0.1')  # 🔧 CORRIGIDO
            
            insights.append({
                'tipo': 'tip',
                'icone': '💡',
                'titulo': 'Oportunidade de Economia',
                'descricao': f'Reduza 10% em {categoria_nome} e economize R$ {float(economia_10):.2f}.',
                'dica': 'Pequenas reduções podem gerar grandes economias!'
            })
        
        return insights
    
    def _padroes_gastos(self):
        """Identifica padrões nos gastos"""
        insights = []
        
        # Conta transações dos últimos 7 dias
        ultimos_7_dias = self.hoje - timedelta(days=7)
        transacoes_recentes = (
            Transacao.objects
            .filter(
                usuario=self.user,
                tipo='despesa',
                data__date__gte=ultimos_7_dias
            )
            .count()
        )
        
        if transacoes_recentes > 15:
            insights.append({
                'tipo': 'info',
                'icone': '🔄',
                'titulo': 'Muitas Transações Recentes',
                'descricao': f'{transacoes_recentes} gastos nos últimos 7 dias.',
                'dica': 'Considere agrupar compras pequenas para melhor controle.'
            })
        
        return insights
    
    def _get_transacoes_mes_atual(self):
        """Retorna transações do mês atual"""
        return Transacao.objects.filter(
            usuario=self.user,
            data__year=self.ano_atual,
            data__month=self.mes_atual
        )
    
    def get_previsao_mensal(self):
        """Prevê gastos para o resto do mês"""
        transacoes_mes = self._get_transacoes_mes_atual()
        despesas_ate_hoje = transacoes_mes.filter(tipo='despesa').aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
        
        # Dias que já passaram no mês
        dias_passados = self.hoje.day
        
        # Total de dias no mês
        dias_totais = calendar.monthrange(self.ano_atual, self.mes_atual)[1]
        
        # Previsão simples baseada na média diária
        if dias_passados > 0:
            media_diaria = despesas_ate_hoje / Decimal(str(dias_passados))  # 🔧 CORRIGIDO
            previsao_total = media_diaria * Decimal(str(dias_totais))  # 🔧 CORRIGIDO
            
            return {
                'previsao_total': float(previsao_total),  # 🔧 CONVERTIDO PARA FLOAT NO TEMPLATE
                'gasto_atual': float(despesas_ate_hoje),
                'dias_restantes': dias_totais - dias_passados,
                'media_diaria': float(media_diaria)
            }
        
        return None