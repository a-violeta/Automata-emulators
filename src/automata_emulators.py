def read_dfa(fisier):
       
    dfa = { # dictionar
        "states": [],
        "sigma": [],
        "rules": [],
        "start": [],
        "accept": []
    }
    
    try:
        with open(fisier, 'r') as f:
            
            sectiune = None  # stocheaza sectiunea curenta
            
            for line in f:
                line = line.strip()
                
                if line == "[start]":
                    sectiune = "start"
                elif line == "[accept]":
                    sectiune = "accept"
                elif line == "[states]":
                    sectiune = "states"
                elif line == "[sigma]":
                    sectiune = "sigma"
                elif line == "[rules]":
                    sectiune = "rules"
                elif line == "[end]":        # comentariile se ignora, orice nu e in formatul standard
                    sectiune = None
                elif sectiune:
                    if sectiune == "rules":
                        # reguli sub forma de tuplu (stare, simbol, stare_destinatie)
                        parti = line.split()
                        if len(parti) != 3:
                            print("O regula nu are nr corect de argumente\n")
                            return
                        
                        if parti[0] not in dfa["states"] or parti[1] not in dfa["sigma"] or parti[2] not in dfa["states"]:
                            print("Un simbol al unei reguli este scris gresit\n")
                            return
                        
                        dfa["rules"].append((parti[0], parti[1], parti[2]))
                            
                    else:
                        dfa[sectiune].append(line)
        
        return dfa
    
    except FileNotFoundError:
        print(f"Eroare: Fisierul '{fisier}' nu a fost gasit.")
        return None
    except Exception as e:
        print(f"Eroare: {e}")
        return None

def emulator_dfa(fisier, input):
    
    dfa = read_dfa(fisier)
    
    if dfa:
    
        starea_curenta=dfa['start'][0]
        starea_finala=dfa['accept']
        
        if ' ' in input:
            input = input.split()
        
        for elem in input:
            
            if elem in dfa['sigma']:
                for tranz in dfa['rules']:
                    if tranz[0] == starea_curenta and tranz[1] == elem:

                        starea_curenta = tranz[2]
                        break
                        #else inseamna ca starea nu s a schimbat, din starea asta elem nu duce in nicio noua stare
            else:
                print("Inputul are elemente care nu se afla in alfabet\n")
                return False
                    
        if input and starea_curenta in starea_finala:
            return True;
        return False;
                
    return


def read_nfa(fisier):

    nfa = { # dictionar
        "states": set(),
        "sigma": set(),
        "rules": {},  # dictionar: {(stare, simbol): set(stări_destinație)}
        "start": None,
        "accept": set()
    }

    try:
        with open(fisier, 'r') as f:
            sectiune = None  # stocheaza sectiunea curenta
            
            for line in f:
                line = line.strip()  # elimina spatiile goale
                
                if line == "[start]":
                    sectiune = "start"
                elif line == "[accept]":
                    sectiune = "accept"
                elif line == "[states]":
                    sectiune = "states"
                elif line == "[sigma]":
                    sectiune = "sigma"
                elif line == "[rules]":
                    sectiune = "rules"
                elif line == "[end]":
                    sectiune = None
                elif sectiune:
                    if sectiune == "rules":
                        
                        parti = line.split()
                        if len(parti) != 3:
                            print(f"Eroare: Regula incorectă: {line}")
                            return None
                        
                        stare, simbol, destinatie = parti

                        if stare not in nfa["states"] or (simbol not in nfa["sigma"] and simbol != "epsilon") or destinatie not in nfa["states"]:
                            print(f"Eroare: Simbol invalid in regula: {line}")
                            return None
                        
                        if (stare, simbol) not in nfa["rules"]:
                            nfa["rules"][(stare, simbol)] = set()
                        nfa["rules"][(stare, simbol)].add(destinatie)
                    
                    elif sectiune == "start":
                        nfa["start"] = line  # start este o singură stare
                    
                    elif sectiune == "accept":
                        nfa["accept"].add(line)
                    
                    else:
                        nfa[sectiune].add(line)

        return nfa
    
    except FileNotFoundError:
        print(f"Eroare: Fisierul '{fisier}' nu a fost gasit.")
        return None
    except Exception as e:
        print(f"Eroare: {e}")
        return None

def epsilon_closure(nfa, states):

    closure = set(states)
    stack = list(states)

    while stack:
        state = stack.pop()
        if (state, "epsilon") in nfa["rules"]:
            for next_state in nfa["rules"][(state, "epsilon")]:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)

    return closure

def emulate_nfa(fisier_nfa, input_string):
    
    nfa = read_nfa(fisier_nfa)
    if not nfa:
        return False

    # initializam multimea starilor curente cu epsilon-closure a starii initiale
    current_states = epsilon_closure(nfa, {nfa["start"]})

    for symbol in input_string:
        next_states = set()  # multimea starilor urmatoare

        for state in current_states:
            # cautam tranzitii posibile
            if (state, symbol) in nfa["rules"]:
                next_states.update(nfa["rules"][(state, symbol)])

        # calculam epsilon-closure
        current_states = epsilon_closure(nfa, next_states)

        # daca nu mai avem stari active, inputul nu poate fi acceptat
        if not current_states:
            return False

    # verificam daca cel putin o stare curenta este de acceptare
    return any(state in nfa["accept"] for state in current_states)

def read_pda(fisier):

    pda = { # dictionar
        "states": set(),
        "sigma": set(),
        "rules": set(),  # dictionar: {(stare, simbol, stack_pop): set((stack_push, stari_destinatie))}
        "start": None,
        "accept": set(),
        "stack_alphabet": set()
    }

    try:
        with open(fisier, 'r') as f:
            sectiune = None  # stocheaza sectiunea curenta
            
            for line in f:
                line = line.strip()  # elimina spatiile goale
                
                if line == "[start]":
                    sectiune = "start"
                elif line == "[accept]":
                    sectiune = "accept"
                elif line == "[states]":
                    sectiune = "states"
                elif line == "[sigma]":
                    sectiune = "sigma"
                elif line == "[rules]":
                    sectiune = "rules"
                elif line == "[stack_alphabet]":
                    sectiune = "stack_alphabet"
                elif line == "[end]":
                    sectiune = None
                elif sectiune:
                    if sectiune == "rules":
                        
                        parti = line.split()
                        if len(parti) != 5:
                            print(f"Eroare: Regula incorectă: {line}")
                            return None
                        
                        stare, simbol, stack_pop, stack_push, destinatie = parti
                        simbol = simbol.strip(",")
                        stack_pop = stack_pop.strip(",")

                        if (
                            stare not in pda["states"]
                            or (simbol not in pda["sigma"] and simbol != "epsilon")
                            or destinatie not in pda["states"]
                            or (stack_pop not in pda["stack_alphabet"] and stack_pop != "epsilon")
                            or (stack_push not in pda["stack_alphabet"] and stack_push != "epsilon")
                        ):
                            print(f"Eroare: Simbol invalid in regula: {line}")
                            return None
                        
                        pda["rules"].add((stare, simbol, stack_pop, stack_push, destinatie))
                    
                    elif sectiune == "start":
                        pda["start"] = line
                    
                    elif sectiune == "accept":
                        pda["accept"].add(line)
                    
                    else:
                        pda[sectiune].add(line)
        
        return pda
    
    except FileNotFoundError:
        print(f"Eroare: Fisierul '{fisier}' nu a fost gasit.")
        return None
    except Exception as e:
        print(f"Eroare: {e}")
        return None
 
