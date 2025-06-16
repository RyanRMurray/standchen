import asyncio
from typing import Optional
from django.template import loader
from django.http import HttpResponse, HttpResponseBadRequest

from standchen.client.models import StandchenAudio
from standchen.client.apps import standchen_player

client_coro: Optional[asyncio.Task] = None


def audios(request):
    all_audios = StandchenAudio.objects.all()
    template = loader.get_template("audios/audio_list.html")
    context = {"audio_list": all_audios}
    return HttpResponse(template.render(context, request))


def test(request):
    return HttpResponse(standchen_player.pretty_print_state())


async def start(request):
    global client_coro
    if client_coro is None:
        client_coro = asyncio.create_task(standchen_player.execute())
        return HttpResponse("Started client", request)
    else:
        return HttpResponseBadRequest("Client is already running", request)


async def end(request):
    global client_coro
    if client_coro is None:
        return HttpResponseBadRequest("Client is already stopped", request)
    else:
        client_coro.cancel()
        client_coro = None
        return HttpResponse("Stopped client", request)
