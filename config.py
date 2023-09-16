import os

version = '1.0.0'

DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK', None)
DISCORD_OP_USER_ID = os.environ.get('DISCORD_OP_USER_ID', None)

SERVER_ROOT = os.path.dirname(__file__)
for i in range(8):
    if os.path.exists(f'{SERVER_ROOT}/server.properties'):
        break
    SERVER_ROOT = os.path.dirname(SERVER_ROOT)

if SERVER_ROOT == '/':
    raise Exception('server.properties not found')

READ_LOG_TIME = 60
KEEP_LATEST_DB_DATA_DAYS = 60

TPS_LAG_THRESHOLD = 19
