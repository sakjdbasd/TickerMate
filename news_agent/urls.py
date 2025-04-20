from django.urls import path 
import views 

urlpatterns = [
    path("dashboard/", views.news_dashboard, name="news_dashboard"), 
]