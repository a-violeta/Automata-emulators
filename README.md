# Emulatoare pentru automate
Program în lucru, scris în Python și menit să emuleze funcționalitățile **automatului finit determinist**, **automatului finit nedeterminist**, al **automatului push-down** și a unei **mașini Turing**. Programul se bazează pe o anumită formatare a fișierului de intrare (fișier cu regulile automatului), asemenea unui limbaj de programare propriu.

## Instalare
```bash
git clone https://github.com/a-violeta/Automata-emulators.git
cd Automata-emulators
```

## Utilizare
## Exemplu
Puteți insera la sfârșitul fișierului `src/automata_emulators.py` liniile:
```python
    emulate_dfa("fisier_dfa.txt")
    emulate_nfa("fisier_nfa.txt")
```
Apoi rulați:
```bash
python automata_emulators.py
```

## Functionalități
- emulare automat finit determinist utilizând funcții
- emulare automat finit nedeterminist utilizând funcții
- citire automat push-down din fișier și transformare în dicționar de stări și reguli
