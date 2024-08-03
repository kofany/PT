import irc.bot
import logging
import sched
import time
import fnmatch
from commands import CommandHandler

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class OpBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667, owner_hostmasks=None):
        if owner_hostmasks is None:
            owner_hostmasks = ["*!*yooz@tahio.pl", "*!*kofany@irc.al"]
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.owner_hostmasks = owner_hostmasks
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.command_handler = CommandHandler(self)

    def on_nicknameinuse(self, c, e):
        logging.info("Nickname in use. Trying alternative nick.")
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        logging.info(f"Joined channel: {self.channel}")
        c.join(self.channel)

    def on_privmsg(self, c, e):
        if e.arguments[0].startswith('.'):
            self.handle_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        if e.arguments[0].startswith('.'):
            self.handle_command(e, e.arguments[0])

    def handle_command(self, e, cmd):
        self.command_handler.handle_command(e, cmd)

    def on_whoisuser(self, c, e):
        self.command_handler.handle_whoisuser(c, e)

    def on_join(self, c, e):
        self.command_handler.handle_join(c, e)

    def is_owner(self, source):
        return any(fnmatch.fnmatch(source, hostmask) for hostmask in self.owner_hostmasks)

if __name__ == "__main__":
    server = "94.125.182.253"
    channel = "#tahioN"
    nickname = "testbot"

    logging.info(f"Connecting to {server} as {nickname}")
    bot = OpBot(channel, nickname, server)
    bot.start()
