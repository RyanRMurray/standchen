from django.urls import path

from standchen.player.views import pages, actions

urlpatterns = [
    # rendered pages
    path("audios/", pages.audios, name="audios"),
    path("audios/upload", pages.upload, name="upload"),
    path("queue", pages.queue, name="queue"),
    path("state", pages.state, name="state"),
    # api
    path(
        "play_immediate/<int:audio_id>", actions.play_immediate, name="play_immediate"
    ),
]
