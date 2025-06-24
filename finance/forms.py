from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Transacao
from .models import MetaFinanceira
from django.utils import timezone


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label="Nome")
    
    class Meta:
        model = User
        fields = ("username", "first_name", "email", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Estilizar campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        # Customizar labels
        self.fields['username'].label = "Nome de usuário"
        self.fields['password1'].label = "Senha"
        self.fields['password2'].label = "Confirmar senha"

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
        
# Formulario para metas financeiras
class MetaFinanceiraForm(forms.ModelForm):
    class Meta:
        model = MetaFinanceira
        fields = ['titulo', 'descricao', 'tipo', 'valor_objetivo', 'data_prazo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Viagem para Europa, Comprar carro...',
                'maxlength': 200
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descreva sua meta em detalhes (opcional)',
                'rows': 3
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'valor_objetivo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '1'
            }),
            'data_prazo': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().strftime('%Y-%m-%d')
            })
        }
        labels = {
            'titulo': '🎯 Título da Meta',
            'descricao': '📝 Descrição',
            'tipo': '📂 Tipo de Meta',
            'valor_objetivo': '💰 Valor Objetivo (R$)',
            'data_prazo': '📅 Data Limite'
        }

class ProgressoMetaForm(forms.Form):
    """Formulário para adicionar progresso a uma meta"""
    valor = forms.DecimalField(
        label='💸 Valor a Adicionar (R$)',
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01'
        })
    )
    descricao = forms.CharField(
        label='📝 Descrição (opcional)',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Economia do mês, vendeu item...'
        })
    )        