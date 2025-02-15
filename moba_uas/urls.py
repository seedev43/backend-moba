"""
URL configuration for moba_uas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from api.views.auth import user_detail_view
from api.views.ai import similarity, add_rating, get_recommendation_movies

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('api.urls')),
    path('user/<int:user_id>/', user_detail_view, name='user_detail'),
    path('similarity', similarity),
    path('add_rating', add_rating, name='add_rating'),
    path('get-recommendation-movies', get_recommendation_movies)
]
