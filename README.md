# 🏦 Sistema Financeiro com IA

Sistema web para controle financeiro pessoal desenvolvido em Django.

## 📸 Preview

Dashboard com controle completo de receitas e despesas, interface moderna e responsiva.

## ⚡ Funcionalidades

- [✅] **Dashboard Financeiro** - Visão geral com totais e saldo
- [✅] **Gestão de Transações** - Receitas e despesas categorizadas  
- [✅] **Painel Administrativo** - Interface completa para gerenciar dados
- [✅] **Design Responsivo** - Funciona em desktop e mobile
- [✅] **Categorização** - Organize gastos por categoria (alimentação, transporte, etc.)

## 🛠️ Tecnologias

- **Backend:** Django 5.2.3
- **Frontend:** HTML5, CSS3 (design moderno)
- **Banco de dados:** SQLite
- **Python:** 3.13

## 🚀 Como rodar o projeto

### Pré-requisitos
- Python 3.8+
- pip

### Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/SEU_USUARIO/sistema-financeiro-ia.git
cd sistema-financeiro-ia
```

2. **Crie e ative o ambiente virtual**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

3. **Instale as dependências**
```bash
pip install django
```

4. **Execute as migrações**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Crie um superusuário**
```bash
python manage.py createsuperuser
```

6. **Rode o servidor**
```bash
python manage.py runserver
```

7. **Acesse o sistema**
- **Dashboard:** http://127.0.0.1:8000
- **Admin:** http://127.0.0.1:8000/admin

## 📊 Como usar

1. **Acesse o painel admin** (`/admin`)
2. **Adicione transações** (receitas e despesas)
3. **Visualize o dashboard** com totais automáticos
4. **Gerencie suas finanças** de forma organizada

## 🎯 Próximas funcionalidades

- [ ] Gráficos interativos
- [ ] Relatórios em PDF
- [ ] Integração com IA para insights
- [ ] API REST
- [ ] Importação de extratos bancários

## 👨‍💻 Desenvolvedor

Projeto desenvolvido como aprendizado em Django e desenvolvimento web.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

⭐ Se este projeto te ajudou, considere dar uma estrela!