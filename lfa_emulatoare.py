def read_dfa(fisier):
    """
    DFA în format:
    [states]
    q0
    q1
    q2
    [end]
    [sigma]
    0
    1
    [end]
    [rules]
    q0 0 q1
    q1 1 q2
    q2 0 q0
    [end]
    
    Returnează un dicționar cu stările, alfabetul și regulile de tranziție.
    """
    
    dfa = {
        "states": [],
        "sigma": [],
        "rules": [],
        "start": [],
        "accept": []
    }
    
    try:
        with open(fisier, 'r') as f:
            sectiune = None  # Stochează secțiunea curentă
            
            for line in f:
                line = line.strip()  # Elimină spațiile goale și newline
                
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
                elif line == "[end]":        # or line=="#" pt comentarii, oricum se ignora orice nu e in formatul standard
                    sectiune = None
                elif sectiune:
                    if sectiune == "rules":
                        # Reguli sub formă de tuplu (stare, simbol, stare_destinatie)
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
        print(f"Eroare: Fișierul '{fisier}' nu a fost găsit.")
        return None
    except Exception as e:
        print(f"Eroare: {e}")
        return None

def emulator_dfa(fisier, input):
    
    dfa=read_dfa(fisier)
    
    if dfa:
    
        starea_curenta=dfa['start'][0]
        starea_finala=dfa['accept']
        #print(starea_curenta)
        #print(starea_finala)
        
        if ' ' in input:
            input=input.split()
            #print(input)
        
        for elem in input:
            #print(elem)
            if elem in dfa['sigma']:
                for tranz in dfa['rules']:
                    if tranz[0] == starea_curenta and tranz[1] == elem:
                        #print(tranz)
                        starea_curenta = tranz[2]
                        break
                        #else inseamna ca starea nu s a schimbat, din starea asta elem nu ma duce in nicio noua stare
            else:
                print("Inputul are elemente care nu se afla in alfabet\n")
                return False
                    
        if input and starea_curenta in starea_finala:
            return True;
        return False;
                
    return


def read_nfa(fisier):
    """
    Citește un NFA dintr-un fișier și returnează un dicționar cu componentele sale.
    """
    nfa = {
        "states": set(),
        "sigma": set(),
        "rules": {},  # Dictionar: {(stare, simbol): set(stări_destinație)}
        "start": None,
        "accept": set()
    }

    try:
        with open(fisier, 'r') as f:
            sectiune = None  # Stochează secțiunea curentă
            
            for line in f:
                line = line.strip()  # Elimină spațiile goale și newline
                
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
                            print(f"Eroare: Simbol invalid în regulă: {line}")
                            return None
                        
                        if (stare, simbol) not in nfa["rules"]:
                            nfa["rules"][(stare, simbol)] = set()
                        nfa["rules"][(stare, simbol)].add(destinatie)
                    
                    elif sectiune == "start":
                        nfa["start"] = line  # Start trebuie să fie o singură stare
                    
                    elif sectiune == "accept":
                        nfa["accept"].add(line)
                    
                    else:
                        nfa[sectiune].add(line)

        return nfa
    
    except FileNotFoundError:
        print(f"Eroare: Fișierul '{fisier}' nu a fost găsit.")
        return None
    except Exception as e:
        print(f"Eroare: {e}")
        return None

def epsilon_closure(nfa, states):
    """
    Calculează epsilon-closure pentru un set de stări.
    """
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
    """
    Simulează un NFA pe baza unui input.
    """
    nfa = read_nfa(fisier_nfa)
    if not nfa:
        return False

    # Inițializăm mulțimea stărilor curente cu epsilon-closure a stării inițiale
    current_states = epsilon_closure(nfa, {nfa["start"]})

    # Parcurgem fiecare simbol din input
    for symbol in input_string:
        next_states = set()  # Mulțimea stărilor următoare

        for state in current_states:
            # Căutăm tranziții posibile pentru simbolul curent
            if (state, symbol) in nfa["rules"]:
                next_states.update(nfa["rules"][(state, symbol)])

        # Calculăm epsilon-closure pentru noile stări
        current_states = epsilon_closure(nfa, next_states)

        # Dacă nu mai avem stări active, inputul nu poate fi acceptat
        if not current_states:
            return False

    # Verificăm dacă cel puțin o stare curentă este de acceptare
    return any(state in nfa["accept"] for state in current_states)

def nfa_sau_dfa_din_regex(input): #asta nu merge
    
    dfa = {
        "states": [],
        "sigma": [],
        "rules": [],
        "start": [],
        "accept": []
    }
    
    for elem in input:
        if elem!='*' and elem!='+' and elem!='(' and elem!=')':
            dfa['sigma'].append(elem);
            
#nu e gata

    return dfa


def read_pda(fisier):

    pda = {
        "states": set(),
        "sigma": set(),
        "rules": set(),  # Dictionar: {(stare, simbol, stack_pop): set((stack_push, stări_destinație))}
        "start": None,
        "accept": set(),
        "stack_alphabet": set()
    }

    try:
        with open(fisier, 'r') as f:
            sectiune = None  # Stochează secțiunea curentă
            
            for line in f:
                line = line.strip()  # Elimină spațiile goale și newline
                
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

                        if stare not in pda["states"] or (simbol not in pda["sigma"] and simbol != "epsilon") or destinatie not in pda["states"] or (stack_pop not in pda["stack_alphabet"] and stack_pop != "epsilon") or (stack_push not in pda["stack_alphabet"] and stack_push != "epsilon"):
                            print(f"Eroare: Simbol invalid în regulă: {line}")
                            return None
                        
                        #if (stare, simbol, stack_pop, stack_push, destinatie) not in pda["rules"]:
                            #pda["rules"][(stare, simbol, stack_pop)] = set()
                        pda["rules"].add((stare, simbol, stack_pop, stack_push, destinatie))
                    
                    elif sectiune == "start":
                        pda["start"] = line  # Start trebuie să fie o singură stare
                    
                    elif sectiune == "accept":
                        pda["accept"].add(line)
                    
                    else:
                        pda[sectiune].add(line)
        #print(pda)
        return pda
    
    except FileNotFoundError:
        print(f"Eroare: Fișierul '{fisier}' nu a fost găsit.")
        return None
    except Exception as e:
        print(f"Eroare: {e}")
        return None
    
def epsilon_closure_pda(pda, stiva, state):
    """
    Greu de zis daca e ok, era de la nfa deci tine stiva pe posibile ramuri, ceea ce pda nu are, dar ar putea merge asa cum un dfa e un nfa
    """
    closure = set(state)
    stack = list(state)

    while stack:
        state = stack.pop()
        #if (state, "epsilon", "epsilon") in pda["rules"]:
        for rule in pda["rules"]:
            if rule[0] == state and rule[1] == "epsilon" and rule[2] == "epsilon":
                #for next_state in pda["rules"][(state, "epsilon", "epsilon")]:
                    #if next_state[1] not in closure: #next_state e pair stack_push si destinatie
                next_state = rule[4]
                stack_push = rule[3]
                closure.add(next_state)
                stack.append(next_state)
                stiva.append(stack_push)
                #print()
        
        for elem in pda["stack_alphabet"]:
            #if(state, "epsilon", elem) in pda["rules"]:
            for rule in pda["rules"]:
                if rule[0] == state and rule[1] == "epsilon" and rule[2] == elem:
                    if stiva[-1] == elem:
                    #for next_state in pda["rules"][(state, "epsilon", elem)]:
                        #if next_state[1] not in closure: #next_state e pair stack_push si destinatie
                        next_state=rule[4]
                        stack_push=rule[3]
                        closure.add(next_state)
                        stack.append(next_state)
                        stiva.pop(elem)
                        stiva.append(stack_push)

    return closure

def emulate_pda(fisier_pda, input_string):
    """
    Simulează un PDA pe baza unui input.
    """
    pda = read_pda(fisier_pda)
    if not pda:
        return False
    
    stiva=[]

    # Inițializăm mulțimea stărilor curente cu epsilon-closure a stării inițiale
    current_states = epsilon_closure_pda(pda, stiva, {pda["start"]})
    #print()
    print(f'Starile curente: {current_states}\n')
    
    

    # Parcurgem fiecare simbol din input
    for symbol in input_string:
        print(f'procesam: {symbol}\n')
        #next_states = set()  # Mulțimea stărilor următoare
        next_state = ""
        for state in current_states:
            print(f'starea curenta este: {state}\n')
            # Căutăm tranziții posibile pentru simbolul curent
            for rule in pda["rules"]:
                print(f'regula curenta: {rule}\n')
                #print(f'{rule[0]} & {state}, {rule[1]} & {symbol}, {rule[2]} & {stiva[-1]}\n')
                #print(f'{pda['rules']}\n')
                if rule[0] == state and rule[1] == symbol:
                    if rule[2] == stiva[-1]:
            #if (state, symbol, stiva[-1]) in pda["rules"]:
                #next_states.update(pda["rules"][(state, symbol, stiva[-1])])
                        next_state = rule[4]
                        current_states.add(next_state)
                        stiva.pop(stiva[-1])
                        if rule[3] != "epsilon":
                            stiva.push(rule[3])
                            print(f'In prezent: {current_states}\n')
                    
                        break
                    else:# rule[2] == 'epsilon':
                        print(f'{rule[4]}\n')
                        next_state = rule[4]
                        current_states.add(next_state)
                        #stiva.pop(stiva[-1])
                        if rule[3] != "epsilon":
                            stiva.append(rule[3])
                            print(f'In prezent: {current_states}\n')
                    
                        break
            print('aici\n')
            
        # Calculăm epsilon-closure pentru noile stări
        print(f"Stari: {current_states}\n")
        current_states = epsilon_closure_pda(pda, stiva, next_state)
        #asta strica treaba
        print(f"Ultimele stari: {current_states}\n")

        # Dacă nu mai avem stări active, inputul nu poate fi acceptat
        if not current_states:
            return False

    # Verificăm dacă cel puțin o stare curentă este de acceptare
    #return any(state in pda["accept"] for state in current_states)
    for state in current_states:
        if state in pda['accept']:
            return True

#turing acum
def read_turing_machine(fisier):
    turing = {
        "states": set(),
        "sigma": set(),
        "directions": set(),
        "rules": [],
        "start": None,
        "accept": set()
    }

    try:
        with open(fisier, 'r') as f:
            sectiune = None  # Stochează secțiunea curentă
            
            for line in f:
                line = line.strip()  # Elimină spațiile goale și newline
                
                if line == "[start]":
                    sectiune = "start"
                elif line == "[accept]":
                    sectiune = "accept"
                elif line == "[states]":
                    sectiune = "states"
                elif line == "[sigma]":
                    sectiune = "sigma"
                elif line == "[directions]":
                    sectiune = "directions"
                elif line == "[rules]":
                    sectiune = "rules"
                elif line == "[end]":
                    sectiune = None
                elif sectiune:
                    if sectiune == "rules":
                        # Reguli sub formă de tuplu (stare, simbol, stare_destinatie, de_scris, directie)
                        parti = line.split()
                        if len(parti) != 5:
                            print("O regula nu are nr corect de argumente\n")
                            return
                        
                        if parti[0] not in turing["states"] or parti[1] not in turing["sigma"] or parti[2] not in turing["states"] or parti[3] not in turing["sigma"] or parti[4] not in turing["directions"]:
                            print("Un simbol al unei reguli este scris gresit\n")
                            print(parti[0], parti[1], parti[2], parti[3], parti[4])
                            return
                        
                        turing["rules"].append((parti[0], parti[1], parti[2], parti[3], parti[4])) #blank sa fie _ sau nimic sau ' '?
                    
                    elif sectiune == "start":
                        turing["start"] = line  # Start trebuie să fie o singură stare
                    
                    elif sectiune == "accept":
                        turing["accept"].add(line)
                    
                    else:
                        turing[sectiune].add(line)

        return turing
    
    except FileNotFoundError:
        print(f"Eroare: Fișierul '{fisier}' nu a fost găsit.")
        return None
    except Exception as e:
        print(f"Eroare: {e}")
        return None
    
def emulator_turing_machine(fisier, banda): #inca nu merge
    
    turing=read_turing_machine(fisier)
    
    if turing:
    
        starea_curenta=turing['start']
        starea_finala=turing['accept']
        
        print(starea_curenta)
        print(starea_finala)
        
        for i in range(len(banda)):
            #print(elem)
            if banda[i] in turing['sigma']:
                for tranz in turing['rules']: #tranz e de forma (stare, simbol, stare_destinatie, de_scris, directie)
                    if tranz[0] == starea_curenta and tranz[1] == banda[i]:
                        #print(tranz)
                        starea_curenta = tranz[2]
                        #se scrie pe banda
                        banda[i]=tranz[3]
                        #se ia directia noua
                        if tranz[4] == 'left' and i>0:
                            i=i-2
                        break
                        #else inseamna ca starea nu s a schimbat, din starea asta elem nu ma duce in nicio noua stare
            else:
                print("Inputul are elemente care nu se afla in alfabet\n")
                return
                    
        if starea_curenta in starea_finala:
            return banda
        print('Nu s a putut\n') #aici ajunge de fiecare data
        return banda
                
    return 'Lipseste turing\n'
    
#print(read_turing_machine("turing_n1+n2_unare.txt")) #pare ok
banda=['1', '1', '1', '+', '1', '1', '1', '1', '$']
print(emulator_turing_machine("turing_n1+n2_unare.txt", banda))

#print(emulate_pda("pda_0^n_1^n.txt", "0011"))

# (1+0)* adica macar un 1 sau mai multi, un zero, si asta se repeta de oricate ori

#result = emulate_nfa("nfa_chatgpt.txt", "00101")
#print("Acceptat" if result else "Respins")


# Testare
#print(emulator_dfa('dfa_antepenultimul.txt', 'aaabb'))

#print(emulator_dfa('joc_dfa_2.txt', 'up left pick_spoon right right down'))

#if emulate_nfa('nfa_mod2_mod3.txt', '00010110'):
    #print('True')
#else:
    #print('False')

#antepenultimul sa fie 1, sa fie lungime para

    