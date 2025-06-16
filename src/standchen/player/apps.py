from django.apps import AppConfig


standchen_player = None


class ClientConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "standchen.player"

    def ready(self):
        from standchen.player.player import StandchenClient

        global standchen_player
        standchen_player = StandchenClient()
