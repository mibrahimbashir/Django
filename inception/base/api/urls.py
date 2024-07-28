from django.urls import path
from . import views

urlpatterns = [
	path('', views.routes),
	path('rooms/', views.get_rooms),
	path('room/<str:pk>', views.get_room),
]