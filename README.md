# Standchen
Music bot thingy

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
- `guild_id` is the target server's ID
- `bot_token` is the [Discord Bot's](https://discordpy.readthedocs.io/en/stable/discord.html) auth token.

Start poetry environment with `eval $(poetry env activate)`
Start bot and site with `start`

## Contribute
1. Install extra dependencies with `poetry install --with dev`
2. Run `pre-commit install`
