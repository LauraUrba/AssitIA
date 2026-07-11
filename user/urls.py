from django.urls import path
from . import views

urlpatterns = [
    # Autenticação - TELAS HTML
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('logout/', views.logout_view, name='logout'),
    path('esqueci-senha/', views.esqueci_senha_view, name='esqueci_senha'),
    path('redefinir-senha/<str:uidb64>/<str:token>/', views.redefinir_senha_view, name='redefinir_senha'),
    path('verificar-otp/', views.verificar_otp_view, name='verificar_otp'),

]