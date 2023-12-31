# Minecraft Operation Bot

**Minecraft Operation Bot** is developed in Python for operating Minecraft Server.

NOTE: Currently only supports Linux.

## Commands
**Minecraft Operation Bot** supports the following commands:

### cmd_start_service
Activate the server service, which has the following features.

Such as:
- Restart server while the server is lagging
- Backup server map data
- Automatically update server program
- Send a message to the Discord channel when the server is started or stopped


### cmd_stop_service
This function will be responsible for stopping the server.

### cmd_update_service
This function will be responsible for applying the new version **Minecraft Operation Bot** without restarting the server.

## How to use

### Requirements
- Python 3.8 or higher

### Installation

```bash
cd minecraft_server_root

git clone git@github.com:rock-mc/OperationBot.git operation_bot
cd operation_bot
pip install -r requirements.txt
```

### Configuration

First, you need to create a script file to run server that named `run_server.sh` in the root directory of the server.
Here is an example of the script file.

```bash
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH

./$JAVA_PATH/java -Xms24G -Xmx24G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=40 -XX:G1MaxNewSizePercent=50 -XX:G1HeapRegionSize=16M -XX:G1ReservePercent=15 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=20 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -Dusing.aikars.flags=https://mcflags.emc.gs -Daikars.new.flags=true -jar $1 nogui
````

[Optional] Next, you need to create a Discord Webhook.

```bash
export DISCORD_WEBHOOK="https://discord.com/api/webhooks/xxxxx"
export DISCORD_OP_USER_ID="xxxxxxxxxxxxxxxxxx"
```

### Run

Run the following command to start the service.
```bash
python3 operation_bot/cmd_start_service.py
```

Run the following command to stop the service.
```bash
python3 operation_bot/cmd_stop_service.py
```

Run the following command to update the service.
```bash
python3 operation_bot/cmd_update_service.py
```
### Set as a service

Create a service file in `/etc/systemd/system/minecraft.service` with the following content.
It can keep cmd_start_service.py running at all times.

```text
[Unit]
Description=Minecraft service
After=network.target

[Service]
WorkingDirectory=THIS_VALUE_WILL_REPLACE_WITH_MCHOME
ExecStart=/usr/bin/python3 THIS_VALUE_WILL_REPLACE_WITH_MCHOME/operation_bot/cmd_start_service.py
ExecStop=/usr/bin/python3 THIS_VALUE_WILL_REPLACE_WITH_MCHOME/operation_bot/cmd_stop_service.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

If you want to start the service automatically when the system starts, run the following command.
```bash
systemctl enable minecraft
```

If you want to start the service manually, run the following command.
```bash
systemctl start minecraft
```

If you want to stop the service, run the following command.
```bash
systemctl stop minecraft
```

## Features

- [x] Update **Minecraft Operation Bot** without restarting the server