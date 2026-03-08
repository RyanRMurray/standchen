from pathlib import Path

from asgiref.sync import sync_to_async
import mutagen
from mutagen import FileType
import asyncio
from enum import Enum
import math
import os
from typing import Optional
from collections import deque
from discord import FFmpegPCMAudio, VoiceClient
from django.db import models
import logging

from standchen.player.common import VALID_EXTENSIONS

logger = logging.getLogger(__name__)


class StandchenAudio(models.Model):
    # max length based on limitation of ubuntu filepaths
    filepath = models.CharField(max_length=4096, unique=True)
    title = models.CharField(max_length=256)
    length = models.IntegerField()
    album = models.CharField(null=True)
    artist = models.CharField(null=True)

    def get_name(self) -> str:
        if self.title:
            return self.title
        return self.filepath

    def get_file(self) -> str:
        if os.path.exists(self.filepath):
            return self.filepath

        raise OSError(f"No such audio file: {self.filepath}")

    def pretty_length(self) -> str:
        mins = math.floor(self.length / (1000 * 60))
        secs = math.floor((self.length / 1000) % 60)
        return f"{mins}:{secs}"

    def __str__(self) -> str:
        return f"{self.title} ({self.pretty_length()}): {self.filepath}"

    def html_str(self) -> str:
        return f"<b>{self.title}</b> ({self.pretty_length()}): {self.filepath}"


class Playlist(models.Model):
    title = models.CharField(max_length=256)
    tracks = models.ManyToManyField(StandchenAudio)

    def html_str(self) -> str:
        return f"<b>{self.title}</b> ({self.tracks.count()} tracks)"


class Repeat(Enum):
    NONE = 1
    SINGLE = 2
    ALL = 3


@sync_to_async
def async_get_playlist_tracks(playlist: Playlist) -> list[StandchenAudio]:
    return list(StandchenAudio.objects.filter(playlist=playlist).all())


class StandchenPlayer:
    def __init__(self):
        self.voice_client: Optional[VoiceClient] = None

        self.current: Optional[StandchenAudio] = None
        self.queue: deque[StandchenAudio] = deque()
        self.repeat = Repeat.NONE
        self.lock = asyncio.Lock()
        self.exiting = False

    # def need_vc(func):d
    #     def wrapper(self, *args, **kwargs):
    #         if self.voice_client:
    #             func(self, *args, **kwargs)
    #         else:
    #             print("No voice client")

    #     return wrapper

    def blocking(func):
        async def wrapper(self, *args, **kwargs):
            await self.lock.acquire()
            try:
                result = await func(self, *args, **kwargs)
                return result
            except Exception as e:
                raise e
            finally:
                self.lock.release()

        return wrapper

    @blocking
    async def set_vc(self, new_voice_client: VoiceClient):
        """Set the active voice client for this client"""

        if self.voice_client:  # disconnect from old vc if needed
            if self.voice_client.channel != new_voice_client.channel:
                await self.voice_client.disconnect()
            else:
                return

        self.voice_client = await new_voice_client.channel.connect()

    @blocking
    async def set_repeat(self, setting: int):
        self.repeat = Repeat(setting)

    async def _play_track(self, audio: StandchenAudio):
        """Retrieve and play the specified audio"""
        f = audio.get_file()

        def after(error: Exception):
            if error:
                n = audio.get_name()
                print(f"Failed to play '{n}': {str(error)}")
                raise error

        # TODO: pass in ffmpeg args - e.g. skip to time
        self.voice_client.play(FFmpegPCMAudio(source=f), after=after)

    async def add_track_by_filepath(
        self, filepath: str, replace=False
    ) -> StandchenAudio:
        """
        Validate a filepath is a track and add it to the library.
        If replace is true, overwrites an entry with the same filepath (e.g. for bulk updating metadata)
        Returns the new/existing audio track
        """

        existing = await StandchenAudio.objects.filter(filepath=filepath).afirst()
        if existing is not None:
            if not replace:
                return existing
            else:
                # TODO: ensure this doesn't remove the item from playlists when they're implemented
                await existing.adelete()

        fp = Path(filepath)
        # check file is valid
        if not fp.is_file():
            raise OSError("Filepath is not a file!")
        if fp.suffix not in VALID_EXTENSIONS:
            raise OSError(f"Invalid file type: '{fp.suffix}'")

        # get data
        data = mutagen.File(fp)

        if not isinstance(data, FileType):
            raise OSError("File is invalid/corrupt.")

        default_name = fp.name
        track = await StandchenAudio.objects.acreate(
            filepath=filepath,
            title=data.get("title", [default_name])[0],
            length=math.floor(
                data.info.length * 1000
            ),  # convert from float secs to int millisecs
            album=data.get("album", [None])[0],
            artist=data.get("artist", [None])[0],
        )
        return track

    @blocking
    async def queue_local(self, filepath: str) -> str:
        """Create an audio object from a filepath and add it to the queue"""
        try:
            track = await self.add_track_by_filepath(filepath)
        except OSError as e:
            return str(e)
        except Exception as e:
            logging.error(e)
            return f"Failed to add filepath '{filepath}' to queue."

        self.queue.append(track)
        return f"Added track '{track.get_name()}' to queue."

    @blocking
    async def play_immediate_by_id(self, id: int) -> str | None:
        """Cancel current track and immediately play new track in its place in the queue"""
        track = await StandchenAudio.objects.aget(id=id)

        self.queue.appendleft(track)
        self.current = None
        self.voice_client.stop()

    @blocking
    async def play_playlist_immediate_by_id(self, id: int) -> str | None:
        """Cancel current track and immediately play new playlist in its place in the queue"""
        # TODO: options for ordering
        playlist = await Playlist.objects.aget(id=id)
        tracks = await async_get_playlist_tracks(playlist)

        self.queue = deque(tracks)
        self.current = None
        self.voice_client.stop()

    async def execute(self):
        """Core audio stream loop logic"""

        def play_ready() -> bool:
            if not self.voice_client:
                return False
            if not self.current and len(self.queue) == 0:
                return False
            return not self.voice_client.is_playing()

        while not self.exiting:
            # ensure we have a vc and content
            while not play_ready():
                await asyncio.sleep(0.2)

            await self.lock.acquire()

            if not self.current:
                self.current = self.queue.popleft()
            # play
            try:
                await self._play_track(self.current)
            except Exception as e:
                n = self.current.get_name()
                self.current = None

                self.lock.release()
                print(f"Failed to play track '{n}'. Removing from queue.\nError: {e}")

            # handle repeat logic
            # TODO: this doesn't work right if we want to display the name of the current track and its not Repeat.SINGLE
            if self.repeat == Repeat.NONE:
                self.current = None
            if self.repeat == Repeat.ALL:
                self.queue.append(self.current)
                self.current = None
            self.lock.release()

    def pretty_print_state(self) -> str:
        """Return a discord-formatted string to represent the current state of the client for end users"""
        current = f"**{self.current.get_name()}**" if self.current else "*None*"
        match self.repeat:
            case Repeat.NONE:
                repeat = "None ❌"
            case Repeat.SINGLE:
                repeat = "Single 🔂"
            case Repeat.ALL:
                repeat = "All 🔁"
        queue_items = [f"1. {a.get_name()}" for a in self.queue]
        queue = "\n".join(queue_items) if queue_items else "*Empty*"

        return f"""
**Currently Playing:** {current}
**Repeating:** {repeat}
**Queue:**
{queue}
"""
