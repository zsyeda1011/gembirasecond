from django.urls import path
from . import views

urlpatterns = [
 path('', views.index, name='movies.index'),
 path('map/', views.map_view, name='movies.map'),
 path('locations-geojson/', views.locations_geojson, name='movies.locations_geojson'),
 path('<int:id>/', views.show, name='movies.show'),
 path('<int:id>/purchase/', views.purchase_movie, name='movies.purchase_movie'),
 path('<int:id>/review/create/', views.create_review,
 name='movies.create_review'),
 path('<int:id>/review/<int:review_id>/edit/',
    views.edit_review, name='movies.edit_review'),
 path('<int:id>/review/<int:review_id>/delete/',
    views.delete_review, name='movies.delete_review'),
path('petitions/', views.petitions_index, name='petitions.index'),
path("petitions/create/", views.petition_create, name="create_petitions"),
path("petitions/<int:id>/vote/", views.petition_vote, name="petitions.vote"),
path ('<int:id>/rate/', views.rate_movie, name='movies.rate_movie'),
]
