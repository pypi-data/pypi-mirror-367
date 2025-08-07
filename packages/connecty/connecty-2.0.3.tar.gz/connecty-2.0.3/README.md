
# ᵛᶦᵐᵛᶦᵐ'ˢ Connecty
## Overview
1. Install python (Windows or debian)
2. Install connecty
3. Setup manuallly or using GUI
4. Start connecty
## Install python on Windows
#### Install Python
Get the installer [here](https://www.python.org/downloads/).
Although you installed python, you will not run python directly, but use the cmd/terminal/powershell

## Install python on Debian
Get python 3 through your package manager
```
sudo apt-get install python3
```
## Install Connecty
Install connecty
```
python3 -m pip install connecty
```

## Manual Setup
### Create a config file
Save a new text file with your config. You can save it anywhere on your computer.
The file must be in the .ini format and contain your token and all your connections.
 ```ini
[BOT]
token = tokengoeshere

[my_connection_1]
channels = 123456789 123456789 123456789

[my_connection_2]
channels = 123456789 123456789 123456789
```
The first section should be called `[BOT]` and contain your token.
Each subsequent section is a different connection.
The exact name doesn't matter so name them something memorable.

### Run the bot
Run this command in cmd/terminal
 ```
python3 -m connecty path/to/config.ini
 ```

## GUI Setup
Run this command in cmd/terminal
 ```
python3 -m connecty
 ```
The window below will appear

![](https://i.imgur.com/3kzbFIq.png)

This lets you manage your config file and run the bot. Start by clicking the `New` button and
choosing a file to save to. Enter a name for your first connection into box `A` and click the `Add` button above it.
Enter the channel ID for your first channel into box `C` and click the `Add` button above it.
Select an existing connection by picking it from box `B`. Select an existing channel by picking it from box `D`. 
Into box `F` enter your token. Finally click the `Run` button.
Second time you run the bot, click the `Load` button and select the file you saved earlier.

## GUI + Manual Setup
Use the `-i` flag to open the GUI with a config file already loaded.
 ```
python3 -m connecty path/to/config.ini -i
 ```