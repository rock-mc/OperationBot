from discordwebhook import Discord

import config

enabled = config.DISCORD_WEBHOOK is not None and config.DISCORD_OP_USER_ID is not None
discord_bot = Discord(url=config.DISCORD_WEBHOOK) if enabled else None

if __name__ == '__main__':
    discord_bot.post(content="Hello World!")
