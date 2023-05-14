from django.urls import path
from . import views

urlpatterns = [
    path('', views.autentificare_magazin, name='autentificare_magazin'),
    path('inregistrare/', views.inregistrare_magazin, name='inregistrare_magazin'),
    path('acasa/', views.acasa, name='acasa'),
    path('comenzi/', views.comenzi, name='comenzi'),
    path('clienti/', views.clienti, name='clienti'),
    path('aprovizionari/', views.aprovizionari, name='aprovizionari'),
    path('venituri/', views.venituri, name='venituri'),
    path('adaugare_produs/', views.adaugare_produs,  name = 'adaugare_produs'),
    path('adaugare_aprovizionare/<int:id_produs>', views.adaugare_aprovizionare,  name = 'adaugare_aprovizionare'),
    path('stergere_produs/<int:id_produs>', views.stergere_produs, name='stergere_produs'),
    path('editare_produs/<int:id_produs>', views.editare_produs,  name = 'editare_produs'),
    #path('home/<int:product_id>/edit/', views.edit_product, name='edit_product'),

]
