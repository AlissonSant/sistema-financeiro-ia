# finance/ai_engine.py
"""
🤖 FLUX AI ENGINE - Sistema de Inteligência Artificial
Desenvolvido para análise preditiva e insights financeiros
"""

from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json
from .models import Transacao, MetaFinanceira


class FluxAIEngine:
    """
    🧠 Motor principal de IA do FLUX Finance
    Responsável por análises preditivas e insights inteligentes
    """
    
    def __init__(self, usuario):
        self.usuario = usuario
        self.transacoes = Transacao.objects.filter(usuario=usuario)
        self.metas = MetaFinanceira.objects.filter(usuario=usuario)
        
    def analisar_padroes_gastos(self):
        """
        📊 Analisa padrões de gastos do usuário
        Retorna insights sobre comportamento financeiro
        """
        print(f"🔍 Analisando padrões para {self.usuario.username}...")
        
        # Últimos 30 dias
        data_inicio = timezone.now().date() - timedelta(days=30)
        transacoes_recentes = self.transacoes.filter(
            data__gte=data_inicio,
            tipo='despesa'
        )
        
        if not transacoes_recentes.exists():
            return {
                'status': 'sem_dados',
                'message': 'Não há dados suficientes para análise'
            }
        
        # 📊 ANÁLISES BÁSICAS
        total_gastos = transacoes_recentes.aggregate(Sum('valor'))['valor__sum'] or 0
        media_diaria = total_gastos / 30
        
        # 📈 GASTOS POR CATEGORIA
        gastos_categoria = transacoes_recentes.values('categoria').annotate(
            total=Sum('valor')
        ).order_by('-total')
        
        # 🎯 CATEGORIA DOMINANTE
        categoria_principal = gastos_categoria.first() if gastos_categoria else None
        
        # 📅 PADRÃO SEMANAL
        padroes_semana = self._analisar_padroes_semanais(transacoes_recentes)
        
        # 🚨 DETECÇÃO DE ANOMALIAS
        anomalias = self._detectar_anomalias(transacoes_recentes)
        
        resultado = {
            'status': 'sucesso',
            'periodo_analise': '30 dias',
            'total_transacoes': transacoes_recentes.count(),
            'total_gastos': float(total_gastos),
            'media_diaria': float(media_diaria),
            'categoria_principal': {
                'nome': categoria_principal['categoria'] if categoria_principal else 'N/A',
                'valor': float(categoria_principal['total']) if categoria_principal else 0,
                'percentual': (float(categoria_principal['total']) / float(total_gastos) * 100) if categoria_principal and total_gastos > 0 else 0
            },
            'gastos_por_categoria': list(gastos_categoria),
            'padroes_semana': padroes_semana,
            'anomalias': anomalias,
            'timestamp': timezone.now().isoformat()
        }
        
        print(f"✅ Análise concluída! {transacoes_recentes.count()} transações processadas")
        return resultado
    
    def _analisar_padroes_semanais(self, transacoes):
        """📅 Analisa padrões por dia da semana"""
        padroes = {}
        
        for transacao in transacoes:
            dia_semana = transacao.data.strftime('%A')  # Nome do dia em inglês
            if dia_semana not in padroes:
                padroes[dia_semana] = {'count': 0, 'total': 0}
            
            padroes[dia_semana]['count'] += 1
            padroes[dia_semana]['total'] += float(transacao.valor)
        
        # Calcular médias
        for dia in padroes:
            if padroes[dia]['count'] > 0:
                padroes[dia]['media'] = padroes[dia]['total'] / padroes[dia]['count']
            else:
                padroes[dia]['media'] = 0
                
        return padroes
    
    def _detectar_anomalias(self, transacoes):
        """🚨 Detecta gastos anômalos (muito acima da média)"""
        if not transacoes.exists():
            return []
            
        # Calcular média e desvio
        valores = [float(t.valor) for t in transacoes]
        media = sum(valores) / len(valores)
        
        # Gastos 3x acima da média são considerados anômalos
        threshold = media * 3
        
        anomalias = []
        for transacao in transacoes:
            if float(transacao.valor) > threshold:
                anomalias.append({
                    'data': transacao.data.strftime('%d/%m/%Y'),
                    'descricao': transacao.descricao,
                    'valor': float(transacao.valor),
                    'categoria': transacao.categoria,
                    'desvio_percentual': ((float(transacao.valor) - media) / media * 100)
                })
        
        return anomalias[:5]  # Retorna apenas as 5 maiores anomalias
    
    def prever_gastos_futuros(self, dias=30):
        """
        🔮 Prevê gastos futuros baseado em padrões históricos
        """
        print(f"🔮 Prevendo gastos para os próximos {dias} dias...")
        
        # Últimos 60 dias para análise
        data_inicio = timezone.now().date() - timedelta(days=60)
        transacoes_historicas = self.transacoes.filter(
            data__gte=data_inicio,
            tipo='despesa'
        )
        
        if not transacoes_historicas.exists():
            return {
                'status': 'sem_dados',
                'message': 'Histórico insuficiente para previsões'
            }
        
        # 📊 CÁLCULOS PREDITIVOS
        total_historico = transacoes_historicas.aggregate(Sum('valor'))['valor__sum'] or 0
        media_diaria_historica = total_historico / 60
        
        # 📈 TENDÊNCIA (crescimento ou redução)
        primeira_metade = transacoes_historicas.filter(
            data__gte=data_inicio,
            data__lt=data_inicio + timedelta(days=30)
        ).aggregate(Sum('valor'))['valor__sum'] or 0
        
        segunda_metade = transacoes_historicas.filter(
            data__gte=data_inicio + timedelta(days=30)
        ).aggregate(Sum('valor'))['valor__sum'] or 0
        
        if primeira_metade > 0:
            tendencia_percentual = ((segunda_metade - primeira_metade) / primeira_metade) * 100
        else:
            tendencia_percentual = 0
        
        # 🎯 PREVISÃO AJUSTADA PELA TENDÊNCIA
        previsao_base = media_diaria_historica * dias
        ajuste_tendencia = previsao_base * (tendencia_percentual / 100)
        previsao_final = previsao_base + ajuste_tendencia
        
        # 📊 PREVISÃO POR CATEGORIA
        previsoes_categoria = self._prever_por_categoria(transacoes_historicas, dias)
        
        resultado = {
            'status': 'sucesso',
            'dias_previsao': dias,
            'media_diaria_historica': float(media_diaria_historica),
            'tendencia_percentual': round(tendencia_percentual, 2),
            'previsao_total': float(previsao_final),
            'previsao_por_categoria': previsoes_categoria,
            'confianca': self._calcular_confianca(transacoes_historicas),
            'timestamp': timezone.now().isoformat()
        }
        
        print(f"✅ Previsão concluída! Estimativa: R$ {previsao_final:.2f}")
        return resultado
    
    def _prever_por_categoria(self, transacoes, dias):
        """📊 Previsão específica por categoria"""
        categorias = transacoes.values('categoria').annotate(
            total=Sum('valor'),
            count=Count('id')
        )
        
        previsoes = []
        for categoria in categorias:
            media_diaria_cat = categoria['total'] / 60  # Base nos últimos 60 dias
            previsao_cat = media_diaria_cat * dias
            
            previsoes.append({
                'categoria': categoria['categoria'],
                'previsao': float(previsao_cat),
                'media_diaria': float(media_diaria_cat),
                'frequencia_historica': categoria['count']
            })
        
        return sorted(previsoes, key=lambda x: x['previsao'], reverse=True)
    
    def _calcular_confianca(self, transacoes):
        """📈 Calcula nível de confiança da previsão"""
        if transacoes.count() < 10:
            return 'baixa'
        elif transacoes.count() < 30:
            return 'media'
        else:
            return 'alta'
    
    def gerar_alertas_inteligentes(self):
        """
        🚨 Gera alertas baseados em padrões e anomalias
        """
        print(f"🚨 Gerando alertas inteligentes...")
        
        alertas = []
        
        # 1. ANÁLISE DE PADRÕES
        padroes = self.analisar_padroes_gastos()
        if padroes['status'] == 'sucesso':
            
            # 🔥 ALERTA: Categoria dominante
            if padroes['categoria_principal']['percentual'] > 50:
                alertas.append({
                    'tipo': 'warning',
                    'prioridade': 'alta',
                    'icone': '⚠️',
                    'titulo': 'Concentração de Gastos',
                    'descricao': f"Você está gastando {padroes['categoria_principal']['percentual']:.1f}% do seu orçamento em {padroes['categoria_principal']['nome']}",
                    'acao': 'Considere diversificar seus gastos para maior controle financeiro'
                })
            
            # 💸 ALERTA: Gastos acima da média
            if padroes['media_diaria'] > 100:  # R$ 100/dia
                alertas.append({
                    'tipo': 'danger',
                    'prioridade': 'urgente',
                    'icone': '💸',
                    'titulo': 'Gastos Elevados',
                    'descricao': f"Sua média diária de gastos é R$ {padroes['media_diaria']:.2f}",
                    'acao': 'Revise seus gastos e estabeleça um limite diário'
                })
            
            # 🎯 ALERTA: Anomalias detectadas
            if padroes['anomalias']:
                alertas.append({
                    'tipo': 'info',
                    'prioridade': 'media',
                    'icone': '🔍',
                    'titulo': 'Gastos Anômalos Detectados',
                    'descricao': f"Encontramos {len(padroes['anomalias'])} gastos fora do padrão",
                    'acao': 'Verifique se esses gastos eram planejados'
                })
        
        # 2. ANÁLISE DE METAS
        alertas_metas = self._gerar_alertas_metas()
        alertas.extend(alertas_metas)
        
        # 3. PREVISÕES
        previsoes = self.prever_gastos_futuros(30)
        if previsoes['status'] == 'sucesso':
            if previsoes['tendencia_percentual'] > 20:
                alertas.append({
                    'tipo': 'warning',
                    'prioridade': 'alta',
                    'icone': '📈',
                    'titulo': 'Tendência de Aumento',
                    'descricao': f"Seus gastos aumentaram {previsoes['tendencia_percentual']:.1f}% recentemente",
                    'acao': 'Monitore seus gastos para evitar surpresas no orçamento'
                })
        
        print(f"✅ {len(alertas)} alertas gerados!")
        return alertas
    
    def _gerar_alertas_metas(self):
        """🎯 Alertas específicos para metas"""
        alertas = []
        
        for meta in self.metas.filter(status='ativa'):
            # Meta próxima do prazo
            if meta.dias_restantes <= 30 and meta.percentual_concluido < 80:
                alertas.append({
                    'tipo': 'warning',
                    'prioridade': 'alta',
                    'icone': '⏰',
                    'titulo': f'Meta "{meta.titulo}" Urgente',
                    'descricao': f'Faltam apenas {meta.dias_restantes} dias e você está {meta.percentual_concluido:.1f}% completo',
                    'acao': f'Acelere o ritmo! Economize R$ {meta.valor_diario_necessario:.2f} por dia'
                })
            
            # Meta quase concluída
            elif meta.percentual_concluido >= 90:
                alertas.append({
                    'tipo': 'success',
                    'prioridade': 'baixa',
                    'icone': '🏆',
                    'titulo': f'Meta "{meta.titulo}" Quase Concluída!',
                    'descricao': f'Você está a {100 - meta.percentual_concluido:.1f}% de conquistar sua meta!',
                    'acao': f'Continue assim! Faltam apenas R$ {meta.valor_restante:.2f}'
                })
        
        return alertas
    
    def calcular_score_financeiro(self):
        """
        📊 Calcula score de saúde financeira (0-100)
        """
        print(f"📊 Calculando score financeiro...")
        
        score = 0
        detalhes = []
        
        # 1. CONSISTÊNCIA DE DADOS (20 pontos)
        if self.transacoes.count() >= 30:
            score += 20
            detalhes.append("✅ Dados suficientes para análise (+20)")
        elif self.transacoes.count() >= 10:
            score += 10
            detalhes.append("⚠️ Dados parciais para análise (+10)")
        else:
            detalhes.append("❌ Poucos dados para análise confiável (0)")
        
        # 2. CONTROLE DE GASTOS (30 pontos)
        padroes = self.analisar_padroes_gastos()
        if padroes['status'] == 'sucesso':
            if len(padroes['anomalias']) == 0:
                score += 30
                detalhes.append("✅ Gastos sob controle (+30)")
            elif len(padroes['anomalias']) <= 2:
                score += 20
                detalhes.append("⚠️ Alguns gastos fora do padrão (+20)")
            else:
                score += 10
                detalhes.append("❌ Muitos gastos anômalos (+10)")
        
        # 3. DIVERSIFICAÇÃO (20 pontos)
        if padroes['status'] == 'sucesso':
            if padroes['categoria_principal']['percentual'] < 40:
                score += 20
                detalhes.append("✅ Gastos bem diversificados (+20)")
            elif padroes['categoria_principal']['percentual'] < 60:
                score += 10
                detalhes.append("⚠️ Gastos moderadamente concentrados (+10)")
            else:
                detalhes.append("❌ Gastos muito concentrados em uma categoria (0)")
        
        # 4. METAS ATIVAS (30 pontos)
        metas_ativas = self.metas.filter(status='ativa').count()
        if metas_ativas >= 3:
            score += 30
            detalhes.append("✅ Múltiplas metas ativas (+30)")
        elif metas_ativas >= 1:
            score += 20
            detalhes.append("✅ Pelo menos uma meta ativa (+20)")
        else:
            detalhes.append("❌ Nenhuma meta ativa (0)")
        
        # 5. CONCLUSÃO DE METAS (bônus até 10 pontos)
        metas_concluidas = self.metas.filter(status='concluida').count()
        bonus_metas = min(10, metas_concluidas * 2)
        score += bonus_metas
        if bonus_metas > 0:
            detalhes.append(f"🏆 Bônus por metas concluídas (+{bonus_metas})")
        
        # Garantir que o score não passe de 100
        score = min(100, score)
        
        # Determinar classificação
        if score >= 80:
            classificacao = "🏆 Excelente"
            cor = "success"
        elif score >= 60:
            classificacao = "✅ Bom"
            cor = "info"
        elif score >= 40:
            classificacao = "⚠️ Regular"
            cor = "warning"
        else:
            classificacao = "❌ Precisa Melhorar"
            cor = "danger"
        
        resultado = {
            'score': score,
            'classificacao': classificacao,
            'cor': cor,
            'detalhes': detalhes,
            'sugestoes': self._gerar_sugestoes_score(score),
            'timestamp': timezone.now().isoformat()
        }
        
        print(f"✅ Score calculado: {score}/100 ({classificacao})")
        return resultado
    
    def _gerar_sugestoes_score(self, score):
        """💡 Gera sugestões para melhorar o score"""
        sugestoes = []
        
        if score < 40:
            sugestoes = [
                "📊 Registre mais transações para melhor análise",
                "🎯 Crie metas financeiras claras",
                "💰 Monitore gastos anômalos regularmente",
                "📈 Diversifique suas categorias de gastos"
            ]
        elif score < 60:
            sugestoes = [
                "🎯 Adicione mais metas para melhorar planejamento",
                "📊 Mantenha consistência nos registros",
                "💡 Analise padrões de gastos semanalmente"
            ]
        elif score < 80:
            sugestoes = [
                "🏆 Continue mantendo o bom trabalho!",
                "📈 Considere metas de longo prazo",
                "💰 Monitore tendências mensais"
            ]
        else:
            sugestoes = [
                "🌟 Parabéns! Você tem excelente controle financeiro!",
                "🚀 Considere investimentos mais avançados",
                "📚 Compartilhe suas estratégias com outros"
            ]
        
        return sugestoes


class FluxAIInsights:
    """
    💡 Gerador de insights inteligentes para o dashboard
    """
    
    def __init__(self, usuario):
        self.ai_engine = FluxAIEngine(usuario)
        self.usuario = usuario
    
    def get_insights_dashboard(self):
        """📊 Retorna insights para o dashboard principal"""
        print(f"💡 Gerando insights para dashboard...")
        
        insights = []
        
        # 1. SCORE FINANCEIRO
        score = self.ai_engine.calcular_score_financeiro()
        insights.append({
            'tipo': 'score',
            'icone': '📊',
            'titulo': f'Score Financeiro: {score["score"]}/100',
            'descricao': score['classificacao'],
            'cor': score['cor'],
            'detalhes': score['detalhes'][:2]  # Primeiros 2 detalhes
        })
        
        # 2. PADRÕES DE GASTOS
        padroes = self.ai_engine.analisar_padroes_gastos()
        if padroes['status'] == 'sucesso':
            insights.append({
                'tipo': 'padroes',
                'icone': '📈',
                'titulo': 'Análise de Padrões',
                'descricao': f"Categoria principal: {padroes['categoria_principal']['nome']} ({padroes['categoria_principal']['percentual']:.1f}%)",
                'cor': 'info',
                'valor_destaque': f"R$ {padroes['media_diaria']:.2f}/dia"
            })
        
        # 3. PREVISÕES
        previsoes = self.ai_engine.prever_gastos_futuros(30)
        if previsoes['status'] == 'sucesso':
            insights.append({
                'tipo': 'previsao',
                'icone': '🔮',
                'titulo': 'Previsão 30 Dias',
                'descricao': f"Estimativa baseada em padrões históricos",
                'cor': 'warning' if previsoes['tendencia_percentual'] > 10 else 'success',
                'valor_destaque': f"R$ {previsoes['previsao_total']:.2f}"
            })
        
        # 4. ALERTAS RESUMO
        alertas = self.ai_engine.gerar_alertas_inteligentes()
        alertas_urgentes = [a for a in alertas if a['prioridade'] == 'urgente']
        if alertas_urgentes:
            insights.append({
                'tipo': 'alertas',
                'icone': '🚨',
                'titulo': f'{len(alertas_urgentes)} Alerta(s) Urgente(s)',
                'descricao': alertas_urgentes[0]['titulo'],
                'cor': 'danger',
                'acao': 'Ver todos os alertas'
            })
        
        print(f"✅ {len(insights)} insights gerados!")
        return insights


# 🎯 FUNÇÃO AUXILIAR PARA TESTES
def testar_ia_engine(usuario):
    """🧪 Função para testar todas as funcionalidades da IA"""
    print(f"\n🧪 TESTANDO IA ENGINE PARA {usuario.username}")
    print("=" * 50)
    
    ai = FluxAIEngine(usuario)
    
    # Teste 1: Padrões
    print("\n1️⃣ TESTANDO ANÁLISE DE PADRÕES...")
    padroes = ai.analisar_padroes_gastos()
    print(f"Status: {padroes['status']}")
    
    # Teste 2: Previsões
    print("\n2️⃣ TESTANDO PREVISÕES...")
    previsoes = ai.prever_gastos_futuros(30)
    print(f"Status: {previsoes['status']}")
    
    # Teste 3: Alertas
    print("\n3️⃣ TESTANDO ALERTAS...")
    alertas = ai.gerar_alertas_inteligentes()
    print(f"Alertas gerados: {len(alertas)}")
    
    # Teste 4: Score
    print("\n4️⃣ TESTANDO SCORE...")
    score = ai.calcular_score_financeiro()
    print(f"Score: {score['score']}/100")
    
    print("\n✅ TODOS OS TESTES CONCLUÍDOS!")
    return True