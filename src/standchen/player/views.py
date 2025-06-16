import asyncio
from typing import Optional
from django.template import loader
from django.views.decorators.http import require_GET
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest

from standchen.player.models import StandchenAudio
from standchen.player.apps import standchen_player

player_coro: Optional[asyncio.Task] = None


def ensure_started(func):
    async def wrapper(self, *args, **kwargs):
        if player_coro is None:
            await start()
            return func(self, *args, **kwargs)

    return wrapper


async def start():
    global player_coro
    if player_coro is None:
        player_coro = asyncio.create_task(standchen_player.execute())
    else:
        raise RuntimeError("Player is already running")


async def end():
    global player_coro
    if player_coro is None:
        raise RuntimeError("Player is already stopped")
    else:
        player_coro.cancel()
        player_coro = None


def audios(request: HttpRequest):
    all_audios = StandchenAudio.objects.all()
    template = loader.get_template("audios/audio_list.html")
    context = {"audio_list": all_audios}
    return HttpResponse(template.render(context, request))


def state(request: HttpRequest):
    return HttpResponse(standchen_player.pretty_print_state(), request)


@require_GET
async def queue(request: HttpRequest):
    id = request.GET.get("audio_id")
    filepath = request.GET.get("filepath")
    if id is not None:
        # todo
        return HttpResponseBadRequest("Not yet implemented", request)

    if filepath is not None:
        result = await standchen_player.queue_local(filepath)
        return HttpResponse(result)

    return HttpResponseBadRequest("Request should have an audio ID or filepath")
