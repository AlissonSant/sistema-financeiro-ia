from django.core.management.base import BaseCommand
from finance.models import Transacao, MetaFinanceira
from django.contrib.auth.models import User
from decimal import Decimal
import random
from datetime import datetime, timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Popula o banco com dados realistas para os gráficos'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando população de dados...'))
        
        # Pegar o usuário atual (você)
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('❌ Nenhum usuário encontrado!'))
            return
            
        self.stdout.write(f'👤 Populando dados para: {user.username}')
        
        # Limpar dados antigos para evitar duplicação
        Transacao.objects.filter(usuario=user).delete()
        MetaFinanceira.objects.filter(usuario=user).delete()
        
        # Dados realistas
        categorias_gastos = [
            'alimentacao', 'transporte', 'lazer', 'saude', 'educacao',
            'casa', 'outros'
        ]
        
        categorias_receitas = [
            'outros'  # Todas as receitas como 'outros' pois é o que existe no model
        ]
        
        descricoes_gastos = {
            'alimentacao': ['Almoço no restaurante', 'Lanche da tarde', 'Jantar', 'Delivery'],
            'transporte': ['Combustível', 'Uber', 'Ônibus', 'Estacionamento'],
            'lazer': ['Cinema', 'Streaming', 'Balada', 'Livros'],
            'saude': ['Consulta médica', 'Medicamentos', 'Academia', 'Dentista'],
            'educacao': ['Curso online', 'Livros', 'Material escolar', 'Certificação'],
            'casa': ['Aluguel', 'Luz', 'Água', 'Internet'],
            'outros': ['Roupas', 'Tecnologia', 'Supermercado', 'Farmácia']
        }
        
        descricoes_receitas = {
            'outros': ['Salário mensal', 'Freelance', 'Vendas', 'Investimentos', 'Presente']
        }
        
        # Criar transações dos últimos 90 dias
        hoje = timezone.now().date()
        
        for i in range(120):  # 120 transações
            # 70% gastos, 30% receitas (mais realista)
            if random.random() < 0.7:
                # GASTO
                categoria = random.choice(categorias_gastos)
                descricao = random.choice(descricoes_gastos[categoria])
                
                # Valores mais realistas por categoria
                if categoria in ['casa']:
                    valor = Decimal(random.uniform(800, 2000))
                elif categoria in ['saude', 'educacao']:
                    valor = Decimal(random.uniform(50, 400))
                elif categoria == 'alimentacao':
                    valor = Decimal(random.uniform(15, 80))
                elif categoria == 'transporte':
                    valor = Decimal(random.uniform(10, 150))
                else:
                    valor = Decimal(random.uniform(20, 300))
                
                tipo = 'despesa'
            else:
                # RECEITA
                categoria = random.choice(categorias_receitas)
                descricao = random.choice(descricoes_receitas[categoria])
                
                if categoria == 'outros':
                    valor = Decimal(random.uniform(2000, 5000))
                else:
                    valor = Decimal(random.uniform(50, 800))
                
                tipo = 'receita'
            
            # Data aleatória nos últimos 90 dias
            data_transacao = hoje - timedelta(days=random.randint(0, 90))
            
            Transacao.objects.create(
                usuario=user,
                tipo=tipo,
                categoria=categoria,
                valor=valor,
                descricao=descricao,
                data=timezone.make_aware(datetime.combine(data_transacao, datetime.min.time()))
            )
        
        # Criar algumas metas financeiras
        metas = [
            {
                'titulo': 'Viagem de Férias',
                'descricao': 'Economizar para uma viagem dos sonhos',
                'tipo': 'economia',
                'valor_objetivo': Decimal('3000.00'),
                'valor_atual': Decimal('1200.00')
            },
            {
                'titulo': 'Reserva de Emergência',
                'descricao': 'Criar uma reserva para emergências',
                'tipo': 'economia',
                'valor_objetivo': Decimal('10000.00'),
                'valor_atual': Decimal('4500.00')
            },
            {
                'titulo': 'Curso de Especialização',
                'descricao': 'Investir em qualificação profissional',
                'tipo': 'investimento',
                'valor_objetivo': Decimal('2500.00'),
                'valor_atual': Decimal('800.00')
            },
            {
                'titulo': 'Novo Notebook',
                'descricao': 'Comprar um notebook para programação',
                'tipo': 'compra',
                'valor_objetivo': Decimal('4000.00'),
                'valor_atual': Decimal('1500.00')
            }
        ]
        
        for meta in metas:
            MetaFinanceira.objects.create(
                usuario=user,
                titulo=meta['titulo'],
                descricao=meta['descricao'],
                tipo=meta['tipo'],
                valor_objetivo=meta['valor_objetivo'],
                valor_atual=meta['valor_atual'],
                data_prazo=hoje + timedelta(days=random.randint(30, 365))
            )
        
        # Estatísticas finais
        total_transacoes = Transacao.objects.filter(usuario=user).count()
        total_metas = MetaFinanceira.objects.filter(usuario=user).count()
        
        self.stdout.write(self.style.SUCCESS(f'✅ Sucesso!'))
        self.stdout.write(self.style.SUCCESS(f'📊 {total_transacoes} transações criadas'))
        self.stdout.write(self.style.SUCCESS(f'🎯 {total_metas} metas criadas'))
        self.stdout.write(self.style.SUCCESS('🎉 Agora seus gráficos vão aparecer lindos!'))