import math
import os
from django.db import models


class StandchenAudio(models.Model):
    # max length based on limitation of ubuntu filepaths
    filepath = models.CharField(max_length=4096, unique=True)
    name = models.CharField(max_length=256)
    length = models.IntegerField()

    def get_name(self) -> str:
        if self.name:
            return self.name
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
        return f"{self.name} ({self.pretty_length()}): {self.filepath}"
