# Komendy Bota IRC

Ten bot IRC oferuje różne komendy do zarządzania kanałem. Oto lista dostępnych komend i ich zastosowanie:

## Lista komend

### `.add <nick>`
- **Kto może używać**: Właściciele i masterzy
- **Działanie**: Dodaje użytkownika do listy głosów. Bot wykonuje WHOIS na podanym nicku, aby uzyskać pełny hostmask, dodaje go do listy głosów i nadaje mu status voice (+v) na kanale.

### `.del <nick>`
- **Kto może używać**: Właściciele i masterzy
- **Działanie**: Usuwa użytkownika z listy głosów. Jeśli użytkownik jest właścicielem, komenda jest ignorowana.

### `.list`
- **Kto może używać**: Właściciele i masterzy
- **Działanie**: Wyświetla listę wszystkich użytkowników z głosem.

### `.ban <nick>`
- **Kto może używać**: Właściciele i masterzy
- **Działanie**: Banuje użytkownika na kanale. Bot wykonuje WHOIS na podanym nicku, aby uzyskać hostmask, a następnie nakłada bana na *!*@host.

### `.unban <maska>`
- **Kto może używać**: Właściciele i masterzy
- **Działanie**: Zdejmuje bana o podanej masce z kanału.

### `.voice <nick>`
- **Kto może używać**: Właściciele i masterzy
- **Działanie**: Nadaje status voice (+v) użytkownikowi na kanale.

### `.devoice <nick>`
- **Kto może używać**: Właściciele i masterzy
- **Działanie**: Odbiera status voice (-v) użytkownikowi na kanale. Jeśli użytkownik jest właścicielem, komenda jest ignorowana.

### `.kick <nick>`
- **Kto może używać**: Właściciele i masterzy
- **Działanie**: Wyrzuca użytkownika z kanału. Bot wykonuje WHOIS na podanym nicku, aby upewnić się, że nie jest to chroniony użytkownik.

### `.topic <tekst>`
- **Kto może używać**: Właściciele, masterzy i użytkownicy z głosem
- **Działanie**: Ustawia nowy temat kanału.

### `.block`
- **Kto może używać**: Właściciele i masterzy
- **Działanie**: Ustawia kanał w tryb tylko na zaproszenie (+i) i moderowany (+m).

### `.unblock`
- **Kto może używać**: Właściciele i masterzy
- **Działanie**: Usuwa tryb tylko na zaproszenie (-i) i moderowany (-m) z kanału.

### `.silence`
- **Kto może używać**: Właściciele i masterzy
- **Działanie**: Ustawia kanał w tryb moderowany (+m).

### `.unsilence`
- **Kto może używać**: Właściciele i masterzy
- **Działanie**: Usuwa tryb moderowany (-m) z kanału.

### `.help`
- **Kto może używać**: Właściciele i masterzy
- **Działanie**: Wyświetla listę dostępnych komend wraz z krótkim opisem.

### `.warn <nick>`
- **Kto może używać**: Właściciele, masterzy i użytkownicy z głosem
- **Działanie**: Ostrzega użytkownika. Oto szczegółowy opis mechanizmu:
  1. Bot sprawdza, czy użytkownik wydający komendę ma odpowiednie uprawnienia.
  2. Wykonuje WHOIS na podanym nicku, aby uzyskać pełny hostmask użytkownika.
  3. Sprawdza, czy ostrzegany użytkownik nie jest chroniony (właściciel lub master).
  4. Jeśli użytkownik nie jest chroniony, bot sprawdza, czy istnieje już ostrzeżenie dla tego hostmaska:
     - Jeśli nie ma wcześniejszego ostrzeżenia, bot zapisuje nowe ostrzeżenie z aktualnym czasem i informacją o tym, kto je wydał.
     - Jeśli istnieje wcześniejsze ostrzeżenie, bot sprawdza, czy minęło więcej niż 15 minut od poprzedniego ostrzeżenia:
       * Jeśli minęło mniej niż 15 minut, bot aktualizuje istniejące ostrzeżenie z nowym czasem i informacją o tym, kto je wydał.
       * Jeśli minęło więcej niż 15 minut, bot nakłada bana na *!*@host użytkownika, wyrzuca go z kanału i usuwa ostrzeżenie z listy.
  5. Bot zapisuje aktualny stan ostrzeżeń do pliku warns.txt.
  6. Bot informuje kanał o wydaniu ostrzeżenia lub o nałożeniu bana, w zależności od sytuacji.

Ostrzeżenia są przechowywane w pamięci bota oraz zapisywane do pliku, co pozwala na ich utrzymanie nawet po restarcie bota. Mechanizm ten zapewnia stopniowanie konsekwencji dla użytkowników naruszających zasady kanału, dając im szansę na poprawę przed nałożeniem bana.
