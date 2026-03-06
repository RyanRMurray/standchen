import asyncio
from typing import Optional
import logging

from django.template import loader
from django.urls import reverse
from django.views.decorators.http import require_GET
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
)

from standchen.player.common import get_permitted_filepaths
from standchen.player.forms import NewAudioForm
from standchen.player.models import StandchenAudio
from standchen.player.apps import standchen_player as api

logger = logging.getLogger(__name__)

player_coro: Optional[asyncio.Task] = None


async def end():
    global player_coro
    if player_coro is None:
        raise RuntimeError("Player is already stopped")
    else:
        player_coro.cancel()
        player_coro = None


def audios(request: HttpRequest):
    all_audios = StandchenAudio.objects.all()
    if len(all_audios) == 0:
        return HttpResponse("No tracks.")
    template = loader.get_template("audios/list.html")
    context = {"audio_list": all_audios}
    return HttpResponse(template.render(context, request))


def state(request: HttpRequest):
    return HttpResponse(api.pretty_print_state(), request)


def upload(request: HttpRequest):
    if request.method == "POST":
        form = NewAudioForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("audios"))

    template = loader.get_template("audios/upload.html")
    context = {"filepaths": get_permitted_filepaths()}
    return HttpResponse(template.render(context, request))


@require_GET
async def queue(request: HttpRequest):
    id = request.GET.get("audio_id")
    filepath = request.GET.get("filepath")
    if id is not None:
        # todo
        return HttpResponseBadRequest("Not yet implemented", request)

    if filepath is not None:
        result = await api.queue_local(filepath)
        return HttpResponse(result)

    return HttpResponseBadRequest("Request should have an audio ID or filepath")
