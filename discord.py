from discordwebhook import Discord

import config

discord_bot = Discord(url=config.DISCORD_WEBHOOK)

if __name__ == '__main__':
    discord_bot.post(content="Hello World!")
