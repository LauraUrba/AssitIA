# telas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Estudantes
    path('estudantes/', views.lista_estudantes, name='lista_estudantes'),
    path('estudantes/novo/', views.novo_estudante, name='novo_estudante'),
    path('estudantes/<uuid:id>/', views.detalhe_estudante, name='detalhe_estudante'),
    path('estudantes/<uuid:id>/editar/', views.editar_estudante, name='editar_estudante'),
    path('estudantes/<uuid:estudante_id>/salvar-perfil/', views.salvar_perfil_tea, name='salvar_perfil_tea'),

    # Tecnologias
    path('tecnologias/catalogo/', views.catalogo_tecnologias, name='catalogo_tecnologias'),
    path('tecnologias/avaliar/', views.avaliar_tecnologia, name='avaliar_tecnologia'),

    #ADM
    path('criar-superusuario/', views.criar_superusuario, name='criar_superusuario'),
    path('executar-populate/', views.executar_populate, name='executar_populate'),
    # Recomendações
    path('recomendacoes/', views.lista_recomendacoes, name='lista_recomendacoes'),
    path('recomendacoes/gerar/<uuid:estudante_id>/', views.gerar_recomendacao, name='gerar_recomendacao'),
    path('recomendacoes/<uuid:id>/', views.detalhe_recomendacao, name='detalhe_recomendacao'),
    path('recomendacoes/<uuid:id>/arquivar/', views.arquivar_recomendacao, name='arquivar_recomendacao'),
    path('recomendacoes/<uuid:id>/excluir/', views.excluir_recomendacao, name='excluir_recomendacao'),
    path('recomendacoes/salvar/', views.salvar_recomendacao, name='salvar_recomendacao'),
    path('recomendacoes/feedback/', views.salvar_feedback, name='salvar_feedback'),

    # PEI
    path('pei/', views.lista_pei, name='lista_pei'),
    path('pei/gerar/<uuid:estudante_id>/', views.gerar_pei, name='gerar_pei'),
    path('pei/<uuid:id>/', views.detalhe_pei, name='detalhe_pei'),
    path('pei/<uuid:id>/editar/', views.editar_pei, name='editar_pei'),
    path('pei/<uuid:id>/pdf/', views.gerar_pdf_pei, name='gerar_pdf_pei'),

    # Perfil
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),

    # Segurança
    path('seguranca/', views.dashboard_seguranca, name='dashboard_seguranca'),
    path('seguranca/desbloquear-ip/<str:ip>/', views.desbloquear_ip_view, name='desbloquear_ip'),
]