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
    # ADICIONE essas URLs NO FINAL do seu finance/urls.py

    # 🎯 URLS DO SISTEMA DE METAS
    path('metas/', views.metas_dashboard, name='metas_dashboard'),
    path('metas/criar/', views.criar_meta, name='criar_meta'),
    path('metas/<int:meta_id>/', views.detalhes_meta, name='detalhes_meta'),
    path('metas/<int:meta_id>/editar/', views.editar_meta, name='editar_meta'),
    path('metas/<int:meta_id>/pausar/', views.pausar_meta, name='pausar_meta'),
    path('metas/<int:meta_id>/excluir/', views.excluir_meta, name='excluir_meta'),
]