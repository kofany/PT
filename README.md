# PTbot - Bot IRC z funkcjami moderacyjnymi

PTbot to zaawansowany bot IRC napisany w Pythonie, zaprojektowany do pomocy w zarządzaniu kanałami IRC. Bot oferuje szereg funkcji moderacyjnych i administracyjnych, umożliwiając efektywne zarządzanie społecznością na kanałach IRC.

## Główne funkcje

- Zarządzanie użytkownikami (dodawanie/usuwanie głosów i masterów)
- Moderacja kanału (ban, kick, ostrzeżenia)
- Zmiana ustawień kanału (temat, tryby)
- System ostrzeżeń z automatycznym banem
- Obsługa wielu kanałów
- Wsparcie dla IPv4 i IPv6
- Automatyczne ponowne połączenie i dołączanie do kanałów

## Wymagania

- Python 3.6+
- irc
- chardet

## Instalacja

### 1. Sklonuj repozytorium:

```bash
git clone https://github.com/kofany/PT.git
cd PT
```
### 2. Zainstaluj wymagane zależności:
```bash
pip install irc chardet
```
### 3. Skonfiguruj bota, edytując plik `config.json`:
```json
{
    "server": {
        "host": "irc.twoj-serwer.com",
        "port": 6667
    },
    "bind_ip": "0.0.0.0",
    "nickname": "OpBot",
    "channels": ["#kanal1", "#kanal2"],
    "owners": ["*!*owner@example.com"],
    "voices_file": "voices.json",
    "masters_file": "masters.json",
    "warns_file": "warns.json"
}
```

### 4. Uruchomienie
Aby uruchomić bota, wykonaj:
```bash
python3 ptbot.py
``` 
### 5. Dostępne komendy

.add <nick> - Dodaj użytkownika do listy głosów
.del <nick> - Usuń użytkownika z listy głosów
.list - Pokaż listę użytkowników z głosem
.addm <nick> - Dodaj użytkownika do listy masterów
.delm <nick> - Usuń użytkownika z listy masterów
.ban <nick> - Zbanuj użytkownika
.unban <maska> - Odbanuj użytkownika
.kick <nick> - Wyrzuć użytkownika z kanału
.warn <nick> - Ostrzeż użytkownika
.topic <tekst> - Ustaw temat kanału
.block - Ustaw kanał na tryb tylko dla zaproszonych i moderowany
.unblock - Usuń tryb tylko dla zaproszonych i moderowany
.silence - Wycisz kanał
.unsilence - Wyłącz wyciszenie kanału

Współtworzenie
Jeśli chcesz przyczynić się do rozwoju projektu, śmiało zgłaszaj problemy lub twórz pull requesty. Wszelkie kontrybucje są mile widziane!
