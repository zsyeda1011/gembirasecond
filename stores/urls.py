from django.urls import path
from . import views
urlpatterns = [
    path('cafe', views.cafe, name='stores.cafe'),
]