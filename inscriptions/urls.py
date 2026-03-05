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

    # Dashboard de gestion
    path('gestion/', views.admin_dashboard, name='admin_dashboard'),
    path('gestion/inscriptions/', views.admin_inscriptions, name='admin_inscriptions'),
    path('gestion/inscriptions/<int:pk>/', views.admin_inscription_detail, name='admin_inscription_detail'),
    path('gestion/inscriptions/<int:pk>/edit/', views.admin_inscription_edit, name='admin_inscription_edit'),
    path('gestion/inscriptions/<int:pk>/delete/', views.admin_inscription_delete, name='admin_inscription_delete'),
    path('gestion/inscriptions/<int:pk>/valider/', views.admin_inscription_valider, name='admin_inscription_valider'),

    # Gestion du contenu
    path('gestion/contenu/', views.admin_contenu_page, name='admin_contenu_page'),
    path('gestion/contenu/<str:section>/', views.admin_edit_section, name='admin_edit_section'),
    path('gestion/chiffres/', views.admin_chiffres, name='admin_chiffres'),
    path('gestion/experts/', views.admin_experts, name='admin_experts'),
    path('gestion/ateliers/', views.admin_ateliers, name='admin_ateliers'),
    path('temp-ateliers/', views.admin_ateliers, name='temp_admin_ateliers'),
    path('gestion/evenements/', views.admin_evenements, name='admin_evenements'),
    path('restitution/', views.restitution_page, name='restitution_page'),
    path('event/<slug:event_slug>/', views.event_page, name='event_page'),
    path('search/', views.search_results, name='search_results'),
    path('gestion/dounia-events/', views.admin_dounia_events, name='admin_dounia_events'),
    path('gestion/restitution/', views.admin_restitution, name='admin_restitution'),
    path('gestion/partenaires/', views.admin_partenaires, name='admin_partenaires'),

    # Export
    path('gestion/export/inscriptions/', views.export_inscriptions_csv, name='export_inscriptions_csv'),
    path('gestion/export/inscriptions/pdf/', views.export_inscriptions_pdf, name='export_inscriptions_pdf'),
    path('gestion/agenda/pdf/', views.generer_agenda_pdf_view, name='generer_agenda_pdf'),

    # Gestion des images hero et statistiques
    path('gestion/hero-stats-images/', views.manage_hero_stats_images, name='manage_hero_stats_images'),
    path('gestion/hero-images/add/', views.add_hero_image, name='add_hero_image'),
    path('gestion/stats-images/add/', views.add_stats_image, name='add_stats_image'),
    path('gestion/hero-images/toggle/<int:image_id>/', views.toggle_hero_image, name='toggle_hero_image'),
    path('gestion/stats-images/toggle/<int:image_id>/', views.toggle_stats_image, name='toggle_stats_image'),
    path('gestion/hero-images/delete/<int:image_id>/', views.delete_hero_image, name='delete_hero_image'),
    path('gestion/stats-images/delete/<int:image_id>/', views.delete_stats_image, name='delete_stats_image'),
    path('gestion/hero-images/update-order/', views.update_hero_image_order, name='update_hero_image_order'),
    path('gestion/stats-images/update-order/', views.update_stats_image_order, name='update_stats_image_order'),

    # Carousel images
    path('gestion/carousel-images/add/', views.add_carousel_image, name='add_carousel_image'),
    path('gestion/carousel-images/toggle/<int:image_id>/', views.toggle_carousel_image, name='toggle_carousel_image'),
    path('gestion/carousel-images/delete/<int:image_id>/', views.delete_carousel_image, name='delete_carousel_image'),
    path('gestion/carousel-images/order/', views.update_image_order, name='update_carousel_image_order'),
]
