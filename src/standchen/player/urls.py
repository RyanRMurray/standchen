from django.urls import path

from . import views

urlpatterns = [
    path("audios/", views.audios, name="audios"),
    path("audios/upload", views.upload, name="upload"),
    path("queue", views.queue, name="queue"),
    path("state", views.state, name="state"),
]
