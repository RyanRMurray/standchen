import asyncio
from typing import Optional
import logging

from django.template import loader
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_GET
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
)

from standchen.player.common import get_files_and_directories, get_permitted_filepaths
from standchen.player.forms import DUPLICATE_FILEPATH, NewAudioForm, NewPlaylistForm
from standchen.player.models import Playlist, StandchenAudio
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
    all_playlists = Playlist.objects.all()
    if len(all_audios) == 0:
        return HttpResponse("No tracks.")
    template = loader.get_template("audios/list.html")
    context = {"audio_list": all_audios, "playlist_list": all_playlists}
    return HttpResponse(template.render(context, request))


def state(request: HttpRequest):
    return HttpResponse(api.pretty_print_state(), request)


def _upload_directory(dir: str) -> tuple[int, int, list[tuple[str, dict]]]:
    files, _ = get_files_and_directories(dir)
    new, dupes, errors = 0, 0, []

    for f in files:
        form = NewAudioForm({"filepath": f})
        if form.is_valid():
            form.save()
            new += 1
        elif DUPLICATE_FILEPATH in form.errors["filepath"]:
            dupes += 1
        else:
            errors.append((f, form.errors))

    return new, dupes, errors


def upload(request: HttpRequest):
    template = loader.get_template("audios/upload.html")
    form = NewAudioForm()

    if request.method == "POST" and request.POST["directory"]:
        # upload everything under a directory
        new, dupes, errors = _upload_directory(request.POST["directory"])
        result_message = f"Added {new} new tracks.\n"
        if dupes > 0:
            result_message += f"Skipped {dupes} tracks that were already uploaded.\n"
        if len(errors) > 0:
            result_message += "The following filepaths were invalid:\n"
            result_message += [f"{fp}: {errs}" for (fp, errs) in errors]

        messages.success(request, result_message)
        return HttpResponseRedirect(reverse("audios"))

    if request.method == "POST":
        # upload a single track
        form = NewAudioForm(request.POST)
        if form.is_valid():
            form.save()
            result_message = f"Uploaded new track at filepath {form.filepath}"
            messages.success(request, result_message)
            return HttpResponseRedirect(reverse("audios"))

    filepaths, directories = get_permitted_filepaths()
    context = {"form": form, "filepaths": filepaths, "directories": directories}
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


def create_playlist(request: HttpRequest):
    template = loader.get_template("audios/create_playlist.html")
    if request.method == "POST":
        form = NewPlaylistForm(request.POST)
        if form.is_valid():
            form.save()

            result_message = f'Created new playlist "{form.cleaned_data["title"]}" with {len(form.cleaned_data["tracks"])} tracks.'
            messages.success(request, result_message)
            return HttpResponseRedirect(reverse("audios"))
        else:
            result_message = "Failed to create playlist (internal error)"
            messages.error(request, result_message)

    # TODO: dynamic query. currently just lists all tracks
    form = NewPlaylistForm()
    context = {"form": form}
    return HttpResponse(template.render(context, request))
