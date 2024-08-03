# IRC Bot Commands

This IRC bot provides various channel management commands. Here's a list of available commands and their usage:

## Command List

### `.add <nick>`
- **Who can use**: Owners and masters
- **Action**: Adds a user to the voice list. The bot performs a WHOIS on the given nick to obtain the full hostmask, adds them to the voice list, and gives them voice (+v) status on the channel.

### `.del <nick>`
- **Who can use**: Owners and masters
- **Action**: Removes a user from the voice list. If the user is an owner, the command is ignored.

### `.list`
- **Who can use**: Owners and masters
- **Action**: Displays a list of all voiced users.

### `.ban <nick>`
- **Who can use**: Owners and masters
- **Action**: Bans a user from the channel. The bot performs a WHOIS on the given nick to obtain the hostmask and then applies a ban on *!*@host.

### `.unban <mask>`
- **Who can use**: Owners and masters
- **Action**: Removes a ban with the specified mask from the channel.

### `.voice <nick>`
- **Who can use**: Owners and masters
- **Action**: Gives voice (+v) status to a user on the channel.

### `.devoice <nick>`
- **Who can use**: Owners and masters
- **Action**: Removes voice (-v) status from a user on the channel. If the user is an owner, the command is ignored.

### `.kick <nick>`
- **Who can use**: Owners and masters
- **Action**: Kicks a user from the channel. The bot performs a WHOIS on the given nick to ensure it's not a protected user.

### `.topic <text>`
- **Who can use**: Owners, masters, and voiced users
- **Action**: Sets a new channel topic.

### `.block`
- **Who can use**: Owners and masters
- **Action**: Sets the channel to invite-only (+i) and moderated (+m) mode.

### `.unblock`
- **Who can use**: Owners and masters
- **Action**: Removes invite-only (-i) and moderated (-m) mode from the channel.

### `.silence`
- **Who can use**: Owners and masters
- **Action**: Sets the channel to moderated (+m) mode.

### `.unsilence`
- **Who can use**: Owners and masters
- **Action**: Removes moderated (-m) mode from the channel.

### `.help`
- **Who can use**: Owners and masters
- **Action**: Displays a list of available commands with a brief description.

### `.warn <nick>`
- **Who can use**: Owners, masters, and voiced users
- **Action**: Warns a user. Here's a detailed description of the mechanism:
  1. The bot checks if the user issuing the command has the appropriate permissions.
  2. It performs a WHOIS on the given nick to obtain the full hostmask of the user.
  3. It checks if the warned user is not protected (owner or master).
  4. If the user is not protected, the bot checks if there's already a warning for this hostmask:
     - If there's no previous warning, the bot records a new warning with the current time and information about who issued it.
     - If there's a previous warning, the bot checks if more than 15 minutes have passed since the previous warning:
       * If less than 15 minutes have passed, the bot updates the existing warning with the new time and information about who issued it.
       * If more than 15 minutes have passed, the bot applies a ban on the user's *!*@host, kicks them from the channel, and removes the warning from the list.
  5. The bot saves the current state of warnings to the warns.txt file.
  6. The bot informs the channel about the warning issued or the ban applied, depending on the situation.

Warnings are stored in the bot's memory and saved to a file, allowing them to be maintained even after the bot restarts. This mechanism provides a gradual escalation of consequences for users violating channel rules, giving them a chance to improve before a ban is applied.

