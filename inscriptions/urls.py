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
    path('soumettre-avis/', views.soumettre_avis, name='soumettre_avis'),
    
    # Pages de gestion (admin)
    path('gestion/login/', views.admin_login, name='admin_login'),
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
    path('gestion/avis/', views.admin_avis, name='admin_avis'),
    path('gestion/edit-section/<str:section>/', views.admin_edit_section, name='admin_edit_section'),
    path('export-csv/', views.export_inscriptions_csv, name='export_inscriptions_csv'),
    path('manage-hero-stats-images/', views.manage_hero_stats_images, name='manage_hero_stats_images'),
    
    # URLs pour les images hero et stats
    path('add-hero-image/', views.add_hero_image, name='add_hero_image'),
    path('add-stats-image/', views.add_stats_image, name='add_stats_image'),
    path('add-carousel-image/', views.add_carousel_image, name='add_carousel_image'),
    path('gestion/hero-images/delete/<int:image_id>/', views.delete_hero_image, name='delete_hero_image'),
    path('gestion/stats-images/delete/<int:image_id>/', views.delete_stats_image, name='delete_stats_image'),
    path('gestion/carousel-images/delete/<int:image_id>/', views.delete_carousel_image, name='delete_carousel_image'),
    
    # Toggle et ordre des images
    path('gestion/hero-images/toggle/<int:image_id>/', views.toggle_hero_image, name='toggle_hero_image'),
    path('gestion/stats-images/toggle/<int:image_id>/', views.toggle_stats_image, name='toggle_stats_image'),
    path('gestion/carousel-images/toggle/<int:image_id>/', views.toggle_carousel_image, name='toggle_carousel_image'),
    path('gestion/hero-images/order/', views.update_hero_image_order, name='update_hero_image_order'),
    path('gestion/stats-images/order/', views.update_stats_image_order, name='update_stats_image_order'),
    path('gestion/images/order/', views.update_image_order, name='update_image_order'),
    
    # Autres fonctionnalités
    path('gestion/hero-images/', views.manage_hero_images, name='manage_hero_images'),
    path('export-pdf/', views.export_inscriptions_pdf, name='export_inscriptions_pdf'),
    path('generer-agenda-pdf/', views.generer_agenda_pdf_view, name='generer_agenda_pdf_view'),
]
