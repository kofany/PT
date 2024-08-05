import irc.bot
import irc.connection
import logging
import sched
import time
import fnmatch
from commands import CommandHandler
import chardet
import json
import socket

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def decode_irc(data):
    if isinstance(data, bytes):
        result = chardet.detect(data)
        return data.decode(result['encoding'], errors='replace')
    return data

class CaseInsensitiveSingleServerIRCBot(irc.bot.SingleServerIRCBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channels = irc.bot.IRCDict()

    def on_join(self, c, e):
        ch = e.target.lower()
        nick = e.source.nick
        if ch not in self.channels:
            self.channels[ch] = irc.bot.Channel()
        self.channels[ch].add_user(nick)

class OpBot(CaseInsensitiveSingleServerIRCBot):
    def __init__(self, config_file='config.json'):
        self.load_config(config_file)
        
        # Sprawdzenie, czy bind_ip jest adresem IPv6
        if ':' in self.config['bind_ip']:
            factory = irc.connection.Factory(bind_address=(self.config['bind_ip'], 0), ipv6=True)
        else:
            factory = irc.connection.Factory(bind_address=(self.config['bind_ip'], 0))

        CaseInsensitiveSingleServerIRCBot.__init__(self, 
                                            [(self.config['server']['host'], self.config['server']['port'])], 
                                            self.config['nickname'], 
                                            self.config['nickname'],
                                            connect_factory=factory)
        
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.command_handler = CommandHandler(self)

    def load_config(self, config_file):
        with open(config_file, 'r') as f:
            self.config = json.load(f)

    def on_nicknameinuse(self, c, e):
        logging.info("Nickname in use. Trying alternative nick.")
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        self.join_channels(c)

    def join_channels(self, c):
        for channel in self.config['channels']:
            logging.info(f"Joining channel: {channel}")
            c.join(channel)
            self.channels[channel.lower()] = irc.bot.Channel()

    def on_disconnect(self, c, e):
        logging.info("Disconnected. Attempting to reconnect...")
        self.jump_server()

    def on_connect(self, c, e):
        logging.info("Connected to server. Joining channels...")
        self.join_channels(c)

    def on_privmsg(self, c, e):
        if e.arguments[0].startswith('.'):
            self.handle_command(e, decode_irc(e.arguments[0]))

    def on_pubmsg(self, c, e):
        if e.arguments[0].startswith('.'):
            self.handle_command(e, decode_irc(e.arguments[0]))

    def handle_command(self, e, cmd):
        self.command_handler.handle_command(e, cmd)

    def on_whoisuser(self, c, e):
        self.command_handler.handle_whoisuser(c, e)

    def on_join(self, c, e):
        super().on_join(c, e)
        channel = e.target.lower()
        nick = e.source.nick
        if nick != c.get_nickname():
            self.command_handler.handle_join(c, e)

    def is_owner(self, source):
        return any(fnmatch.fnmatch(source, hostmask) for hostmask in self.config['owners'])

if __name__ == "__main__":
    # Ustawienie dekodera dla buforów IRC
    irc.client.ServerConnection.buffer_class.encoding = 'utf-8'
    irc.client.ServerConnection.buffer_class.errors = 'replace'
    irc.client.ServerConnection.buffer_class.decode = staticmethod(decode_irc)

    # Włączenie obsługi IPv6
    if socket.has_ipv6:
        irc.client.inet_pton = socket.inet_pton

    bot = OpBot()
    bot.start()
