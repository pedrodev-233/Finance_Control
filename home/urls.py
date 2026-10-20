from django.urls import path
from .views import auth, dashboard

urlpatterns = [
    path('', auth, name='Auth'),
    path('controle/', dashboard, name='Control'),
]