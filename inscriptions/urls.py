from django.urls import path
from . import views

urlpatterns = [
    # Pages publiques
    path('', views.landing_page, name='landing_page'),
    path('inscription/', views.inscription, name='inscription'),
    path('merci/', views.merci, name='merci'),
    path('rapport-download/', views.rapport_download, name='rapport_download'),
    path('rapport-view/', views.rapport_view_pdf, name='rapport_view_pdf'),
    path('atelier/<int:atelier_id>/', views.atelier_detail, name='atelier_detail'),
    path('restitution/', views.restitution_page, name='restitution_page'),
    path('event/<slug:event_slug>/', views.event_page, name='event_page'),
    path('search/', views.search_results, name='search_results'),
]
