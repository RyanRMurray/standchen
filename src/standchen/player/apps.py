from django.apps import AppConfig

from standchen.signals import SET_VC


standchen_player = None


async def set_vc(sender, **kwargs):
    await standchen_player.set_vc(kwargs["voice_channel"])


class ClientConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "standchen.player"

    def ready(self):
        from standchen.player.models import StandchenClient

        global standchen_player
        standchen_player = StandchenClient()
        SET_VC.connect(set_vc)
