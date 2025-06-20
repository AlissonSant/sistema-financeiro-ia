from django import forms
from .models import Transacao

class TransacaoForm(forms.ModelForm):
    class Meta:
        model = Transacao
        fields = ['descricao', 'valor', 'tipo', 'categoria']
        widgets = {
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Supermercado Pão de Açúcar'
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'descricao': '📝 Descrição',
            'valor': '💰 Valor (R$)',
            'tipo': '📊 Tipo',
            'categoria': '🏷️ Categoria',
        }