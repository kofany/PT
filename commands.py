import fnmatch
import logging
import time
from datetime import datetime, timedelta
import json

class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
        self.voices = self.load_json(self.bot.config['voices_file'])
        self.masters = self.load_json(self.bot.config['masters_file'])
        self.warns = self.load_json(self.bot.config['warns_file'])
        self.current_command = None
        self.current_channel = None
        self.target_nick = None

    def load_json(self, filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_json(self, data, filename):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    def handle_command(self, e, cmd):
        source = e.source
        c = self.bot.connection
        nick = e.source.nick
        channel = e.target
        is_owner = self.bot.is_owner(str(source))
        is_master = self.is_master(nick, channel)
        is_voice = self.is_voice(nick, channel)

        cmd_parts = cmd.split(None, 1)
        command = cmd_parts[0].lower()
        args = cmd_parts[1] if len(cmd_parts) > 1 else ""

        command_map = {
            ".add": self.add_voice,
            ".del": self.del_voice,
            ".list": self.list_voices,
            ".addm": self.add_master,
            ".delm": self.del_master,
            ".ban": self.ban_user,
            ".unban": self.unban_user,
            ".voice": self.voice_user,
            ".devoice": self.devoice_user,
            ".kick": self.kick_user,
            ".topic": self.set_topic,
            ".listm": self.list_masters,
            ".block": self.block_channel,
            ".unblock": self.unblock_channel,
            ".silence": self.silence_channel,
            ".unsilence": self.unsilence_channel,
            ".op": self.op_user,
            ".help": self.show_help,
            ".warn": self.warn_user,
        }

        if command in command_map:
            if command in [".topic", ".warn"]:
                if is_owner or is_master or is_voice:
                    command_map[command](c, nick, args, channel, is_owner, is_master, is_voice)
                else:
                    c.privmsg(channel, f"{nick}, nie masz uprawnień do użycia tej komendy.")
            elif is_owner or is_master:
                command_map[command](c, nick, args, channel, is_owner, is_master, is_voice)
            else:
                c.privmsg(channel, f"{nick}, nie masz uprawnień do użycia tej komendy.")

    def is_master(self, nick, channel):
        return channel in self.masters and nick in self.masters[channel]

    def is_voice(self, nick, channel):
        return channel in self.voices and nick in self.voices[channel]

    def add_voice(self, c, nick, args, channel, is_owner, is_master, is_voice):
        if is_owner or is_master:
            self.current_command = ".add"
            self.current_channel = channel
            self.target_nick = args.strip()
            c.whois([self.target_nick])

    def del_voice(self, c, nick, args, channel, is_owner, is_master, is_voice):
        if is_owner or is_master:
            del_voice = args.strip()
            if self.is_owner_hostmask(self.get_hostmask(del_voice, channel)):
                c.privmsg(channel, f"{nick}, nie możesz usunąć głosu {del_voice}, ponieważ jest to właściciel.")
            elif channel in self.voices and del_voice in self.voices[channel]:
                del self.voices[channel][del_voice]
                self.save_voices()
                c.privmsg(channel, f"{del_voice} został usunięty z listy głosów.")
            else:
                c.privmsg(channel, f"{del_voice} nie znaleziono na liście głosów.")

    def list_voices(self, c, nick, args, channel, is_owner, is_master, is_voice):
        if is_owner or is_master:
            if channel in self.voices and self.voices[channel]:
                voices_list = ', '.join(self.voices[channel].keys())
                c.privmsg(channel, f"Aktualne głosy: {voices_list}")
            else:
                c.privmsg(channel, "Nie ma głosów na liście.")

    def add_master(self, c, nick, args, channel, is_owner, is_master, is_voice):
        if is_owner:
            self.current_command = ".addm"
            self.current_channel = channel
            self.target_nick = args.strip()
            c.whois([self.target_nick])

    def del_master(self, c, nick, args, channel, is_owner, is_master, is_voice):
        if is_owner:
            del_master = args.strip()
            if self.is_owner_hostmask(self.get_hostmask(del_master, channel)):
                c.privmsg(channel, f"{nick}, nie możesz usunąć {del_master} z listy masterów, ponieważ jest to właściciel.")
            elif channel in self.masters and del_master in self.masters[channel]:
                del self.masters[channel][del_master]
                self.save_masters()
                c.mode(channel, f"-v {del_master}")
                c.privmsg(channel, f"{del_master} został usunięty z listy masterów.")
            else:
                c.privmsg(channel, f"{del_master} nie znaleziono na liście masterów.")

    def ban_user(self, c, nick, args, channel, is_owner, is_master, is_voice):
        if is_owner or is_master:
            self.current_command = ".ban"
            self.current_channel = channel
            self.target_nick = args.strip()
            c.whois([self.target_nick])

    def unban_user(self, c, nick, args, channel, is_owner, is_master, is_voice):
        if is_owner or is_master:
            unban_mask = args.strip()
            c.mode(channel, f"-b {unban_mask}")
            c.privmsg(channel, f"Odbanowano {unban_mask}")

    def voice_user(self, c, nick, args, channel, is_owner, is_master, is_voice):
        if is_owner or is_master:
            voice_nick = args.strip()
            c.mode(channel, f"+v {voice_nick}")

    def devoice_user(self, c, nick, args, channel, is_owner, is_master, is_voice):
        if is_owner or is_master:
            devoice_nick = args.strip()
            if self.is_owner_hostmask(self.get_hostmask(devoice_nick, channel)):
                c.privmsg(channel, f"{nick}, nie możesz odebrać głosu {devoice_nick}, ponieważ jest to właściciel.")
            else:
                c.mode(channel, f"-v {devoice_nick}")

    def kick_user(self, c, nick, args, channel, is_owner, is_master, is_voice):
        if is_owner or is_master:
            self.current_command = ".kick"
            self.current_channel = channel
            self.target_nick = args.strip()
            c.whois([self.target_nick])

    def set_topic(self, c, nick, args, channel, is_owner, is_master, is_voice):
        if is_owner or is_master or is_voice:
            topic = args.strip()
            c.topic(channel, f"{topic} (ustawione przez {nick})")

    def list_masters(self, c, nick, args, channel, is_owner, is_master, is_voice):
        if is_owner:
            if channel in self.masters and self.masters[channel]:
                masters_list = ', '.join(self.masters[channel].keys())
                c.privmsg(channel, f"Aktualni masterzy: {masters_list}")
            else:
                c.privmsg(channel, "Nie ma masterów na liście.")

    def block_channel(self, c, nick, args, channel, is_owner, is_master, is_voice):
        if is_owner or is_master:
            c.mode(channel, "+mi")
            c.privmsg(channel, "Kanał jest teraz tylko na zaproszenie i moderowany.")

    def unblock_channel(self, c, nick, args, channel, is_owner, is_master, is_voice):
        if is_owner or is_master:
            c.mode(channel, "-mi")
            c.privmsg(channel, "Kanał nie jest już tylko na zaproszenie ani moderowany.")

    def silence_channel(self, c, nick, args, channel, is_owner, is_master, is_voice):
        if is_owner or is_master:
            c.mode(channel, "+m")
            c.privmsg(channel, "Kanał jest teraz moderowany.")

    def unsilence_channel(self, c, nick, args, channel, is_owner, is_master, is_voice):
        if is_owner or is_master:
            c.mode(channel, "-m")
            c.privmsg(channel, "Kanał nie jest już moderowany.")

    def op_user(self, c, nick, args, channel, is_owner, is_master, is_voice):
        if is_owner:
            c.mode(channel, f"+o {nick}")

    def show_help(self, c, nick, args, channel, is_owner, is_master, is_voice):
        if is_owner or is_master:
            help_text = (
                "Dostępne komendy:\n"
                ".add <nick> - Dodaj użytkownika do listy głosów (właściciele i masterzy)\n"
                ".del <nick> - Usuń użytkownika z listy głosów (właściciele i masterzy)\n"
                ".list - Lista użytkowników z głosem (właściciele i masterzy)\n"
                ".addm <nick> - Dodaj użytkownika do listy masterów (tylko właściciele)\n"
                ".delm <nick> - Usuń użytkownika z listy masterów (tylko właściciele)\n"
                ".ban <nick> - Zbanuj użytkownika na kanale (właściciele i masterzy)\n"
                ".unban <maska> - Odbanuj użytkownika na kanale (właściciele i masterzy)\n"
                ".voice <nick> - Daj głos użytkownikowi na kanale (właściciele i masterzy)\n"
                ".devoice <nick> - Odbierz głos użytkownikowi na kanale (właściciele i masterzy)\n"
                ".kick <nick> - Wyrzuć użytkownika z kanału (właściciele i masterzy)\n"
                ".topic <tekst> - Ustaw temat kanału (właściciele, masterzy i głosy)\n"
                ".listm - Lista masterów (tylko właściciele)\n"
                ".block - Ustaw kanał na tylko na zaproszenie i moderowany (właściciele i masterzy)\n"
                ".unblock - Usuń tryb tylko na zaproszenie i moderowany z kanału (właściciele i masterzy)\n"
                ".silence - Ustaw kanał w tryb moderowany (właściciele i masterzy)\n"
                ".unsilence - Usuń tryb moderowany z kanału (właściciele i masterzy)\n"
                ".op - Nadaj sobie status operatora (tylko właściciele)\n"
                ".warn <nick> - Ostrzeż użytkownika (właściciele, masterzy i głosy)\n"
            )
            
            for line in help_text.split('\n'):
                if line.strip():
                    c.privmsg(nick, line.strip())

    def warn_user(self, c, nick, args, channel, is_owner, is_master, is_voice):
        if not (is_owner or is_master or is_voice):
            c.privmsg(channel, f"{nick}, nie masz uprawnień do użycia tej komendy.")
            return

        self.current_command = ".warn"
        self.current_channel = channel
        self.target_nick = args.strip()
        if not self.target_nick:
            c.privmsg(channel, f"{nick}, musisz podać nick użytkownika do ostrzeżenia.")
            return
        self.warn_target = nick
        c.whois([self.target_nick])

    def handle_whoisuser(self, c, e):
        nick = e.arguments[0]
        ident = e.arguments[1]
        host = e.arguments[2]
        full_hostmask = f"{nick}!{ident}@{host}"
        channel = self.current_channel

        if nick != self.target_nick:
            return  # Ignoruj odpowiedzi whois dla innych nicków

        if self.current_command == ".ban":
            if self.is_owner_hostmask(full_hostmask):
                c.privmsg(channel, f"Nie można zbanować {nick}, ponieważ jest to właściciel.")
            elif self.is_protected(full_hostmask, channel):
                c.privmsg(channel, f"Nie można zbanować {nick}, ponieważ jest to chroniony użytkownik.")
            elif not self.is_bannable(full_hostmask, channel, self.bot.is_owner(str(e.source))):
                c.privmsg(channel, f"Nie masz uprawnień do zbanowania {nick}.")
            else:
                ban_mask = f"*!*@{host}"
                c.mode(channel, f"+b {ban_mask}")
                c.kick(channel, nick, "Zostałeś zbanowany!")

        elif self.current_command == ".kick":
            if self.is_owner_hostmask(full_hostmask):
                c.privmsg(channel, f"Nie można wyrzucić {nick}, ponieważ jest to właściciel.")
            elif self.is_protected(full_hostmask, channel):
                c.privmsg(channel, f"Nie można wyrzucić {nick}, ponieważ jest to chroniony użytkownik.")
            elif not self.is_bannable(full_hostmask, channel, self.bot.is_owner(str(e.source))):
                c.privmsg(channel, f"Nie masz uprawnień do wyrzucenia {nick}.")
            else:
                c.kick(channel, nick)

        elif self.current_command == ".addm":
            if channel not in self.masters:
                self.masters[channel] = {}
            if nick not in self.masters[channel] and not self.is_owner_hostmask(full_hostmask):
                self.masters[channel][nick] = full_hostmask
                self.save_masters()
                c.privmsg(channel, f"{nick} został dodany do listy masterów.")
            if channel not in self.voices:
                self.voices[channel] = {}
            if nick not in self.voices[channel]:
                self.voices[channel][nick] = full_hostmask
                c.mode(channel, f"+v {nick}")
                self.save_voices()
                c.privmsg(channel, f"{nick} został dodany do listy głosów.")

        elif self.current_command == ".add":
            if channel not in self.voices:
                self.voices[channel] = {}
            if nick not in self.voices[channel]:
                self.voices[channel][nick] = full_hostmask
                c.mode(channel, f"+v {nick}")
                self.save_voices()
                c.privmsg(channel, f"{nick} został dodany do listy głosów.")

        elif self.current_command == ".warn":
            if self.is_protected(full_hostmask, channel):
                c.privmsg(channel, f"Nie można ostrzec {nick}, ponieważ jest to chroniony użytkownik.")
            else:
                self.process_warn(c, nick, full_hostmask, channel)

        self.current_command = None
        self.current_channel = None
        self.target_nick = None

    def process_warn(self, c, target_nick, full_hostmask, channel):
        current_time = datetime.now()
        if channel not in self.warns:
            self.warns[channel] = {}
        
        if full_hostmask in self.warns[channel]:
            last_warn_time = datetime.fromtimestamp(self.warns[channel][full_hostmask]['time'])
            time_since_last_warn = current_time - last_warn_time
            
            if time_since_last_warn > timedelta(minutes=15):
                # Drugi warn po ponad 15 minutach
                c.mode(channel, f"+b *!*{full_hostmask.split('!')[1]}")
                c.kick(channel, target_nick, "Drugie ostrzeżenie")
                del self.warns[channel][full_hostmask]
                c.privmsg(channel, f"{target_nick} otrzymał drugie ostrzeżenie i został zbanowany.")
            else:
                # Ostrzeżenie w ciągu 15 minut
                minutes_ago = int(time_since_last_warn.total_seconds() / 60)
                c.privmsg(channel, f"{target_nick} już otrzymał ostrzeżenie {minutes_ago} minut temu.")
        else:
            # Pierwszy warn
            self.warns[channel][full_hostmask] = {'time': current_time.timestamp(), 'by': self.warn_target}
            c.privmsg(channel, f"{target_nick} otrzymał pierwsze ostrzeżenie.")
        
        self.save_warns()

    def handle_join(self, c, e):
        nick = e.source.nick
        channel = e.target
        if channel in self.voices:
            for stored_nick, hostmask in self.voices[channel].items():
                if fnmatch.fnmatch(str(e.source), hostmask):
                    c.mode(channel, f"+v {nick}")
                    break

    def save_voices(self):
        self.save_json(self.voices, self.bot.config['voices_file'])

    def save_masters(self):
        self.save_json(self.masters, self.bot.config['masters_file'])

    def save_warns(self):
        self.save_json(self.warns, self.bot.config['warns_file'])

    def is_owner_hostmask(self, hostmask):
        return any(fnmatch.fnmatch(hostmask, owner_mask) for owner_mask in self.bot.config['owners'])

    def is_protected(self, hostmask, channel):
        return self.is_owner_hostmask(hostmask) or (channel in self.masters and hostmask in self.masters[channel].values())

    def is_bannable(self, hostmask, channel, is_owner):
        return not self.is_protected(hostmask, channel) and (is_owner or (channel in self.masters and hostmask not in self.masters[channel].values()))

    def get_hostmask(self, nick, channel):
        if channel in self.masters and nick in self.masters[channel]:
            return self.masters[channel][nick]
        elif channel in self.voices and nick in self.voices[channel]:
            return self.voices[channel][nick]
        return None
