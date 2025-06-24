# finance/alerts.py - SISTEMA DE ALERTAS INTELIGENTES - VERSÃO FINAL
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum
from .models import MetaFinanceira, Transacao

class AlertasInteligentes:
    """Sistema inteligente de alertas financeiros"""
    
    def __init__(self, usuario):
        self.usuario = usuario
        self.alertas = []
    
    def gerar_todos_alertas(self):
        """Gera todos os tipos de alertas para o usuário"""
        self.alertas = []
        
        # Alertas de metas
        self._alertas_metas_urgentes()
        self._alertas_metas_atrasadas()
        self._alertas_metas_parabens()
        
        # Alertas de gastos
        self._alertas_gastos_excessivos()
        self._alertas_sem_transacoes()
        
        return self.alertas
    
    def _alertas_metas_urgentes(self):
        """Metas próximas do prazo (30 dias)"""
        metas_urgentes = MetaFinanceira.objects.filter(
            usuario=self.usuario,
            status='ativa',
            data_prazo__lte=timezone.now().date() + timedelta(days=30),
            data_prazo__gte=timezone.now().date()
        )
        
        for meta in metas_urgentes:
            dias_restantes = meta.dias_restantes
            percentual = meta.percentual_concluido
            
            if percentual < 50 and dias_restantes <= 15:
                self.alertas.append({
                    'tipo': 'urgente',
                    'icone': '🚨',
                    'titulo': f'Meta "{meta.titulo}" precisa de atenção!',
                    'descricao': f'Faltam apenas {dias_restantes} dias e você só alcançou {percentual:.1f}%',
                    'acao': f'Economize R$ {meta.valor_diario_necessario:.2f}/dia para alcançar!',
                    'cor': 'urgente',
                    'meta_id': meta.id
                })
            elif dias_restantes <= 7:
                self.alertas.append({
                    'tipo': 'atencao',
                    'icone': '⏰',
                    'titulo': f'Última semana para "{meta.titulo}"',
                    'descricao': f'Meta termina em {dias_restantes} dias',
                    'acao': f'Faltam R$ {meta.valor_restante:.2f}',
                    'cor': 'warning',
                    'meta_id': meta.id
                })
    
    def _alertas_metas_atrasadas(self):
        """Metas que passaram do prazo"""
        metas_atrasadas = MetaFinanceira.objects.filter(
            usuario=self.usuario,
            status='ativa',
            data_prazo__lt=timezone.now().date()
        )
        
        for meta in metas_atrasadas:
            dias_atraso = (timezone.now().date() - meta.data_prazo).days
            self.alertas.append({
                'tipo': 'atrasada',
                'icone': '📅',
                'titulo': f'Meta "{meta.titulo}" está atrasada',
                'descricao': f'Prazo venceu há {dias_atraso} dias',
                'acao': 'Considere estender o prazo ou pausar a meta',
                'cor': 'urgente',
                'meta_id': meta.id
            })
    
    def _alertas_metas_parabens(self):
        """Metas com bom progresso - motivação!"""
        metas_ativas = MetaFinanceira.objects.filter(
            usuario=self.usuario,
            status='ativa'
        )
        
        for meta in metas_ativas:
            percentual = meta.percentual_concluido
            
            if percentual >= 90:
                self.alertas.append({
                    'tipo': 'sucesso',
                    'icone': '🎉',
                    'titulo': f'Quase lá! "{meta.titulo}"',
                    'descricao': f'Você já alcançou {percentual:.1f}% da meta!',
                    'acao': f'Faltam apenas R$ {meta.valor_restante:.2f}',
                    'cor': 'success',
                    'meta_id': meta.id
                })
            elif percentual >= 75:
                self.alertas.append({
                    'tipo': 'motivacao',
                    'icone': '💪',
                    'titulo': f'Ótimo progresso em "{meta.titulo}"',
                    'descricao': f'{percentual:.1f}% concluído - Continue assim!',
                    'acao': 'Você está no caminho certo!',
                    'cor': 'info',
                    'meta_id': meta.id
                })
    
    def _alertas_gastos_excessivos(self):
        """Alertas baseados em padrão de gastos"""
        try:
            hoje = timezone.now().date()
            mes_atual = hoje.replace(day=1)
            
            # Gastos do mês atual
            gastos_mes = Transacao.objects.filter(
                usuario=self.usuario,
                tipo='despesa',
                data__gte=mes_atual
            ).aggregate(total=Sum('valor'))['total'] or 0
            
            # Alerta se gastou mais de R$ 1000 no mês
            if gastos_mes > 1000:
                self.alertas.append({
                    'tipo': 'gasto_alto',
                    'icone': '💳',
                    'titulo': 'Gastos elevados este mês',
                    'descricao': f'Você já gastou R$ {gastos_mes:.2f} este mês',
                    'acao': 'Revise seus gastos nas próximas semanas',
                    'cor': 'warning',
                    'meta_id': None
                })
        except Exception:
            # Se der erro, apenas ignora este alerta
            pass
    
    def _alertas_sem_transacoes(self):
        """Alerta se usuário não registrou transações recentemente"""
        try:
            ultima_transacao = Transacao.objects.filter(
                usuario=self.usuario
            ).order_by('-data').first()
            
            if ultima_transacao:
                dias_sem_registro = (timezone.now().date() - ultima_transacao.data.date()).days
                
                if dias_sem_registro >= 7:
                    self.alertas.append({
                        'tipo': 'lembrete',
                        'icone': '📝',
                        'titulo': 'Que tal registrar suas transações?',
                        'descricao': f'Há {dias_sem_registro} dias sem registros',
                        'acao': 'Mantenha seu controle financeiro em dia!',
                        'cor': 'info',
                        'meta_id': None
                    })
            else:
                # Nenhuma transação registrada ainda
                self.alertas.append({
                    'tipo': 'lembrete',
                    'icone': '🎯',
                    'titulo': 'Comece registrando suas transações',
                    'descricao': 'Você ainda não registrou nenhuma transação',
                    'acao': 'Adicione suas receitas e despesas para começar!',
                    'cor': 'info',
                    'meta_id': None
                })
        except Exception:
            # Se der erro, apenas ignora este alerta
            pass
    
    def contar_alertas_urgentes(self):
        """Conta alertas urgentes para badge no navbar"""
        urgentes = [a for a in self.alertas if a['tipo'] in ['urgente', 'atrasada']]
        return len(urgentes)
    
    def get_alertas_por_tipo(self, tipo):
        """Filtra alertas por tipo"""
        return [a for a in self.alertas if a['tipo'] == tipo]