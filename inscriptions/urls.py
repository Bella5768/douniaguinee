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
    
    # Pages de gestion (admin)
    path('gestion/', views.admin_dashboard, name='admin_dashboard'),
    path('gestion/evenements/', views.admin_evenements, name='admin_evenements'),
    path('gestion/inscriptions/', views.admin_inscriptions, name='admin_inscriptions'),
    path('gestion/inscription/<int:pk>/', views.admin_inscription_detail, name='admin_inscription_detail'),
    path('gestion/inscription/<int:pk>/edit/', views.admin_inscription_edit, name='admin_inscription_edit'),
    path('gestion/inscription/<int:pk>/delete/', views.admin_inscription_delete, name='admin_inscription_delete'),
    path('gestion/inscription/<int:pk>/valider/', views.admin_inscription_valider, name='admin_inscription_valider'),
    path('gestion/contenu/', views.admin_contenu_page, name='admin_contenu_page'),
    path('gestion/chiffres/', views.admin_chiffres, name='admin_chiffres'),
    path('gestion/experts/', views.admin_experts, name='admin_experts'),
    path('gestion/partenaires/', views.admin_partenaires, name='admin_partenaires'),
    path('gestion/dounia-events/', views.admin_dounia_events, name='admin_dounia_events'),
    path('gestion/restitution/', views.admin_restitution, name='admin_restitution'),
    path('gestion/ateliers/', views.admin_ateliers, name='admin_ateliers'),
    path('gestion/edit-section/<str:section>/', views.admin_edit_section, name='admin_edit_section'),
    path('export-csv/', views.export_inscriptions_csv, name='export_inscriptions_csv'),
]
