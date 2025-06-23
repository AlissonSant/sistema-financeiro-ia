# finance/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # 🆕 NOVAS URLS para CRUD de transações
    path('editar/<int:transacao_id>/', views.editar_transacao, name='editar_transacao'),
    path('excluir/<int:transacao_id>/', views.excluir_transacao, name='excluir_transacao'),
]