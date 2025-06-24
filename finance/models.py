# finance/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Transacao(models.Model):
    # 🆕 Campo para associar transação ao usuário
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    TIPOS = [
        ('receita', '💰 Receita'),
        ('despesa', '💸 Despesa'),
    ]
    
    CATEGORIAS = [
        ('alimentacao', '🍔 Alimentação'),
        ('transporte', '🚗 Transporte'),
        ('lazer', '🎮 Lazer'),
        ('saude', '🏥 Saúde'),
        ('educacao', '📚 Educação'),
        ('casa', '🏠 Casa'),
        ('outros', '📦 Outros'),
    ]
    
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    data = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-data']  # Ordena por data decrescente
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.valor} ({self.get_tipo_display()})"
    
    # ADICIONE isso NO FINAL do seu models.py (depois da classe Transacao)

class MetaFinanceira(models.Model):
    TIPOS_META = [
        ('economia', '💰 Economia'),
        ('investimento', '📈 Investimento'),
        ('pagamento', '💳 Pagamento de Dívida'),
        ('compra', '🛒 Compra Específica'),
    ]
    
    STATUS_CHOICES = [
        ('ativa', '🎯 Ativa'),
        ('pausada', '⏸️ Pausada'),
        ('concluida', '✅ Concluída'),
        ('cancelada', '❌ Cancelada'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200, help_text="Ex: Viagem para Europa")
    descricao = models.TextField(blank=True, help_text="Descrição detalhada da meta")
    tipo = models.CharField(max_length=20, choices=TIPOS_META, default='economia')
    
    # Valores financeiros
    valor_objetivo = models.DecimalField(max_digits=12, decimal_places=2, help_text="Quanto quer alcançar?")
    valor_atual = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Quanto já conseguiu")
    
    # Datas
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_prazo = models.DateField(help_text="Até quando quer alcançar?")
    data_conclusao = models.DateTimeField(null=True, blank=True)
    
    # Status e configurações
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativa')
    valor_mensal_sugerido = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notificacoes_ativas = models.BooleanField(default=True)
    
    # Campos para gamificação
    conquistas = models.JSONField(default=list, blank=True)  # Lista de conquistas alcançadas
    streak_dias = models.IntegerField(default=0)  # Sequência de dias cumprindo meta
    
    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Meta Financeira'
        verbose_name_plural = 'Metas Financeiras'
    
    def __str__(self):
        return f"{self.titulo} - R$ {self.valor_atual}/{self.valor_objetivo}"
    
    @property
    def percentual_concluido(self):
        """Retorna o percentual de conclusão da meta"""
        if self.valor_objetivo > 0:
            return (self.valor_atual / self.valor_objetivo) * 100
        return 0
    
    @property
    def valor_restante(self):
        """Quanto ainda falta para alcançar a meta"""
        return max(0, self.valor_objetivo - self.valor_atual)
    
    @property
    def dias_restantes(self):
        """Quantos dias faltam para o prazo"""
        from django.utils import timezone
        if self.data_prazo:
            delta = self.data_prazo - timezone.now().date()
            return max(0, delta.days)
        return 0
    
    @property
    def valor_diario_necessario(self):
        """Quanto precisa economizar por dia para alcançar a meta"""
        dias = self.dias_restantes
        if dias > 0 and self.valor_restante > 0:
            return self.valor_restante / dias
        return 0
    
    @property
    def status_progresso(self):
        """Retorna o status do progresso (no prazo, atrasado, etc)"""
        percentual = self.percentual_concluido
        dias_restantes = self.dias_restantes
        
        if percentual >= 100:
            return {'status': 'concluida', 'cor': 'success', 'icone': '🏆'}
        elif dias_restantes <= 0:
            return {'status': 'atrasada', 'cor': 'danger', 'icone': '⚠️'}
        elif percentual >= 75:
            return {'status': 'quase_la', 'cor': 'success', 'icone': '🎯'}
        elif percentual >= 50:
            return {'status': 'no_prazo', 'cor': 'info', 'icone': '📈'}
        elif percentual >= 25:
            return {'status': 'inicio', 'cor': 'warning', 'icone': '🟡'}
        else:
            return {'status': 'muito_atrasada', 'cor': 'danger', 'icone': '🔴'}
    
    def adicionar_progresso(self, valor):
        """Adiciona valor ao progresso da meta"""
        self.valor_atual += valor
        if self.valor_atual >= self.valor_objetivo:
            self.status = 'concluida'
            from decimal import Decimal
            self.valor_atual += Decimal(str(valor))
            # Adicionar conquista
            if 'primeira_meta' not in self.conquistas:
                self.conquistas.append('primeira_meta')
        self.save()
    
    def get_sugestoes_ia(self):
        """Retorna sugestões da IA para alcançar a meta"""
        sugestoes = []
        percentual = self.percentual_concluido
        dias_restantes = self.dias_restantes
        valor_diario = self.valor_diario_necessario
        
        if percentual < 25 and dias_restantes > 30:
            sugestoes.append({
                'tipo': 'urgente',
                'icone': '🚨',
                'titulo': 'Acelere o ritmo!',
                'descricao': f'Você precisa economizar R$ {valor_diario:.2f} por dia para alcançar sua meta.'
            })
        elif percentual >= 75:
            sugestoes.append({
                'tipo': 'sucesso',
                'icone': '🎉',
                'titulo': 'Quase lá!',
                'descricao': f'Faltam apenas R$ {self.valor_restante:.2f} para sua meta!'
            })
        
        return sugestoes