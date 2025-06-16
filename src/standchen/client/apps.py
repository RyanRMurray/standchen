from django.apps import AppConfig


standchen_player = None


class ClientConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "standchen.client"

    def ready(self):
        from standchen.client.player import StandchenClient

        global standchen_player
        standchen_player = StandchenClient()
