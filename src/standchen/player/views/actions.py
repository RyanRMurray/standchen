from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_GET
from django.contrib import messages

from standchen.player.apps import standchen_player as api


@require_GET
async def play_immediate(request: HttpRequest, audio_id: int):
    result = await api.play_immediate_by_id(audio_id)

    if result:
        messages.error(request, result)

    # TODO: ajaxify this
    return HttpResponseRedirect(reverse("audios"))
