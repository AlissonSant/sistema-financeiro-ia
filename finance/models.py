from django.db import models
from django.utils import timezone

class Transacao(models.Model):
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
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"