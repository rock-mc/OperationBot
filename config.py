import os
import warnings

version = '1.0.1'

DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK', None)
DISCORD_OP_USER_ID = os.environ.get('DISCORD_OP_USER_ID', None)

ENABLE_CHECK_NETWORK = True
# after WAIT_NETWORK_MINUTES, if network is still not ok, shutdown the server
WAIT_NETWORK_MINUTES = 5

# Check server log every READ_LOG_TIME seconds
READ_LOG_TIME = 60

# Clear db data older than KEEP_LATEST_DB_DATA_DAYS days
KEEP_LATEST_DB_DATA_DAYS = 60

# If TPS is lower than TPS_LAG_THRESHOLD for 5 minutes, restart the server
# It will also send a message to the server when TPS is lower than TPS_LAG_THRESHOLD for 1 minute
TPS_LAG_THRESHOLD = 19

# Find the server.properties file as the root of the server
SERVER_ROOT = os.path.dirname(__file__)
for i in range(8):
    if os.path.exists(f'{SERVER_ROOT}/server.properties'):
        break
    SERVER_ROOT = os.path.dirname(SERVER_ROOT)

if SERVER_ROOT == '/':
    warnings.warn("server.properties is not found", Warning)
