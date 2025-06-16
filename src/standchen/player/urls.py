from django.urls import path

from . import views

urlpatterns = [
    path("audios/", views.audios, name="audios"),
    path("test/", views.test, name="test"),
    path("start", views.start, name="start"),
    path("end", views.end, name="end"),
]
