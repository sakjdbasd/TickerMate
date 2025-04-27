from django.urls import path 
from . import views 

urlpatterns = [
    path("summary", views.summarized_news_api),
]