from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='home'),
    path('signs/signgen/<signsize>', views.SignGen, name='signgen'),
    path('ecouponflooder', views.ecpn, name='ecpn')
]