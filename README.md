# Standchen
A client for playing local music over Discord via a bot.

## Upcoming features
- Playlists
- A django-enabled web app for managing tracks, playlists, and queueing multiple 'channels' at the same time
- optional track pre-loading to ensure smooth transitions between tracks

## Setup
1. Get dependencies:
```shell
sudo apt-get install portaudio19-dev sqlite3
```
1. Install [poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)
1. Install project dependencies with `poetry install`
1. Ensure database is up to date with `manage migrate`

## Run
Create a settings file using the `setting.json.example` file.
- `guild_id` is the target server's ID. Find this by right-clicking the target server's icon in your server list.
- `bot_token` is the [Discord Bot's](https://discordpy.readthedocs.io/en/stable/discord.html) auth token.

Start poetry environment with `eval $(poetry env activate)`
Start bot and site with `start runserver --noreload`

## Contribute
1. Install extra dependencies with `poetry install --with dev`
2. Run `pre-commit install`
