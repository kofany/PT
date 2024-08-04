# PTbot - IRC Bot with Moderation Features

PTbot is an advanced IRC bot written in Python, designed to assist in managing IRC channels. The bot offers a range of moderation and administrative features, allowing for effective management of the community on IRC channels.

## Main Features

- User management (adding/removing voices and masters)
- Channel moderation (ban, kick, warnings)
- Changing channel settings (topic, modes)
- Warning system with automatic bans
- Support for multiple channels
- IPv4 and IPv6 support
- Automatic reconnection and rejoining channels

## Requirements

- Python 3.6+
- irc
- chardet

## Installation

### 1. Clone the repository:

```bash
git clone https://github.com/kofany/PT.git
cd PT
```
### 2. Install required dependencies:
```bash
pip install irc chardet
```
### 3. Configure the bot by editing the config.json file:
```json
{
    "server": {
        "host": "irc.your-server.com",
        "port": 6667
    },
    "bind_ip": "0.0.0.0",
    "nickname": "OpBot",
    "channels": ["#channel1", "#channel2"],
    "owners": ["*!*owner@example.com"],
    "voices_file": "voices.json",
    "masters_file": "masters.json",
    "warns_file": "warns.json"
}
```
### 4. Running
To start the bot, execute:

```bash
python3 ptbot.py
```
### 5. Available Commands
.add <nick> - Add a user to the voice list
.del <nick> - Remove a user from the voice list
.list - Show the list of voiced users
.addm <nick> - Add a user to the master list
.delm <nick> - Remove a user from the master list
.ban <nick> - Ban a user
.unban <mask> - Unban a user
.kick <nick> - Kick a user from the channel
.warn <nick> - Warn a user
.topic <text> - Set the channel topic
.block - Set the channel to invite-only and moderated mode
.unblock - Remove invite-only and moderated mode
.silence - Silence the channel
.unsilence - Remove channel silence
Contributing

If you want to contribute to the project, feel free to report issues or create pull requests. All contributions are welcome!

