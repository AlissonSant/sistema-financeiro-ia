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