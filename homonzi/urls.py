from django.contrib import admin
import homonzi.views as views
from django.urls import path, include

urlpatterns = [
    path('', views.index),
    path('runPrompt', views.runPrompt),
]