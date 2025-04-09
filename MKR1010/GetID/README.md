# GetID

Dette program udlæser det unikke ID fra MKR WiFi 1010 boardets indbyggede kryptografiske chip (ATECC508A/608A).

Programmet:

1. Initialiserer seriel kommunikation
2. Læser det 9-byte lange serienummer fra chippen
3. Udskriver serienummeret i hexadecimal format via den serielle monitor

Dette ID er unikt for hvert board og kan bruges til identifikation af enheden.
