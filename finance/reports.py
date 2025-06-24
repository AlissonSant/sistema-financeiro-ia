# finance/reports.py - SISTEMA DE RELATÓRIOS PROFISSIONAIS
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.colors import Color, blue, green, red, orange
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from django.http import HttpResponse
from django.db.models import Sum
from datetime import datetime, timedelta
from .models import Transacao, MetaFinanceira
from .alerts import AlertasInteligentes
import io

class RelatorioFinanceiro:
    """Gerador de relatórios profissionais em PDF"""
    
    def __init__(self, usuario):
        self.usuario = usuario
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configurar estilos personalizados"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='TituloFintech',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=Color(0.4, 0.49, 0.91),  # Azul fintech
            spaceAfter=30,
            alignment=1  # Centralizado
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='SubtituloFintech',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=Color(0.3, 0.3, 0.3),
            spaceAfter=20
        ))
        
        # Texto com destaque
        self.styles.add(ParagraphStyle(
            name='Destaque',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=Color(0.2, 0.2, 0.8),
            fontName='Helvetica-Bold'
        ))
    
    def gerar_relatorio_completo(self):
        """Gera relatório completo do usuário"""
        # Configurar resposta HTTP
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="relatorio_financeiro_{datetime.now().strftime("%Y%m%d")}.pdf"'
        
        # Criar documento PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Construir conteúdo
        story = []
        story.extend(self._cabecalho())
        story.extend(self._resumo_executivo())
        story.extend(self._analise_transacoes())
        story.extend(self._status_metas())
        story.extend(self._alertas_ia())
        story.extend(self._recomendacoes())
        story.extend(self._rodape())
        
        # Gerar PDF
        doc.build(story)
        pdf_value = buffer.getvalue()
        buffer.close()
        
        response.write(pdf_value)
        return response
    
    def _cabecalho(self):
        """Cabeçalho do relatório"""
        story = []
        
        # Título principal
        titulo = Paragraph("🏦 RELATÓRIO FINANCEIRO INTELIGENTE", self.styles['TituloFintech'])
        story.append(titulo)
        
        # Informações do usuário
        info_usuario = f"""
        <b>Usuário:</b> {self.usuario.first_name or self.usuario.username}<br/>
        <b>Data:</b> {datetime.now().strftime('%d/%m/%Y às %H:%M')}<br/>
        <b>Período:</b> Últimos 30 dias<br/>
        <b>Sistema:</b> IA Financeiro v1.0
        """
        story.append(Paragraph(info_usuario, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        return story
    
    def _resumo_executivo(self):
        """Resumo executivo com números principais"""
        story = []
        
        story.append(Paragraph("📊 RESUMO EXECUTIVO", self.styles['SubtituloFintech']))
        
        # Calcular dados
        receitas = Transacao.objects.filter(usuario=self.usuario, tipo='receita').aggregate(Sum('valor'))['valor__sum'] or 0
        despesas = Transacao.objects.filter(usuario=self.usuario, tipo='despesa').aggregate(Sum('valor'))['valor__sum'] or 0
        saldo = receitas - despesas
        
        # Metas
        total_metas = MetaFinanceira.objects.filter(usuario=self.usuario).count()
        metas_ativas = MetaFinanceira.objects.filter(usuario=self.usuario, status='ativa').count()
        metas_concluidas = MetaFinanceira.objects.filter(usuario=self.usuario, status='concluida').count()
        
        # Tabela de resumo
        dados_resumo = [
            ['MÉTRICA', 'VALOR', 'STATUS'],
            ['💰 Total Receitas', f'R$ {receitas:,.2f}', '✅ Positivo'],
            ['💸 Total Despesas', f'R$ {despesas:,.2f}', '⚠️ Monitorar'],
            ['💳 Saldo Atual', f'R$ {saldo:,.2f}', '✅ Positivo' if saldo >= 0 else '🚨 Negativo'],
            ['🎯 Metas Totais', str(total_metas), '📊 Tracking'],
            ['🎯 Metas Ativas', str(metas_ativas), '🔥 Em Progresso'],
            ['🏆 Metas Concluídas', str(metas_concluidas), '✅ Sucesso']
        ]
        
        tabela = Table(dados_resumo, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(tabela)
        story.append(Spacer(1, 20))
        
        return story
    
    def _analise_transacoes(self):
        """Análise detalhada das transações"""
        story = []
        
        story.append(Paragraph("📈 ANÁLISE DE TRANSAÇÕES", self.styles['SubtituloFintech']))
        
        # Gastos por categoria
        gastos_categoria = Transacao.objects.filter(
            usuario=self.usuario, 
            tipo='despesa'
        ).values('categoria').annotate(total=Sum('valor')).order_by('-total')[:5]
        
        if gastos_categoria:
            story.append(Paragraph("<b>🏷️ Top 5 Categorias de Gastos:</b>", self.styles['Destaque']))
            
            dados_categoria = [['CATEGORIA', 'VALOR', '% DO TOTAL']]
            total_gastos = sum([item['total'] for item in gastos_categoria])
            
            for item in gastos_categoria:
                categoria = dict(Transacao.CATEGORIAS).get(item['categoria'], item['categoria'])
                valor = item['total']
                percentual = (valor / total_gastos * 100) if total_gastos > 0 else 0
                dados_categoria.append([categoria, f'R$ {valor:,.2f}', f'{percentual:.1f}%'])
            
            tabela_cat = Table(dados_categoria, colWidths=[2*inch, 1.5*inch, 1*inch])
            tabela_cat.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue)
            ]))
            
            story.append(tabela_cat)
            story.append(Spacer(1, 20))
        
        return story
    
    def _status_metas(self):
        """Status das metas financeiras"""
        story = []
        
        story.append(Paragraph("🎯 STATUS DAS METAS", self.styles['SubtituloFintech']))
        
        metas = MetaFinanceira.objects.filter(usuario=self.usuario).order_by('-data_criacao')[:5]
        
        if metas:
            dados_metas = [['META', 'PROGRESSO', 'VALOR', 'STATUS', 'PRAZO']]
            
            for meta in metas:
                progresso = f"{meta.percentual_concluido:.1f}%"
                valor_atual = f"R$ {meta.valor_atual:,.2f}"
                status_icon = "🏆" if meta.status == 'concluida' else "🎯" if meta.status == 'ativa' else "⏸️"
                dias_restantes = f"{meta.dias_restantes} dias"
                
                dados_metas.append([
                    meta.titulo[:20] + "..." if len(meta.titulo) > 20 else meta.titulo,
                    progresso,
                    valor_atual,
                    f"{status_icon} {meta.get_status_display()}",
                    dias_restantes
                ])
            
            tabela_metas = Table(dados_metas, colWidths=[2*inch, 0.8*inch, 1*inch, 1*inch, 0.8*inch])
            tabela_metas.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen)
            ]))
            
            story.append(tabela_metas)
            story.append(Spacer(1, 20))
        else:
            story.append(Paragraph("ℹ️ Nenhuma meta cadastrada ainda.", self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        return story
    
    def _alertas_ia(self):
        """Alertas e insights da IA"""
        story = []
        
        story.append(Paragraph("🤖 INSIGHTS DA INTELIGÊNCIA ARTIFICIAL", self.styles['SubtituloFintech']))
        
        # Gerar alertas
        sistema_alertas = AlertasInteligentes(self.usuario)
        alertas = sistema_alertas.gerar_todos_alertas()
        
        if alertas:
            for alerta in alertas[:3]:  # Top 3 alertas
                texto_alerta = f"""
                <b>{alerta['icone']} {alerta['titulo']}</b><br/>
                {alerta['descricao']}<br/>
                <i>💡 Recomendação: {alerta['acao']}</i>
                """
                story.append(Paragraph(texto_alerta, self.styles['Normal']))
                story.append(Spacer(1, 10))
        else:
            story.append(Paragraph("✅ Parabéns! Suas finanças estão em ordem. Continue assim!", self.styles['Destaque']))
        
        story.append(Spacer(1, 20))
        return story
    
    def _recomendacoes(self):
        """Recomendações personalizadas"""
        story = []
        
        story.append(Paragraph("💡 RECOMENDAÇÕES PERSONALIZADAS", self.styles['SubtituloFintech']))
        
        recomendacoes = [
            "📊 <b>Diversificação:</b> Considere distribuir seus investimentos em diferentes categorias.",
            "🎯 <b>Metas SMART:</b> Defina metas específicas, mensuráveis e com prazos realistas.",
            "📱 <b>Automação:</b> Configure alertas para acompanhar seu progresso automaticamente.",
            "💰 <b>Reserva de Emergência:</b> Mantenha 6 meses de despesas guardados para imprevistos.",
            "📈 <b>Revisão Mensal:</b> Analise seus gastos mensalmente para identificar oportunidades."
        ]
        
        for rec in recomendacoes:
            story.append(Paragraph(rec, self.styles['Normal']))
            story.append(Spacer(1, 8))
        
        story.append(Spacer(1, 20))
        return story
    
    def _rodape(self):
        """Rodapé do relatório"""
        story = []
        
        rodape = """
        <br/><br/>
        <i>Relatório gerado automaticamente pelo Sistema IA Financeiro.<br/>
        Este documento contém informações confidenciais do usuário.<br/>
        © 2025 - IA Financeiro - Tecnologia Brasileira 🇧🇷</i>
        """
        
        story.append(Paragraph(rodape, self.styles['Normal']))
        return story