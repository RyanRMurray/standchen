from django.http import HttpResponse
from standchen.bot.apps import start_bot


async def start(request):
    result = await start_bot()
    if result:
        return HttpResponse("Started bot", request)
    else:
        result = HttpResponse("Bot already started")
        result.status_code = 304
        return result
