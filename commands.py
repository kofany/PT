import fnmatch
import logging
import time
from datetime import datetime, timedelta

class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
        self.voices = {}
        self.masters = {}
        self.warns = {}
        self.current_command = None
        self.ban_target = None
        self.kick_target = None
        self.warn_target = None
        self.load_voices()
        self.load_masters()
        self.load_warns()

    def handle_command(self, e, cmd):
        source = e.source
        c = self.bot.connection
        nick = e.source.nick
        is_owner = self.bot.is_owner(str(source))
        is_master = nick in self.masters
        is_voice = nick in self.voices

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
            if command == ".topic" or command == ".warn":
                if is_owner or is_master or is_voice:
                    command_map[command](c, nick, args, is_owner, is_master, is_voice)
                else:
                    c.privmsg(self.bot.channel, f"{nick}, nie masz uprawnień do użycia tej komendy.")
            elif is_owner or is_master:
                command_map[command](c, nick, args, is_owner, is_master, is_voice)
            else:
                c.privmsg(self.bot.channel, f"{nick}, nie masz uprawnień do użycia tej komendy.")

    def add_voice(self, c, nick, args, is_owner, is_master, is_voice):
        if is_owner or is_master:
            self.current_command = ".add"
            c.whois(args.strip())

    def del_voice(self, c, nick, args, is_owner, is_master, is_voice):
        if is_owner or is_master:
            del_voice = args.strip()
            if self.is_owner_hostmask(self.get_hostmask(del_voice)):
                c.privmsg(self.bot.channel, f"{nick}, nie możesz usunąć głosu {del_voice}, ponieważ jest to właściciel.")
            elif del_voice in self.voices:
                del self.voices[del_voice]
                self.save_voices()
                c.privmsg(self.bot.channel, f"{del_voice} został usunięty z listy głosów.")
            else:
                c.privmsg(self.bot.channel, f"{del_voice} nie znaleziono na liście głosów.")

    def list_voices(self, c, nick, args, is_owner, is_master, is_voice):
        if is_owner or is_master:
            if self.voices:
                voices_list = ', '.join(self.voices.keys())
                c.privmsg(self.bot.channel, f"Aktualne głosy: {voices_list}")
            else:
                c.privmsg(self.bot.channel, "Nie ma głosów na liście.")

    def add_master(self, c, nick, args, is_owner, is_master, is_voice):
        if is_owner:
            self.current_command = ".addm"
            c.whois(args.strip())

    def del_master(self, c, nick, args, is_owner, is_master, is_voice):
        if is_owner:
            del_master = args.strip()
            if self.is_owner_hostmask(self.get_hostmask(del_master)):
                c.privmsg(self.bot.channel, f"{nick}, nie możesz usunąć {del_master} z listy masterów, ponieważ jest to właściciel.")
            elif del_master in self.masters:
                del self.masters[del_master]
                self.save_masters()
                c.mode(self.bot.channel, f"-v {del_master}")
                c.privmsg(self.bot.channel, f"{del_master} został usunięty z listy masterów.")
            else:
                c.privmsg(self.bot.channel, f"{del_master} nie znaleziono na liście masterów.")

    def ban_user(self, c, nick, args, is_owner, is_master, is_voice):
        if is_owner or is_master:
            ban_nick = args.strip()
            self.current_command = ".ban"
            self.ban_target = ban_nick
            c.whois(ban_nick)

    def unban_user(self, c, nick, args, is_owner, is_master, is_voice):
        if is_owner or is_master:
            unban_mask = args.strip()
            c.mode(self.bot.channel, f"-b {unban_mask}")
            c.privmsg(self.bot.channel, f"Odbanowano {unban_mask}")

    def voice_user(self, c, nick, args, is_owner, is_master, is_voice):
        if is_owner or is_master:
            voice_nick = args.strip()
            c.mode(self.bot.channel, f"+v {voice_nick}")

    def devoice_user(self, c, nick, args, is_owner, is_master, is_voice):
        if is_owner or is_master:
            devoice_nick = args.strip()
            if self.is_owner_hostmask(self.get_hostmask(devoice_nick)):
                c.privmsg(self.bot.channel, f"{nick}, nie możesz odebrać głosu {devoice_nick}, ponieważ jest to właściciel.")
            else:
                c.mode(self.bot.channel, f"-v {devoice_nick}")

    def kick_user(self, c, nick, args, is_owner, is_master, is_voice):
        if is_owner or is_master:
            kick_nick = args.strip()
            self.current_command = ".kick"
            self.kick_target = kick_nick
            c.whois(kick_nick)

    def set_topic(self, c, nick, args, is_owner, is_master, is_voice):
        if is_owner or is_master or is_voice:
            topic = args.strip()
            c.topic(self.bot.channel, f"{topic} (ustawione przez {nick})")

    def list_masters(self, c, nick, args, is_owner, is_master, is_voice):
        if is_owner:
            if self.masters:
                masters_list = ', '.join(self.masters.keys())
                c.privmsg(self.bot.channel, f"Aktualni masterzy: {masters_list}")
            else:
                c.privmsg(self.bot.channel, "Nie ma masterów na liście.")

    def block_channel(self, c, nick, args, is_owner, is_master, is_voice):
        if is_owner or is_master:
            c.mode(self.bot.channel, "+mi")
            c.privmsg(self.bot.channel, "Kanał jest teraz tylko na zaproszenie i moderowany.")

    def unblock_channel(self, c, nick, args, is_owner, is_master, is_voice):
        if is_owner or is_master:
            c.mode(self.bot.channel, "-mi")
            c.privmsg(self.bot.channel, "Kanał nie jest już tylko na zaproszenie ani moderowany.")

    def silence_channel(self, c, nick, args, is_owner, is_master, is_voice):
        if is_owner or is_master:
            c.mode(self.bot.channel, "+m")
            c.privmsg(self.bot.channel, "Kanał jest teraz moderowany.")

    def unsilence_channel(self, c, nick, args, is_owner, is_master, is_voice):
        if is_owner or is_master:
            c.mode(self.bot.channel, "-m")
            c.privmsg(self.bot.channel, "Kanał nie jest już moderowany.")

    def op_user(self, c, nick, args, is_owner, is_master, is_voice):
        if is_owner:
            c.mode(self.bot.channel, f"+o {nick}")

    def show_help(self, c, nick, args, is_owner, is_master, is_voice):
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

    def warn_user(self, c, nick, args, is_owner, is_master, is_voice):
        # Nie musimy ponownie sprawdzać, czy użytkownik jest w self.voices,
        # ponieważ is_voice jest już przekazywane jako argument

        if not (is_owner or is_master or is_voice):
            c.privmsg(self.bot.channel, f"{nick}, nie masz uprawnień do użycia tej komendy.")
            return

        target_nick = args.strip()
        if not target_nick:
            c.privmsg(self.bot.channel, f"{nick}, musisz podać nick użytkownika do ostrzeżenia.")
            return

        self.current_command = ".warn"
        self.warn_target = nick  # Zapisujemy nick osoby wydającej ostrzeżenie
        c.whois(target_nick)

    def handle_whoisuser(self, c, e):
        nick = e.arguments[0]
        ident = e.arguments[1]
        host = e.arguments[2]
        full_hostmask = f"{nick}!{ident}@{host}"

        if self.current_command == ".ban":
            if self.is_owner_hostmask(full_hostmask):
                c.privmsg(self.bot.channel, f"Nie można zbanować {nick}, ponieważ jest to właściciel.")
            elif self.is_protected(full_hostmask):
                c.privmsg(self.bot.channel, f"Nie można zbanować {nick}, ponieważ jest to chroniony użytkownik.")
            elif not self.is_bannable(full_hostmask, self.bot.is_owner(str(e.source))):
                c.privmsg(self.bot.channel, f"Nie masz uprawnień do zbanowania {nick}.")
            else:
                ban_mask = f"*!*@{host}"
                c.mode(self.bot.channel, f"+b {ban_mask}")
                c.kick(self.bot.channel, nick, "Zostałeś zbanowany!")

        elif self.current_command == ".kick":
            if self.is_owner_hostmask(full_hostmask):
                c.privmsg(self.bot.channel, f"Nie można wyrzucić {nick}, ponieważ jest to właściciel.")
            elif self.is_protected(full_hostmask):
                c.privmsg(self.bot.channel, f"Nie można wyrzucić {nick}, ponieważ jest to chroniony użytkownik.")
            elif not self.is_bannable(full_hostmask, self.bot.is_owner(str(e.source))):
                c.privmsg(self.bot.channel, f"Nie masz uprawnień do wyrzucenia {nick}.")
            else:
                c.kick(self.bot.channel, nick)

        elif self.current_command == ".addm":
            if nick not in self.masters and not self.is_owner_hostmask(full_hostmask):
                self.masters[nick] = full_hostmask
                self.save_masters()
                c.privmsg(self.bot.channel, f"{nick} został dodany do listy masterów.")
            if nick not in self.voices:
                self.voices[nick] = full_hostmask
                c.mode(self.bot.channel, f"+v {nick}")
                self.save_voices()
                c.privmsg(self.bot.channel, f"{nick} został dodany do listy głosów.")

        elif self.current_command == ".add":
            if nick not in self.voices:
                self.voices[nick] = full_hostmask
                c.mode(self.bot.channel, f"+v {nick}")
                self.save_voices()
                c.privmsg(self.bot.channel, f"{nick} został dodany do listy głosów.")

        elif self.current_command == ".warn":
            if self.is_protected(full_hostmask):
                c.privmsg(self.bot.channel, f"Nie można ostrzec {nick}, ponieważ jest to chroniony użytkownik.")
            else:
                self.process_warn(c, nick, full_hostmask)

        self.current_command = None
        self.ban_target = None
        self.kick_target = None
        self.warn_target = None

    def process_warn(self, c, target_nick, full_hostmask):
        current_time = datetime.now()
        if full_hostmask in self.warns:
            last_warn_time = datetime.fromtimestamp(self.warns[full_hostmask]['time'])
            if current_time - last_warn_time > timedelta(minutes=15):
                # Drugi warn po ponad 15 minutach
                c.mode(self.bot.channel, f"+b *!*{full_hostmask.split('!')[1]}")
                c.kick(self.bot.channel, target_nick, "Drugie ostrzeżenie")
                del self.warns[full_hostmask]
                c.privmsg(self.bot.channel, f"{target_nick} otrzymał drugie ostrzeżenie i został zbanowany.")
            else:
                # Aktualizacja istniejącego warna
                self.warns[full_hostmask] = {'time': current_time.timestamp(), 'by': self.warn_target}
                c.privmsg(self.bot.channel, f"{target_nick} otrzymał kolejne ostrzeżenie.")
        else:
            # Pierwszy warn
            self.warns[full_hostmask] = {'time': current_time.timestamp(), 'by': self.warn_target}
            c.privmsg(self.bot.channel, f"{target_nick} otrzymał pierwsze ostrzeżenie.")
        
        self.save_warns()

    def handle_join(self, c, e):
        nick = e.source.nick
        for stored_nick, hostmask in self.voices.items():
            if fnmatch.fnmatch(e.source, hostmask):
                c.mode(self.bot.channel, f"+v {nick}")

    def save_voices(self):
        with open('voices.txt', 'w') as f:
            for nick, hostmask in self.voices.items():
                f.write(f"{nick} {hostmask}\n")

    def load_voices(self):
        try:
            with open('voices.txt', 'r') as f:
                for line in f:
                    nick, hostmask = line.strip().split(None, 1)
                    self.voices[nick] = hostmask
        except FileNotFoundError:
            pass

    def save_masters(self):
        with open('masters.txt', 'w') as f:
            for nick, hostmask in self.masters.items():
                f.write(f"{nick} {hostmask}\n")

    def load_masters(self):
        try:
            with open('masters.txt', 'r') as f:
                for line in f:
                    nick, hostmask = line.strip().split(None, 1)
                    self.masters[nick] = hostmask
        except FileNotFoundError:
            pass

    def save_warns(self):
        with open('warns.txt', 'w') as f:
            for hostmask, warn_data in self.warns.items():
                f.write(f"{hostmask}|{warn_data['time']}|{warn_data['by']}\n")

    def load_warns(self):
        try:
            with open('warns.txt', 'r') as f:
                for line in f:
                    hostmask, warn_time, warn_by = line.strip().split('|')
                    self.warns[hostmask] = {'time': float(warn_time), 'by': warn_by}
        except FileNotFoundError:
            pass

    def is_owner_hostmask(self, hostmask):
        return any(fnmatch.fnmatch(hostmask, owner_mask) for owner_mask in self.bot.owner_hostmasks)

    def is_protected(self, hostmask):
        return self.is_owner_hostmask(hostmask) or hostmask in self.masters.values()

    def is_bannable(self, hostmask, is_owner):
        return not self.is_protected(hostmask) and (is_owner or hostmask not in self.masters.values())

    def get_hostmask(self, nick):
        return self.masters.get(nick) or self.voices.get(nick)
