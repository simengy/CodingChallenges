import re
from collections import Counter
from string import ascii_lowercase
from hangman import is_letter

game = None
candidates = None
unguessed = set(ascii_lowercase)
prevguess = ''

escape = lambda c: c if is_letter(c) else '\\%s' % c
lettercnt = lambda phrase: Counter(c.lower() for c in phrase if is_letter(c))
letterlwr = lambda phrase: [c.lower() for c in phrase if is_letter(c)]
make_let = lambda c: dict(l=c, phrases=0, count=0, pos=[0]*len(game.state), entropy=float('inf'))
def title():
    print("===========")
    print("  Hangman  ")
    print("===========")
    print("\nThis game is running in AI mode.")
    print("Press <Ctrl-c> to quit at any time.")
    input("Press Enter to continue.")

def game_state():
    disp_state = ' '.join(game.state)
    print("\nSecret phrase:", disp_state)
    print("Lives left:", game.lives)
    print("Missed:", game.missed)

def ask(question, is_valid, try_again_msg):
    if question == game.guess_letter_question:
        return _ai_guess()
    # still ask user abt next round
    while True:
        ret = input(question + ' ')
        if is_valid(ret):
            break
        print(try_again_msg)

    if question == game.play_again_question and ret == 'y':
        global candidates
        candidates = None

    return ret

def message(msg):
    print(msg)

def win():
    print("\nYou got the answer!\n")

def lose(phrase):
    print("\nThe answer was:\n%s\n" % phrase)

def goodbye():
    print("\nGoodbye!")

def _ai_guess():
    use_entropy = False
    global candidates
    global unguessed
    global prevguess
    if candidates == None:
        letterize = letterlwr if use_entropy else lettercnt
        candidates = {phrase:letterize(phrase) for phrase in game.phrases}
        unguessed = set(ascii_lowercase)
        prevguess = ''

    wild = '[%s]' % ''.join(unguessed)
    regex = [wild if c == '_' else escape(c) for c in game.state] + ['\Z']
    regex = re.compile(''.join(regex), re.IGNORECASE)

    candidates = {p:candidates[p] for p in candidates if regex.match(p)}
    letters = [make_let(c) for c in unguessed]
    lethash = {let['l']:let for let in letters}

    if use_entropy:
        for phrase in candidates:
            i = 0
            seenbefore = set()
            for c in candidates[phrase]:
                if c not in lethash:
                    continue
                lethash[c]['count'] += 1
                lethash[c]['pos'][i] += 1
                if c not in seenbefore:
                    lethash[c]['phrases'] += 1
                    seenbefore.add(c)
                i += 1
        for let in letters:
            let['entropy'] = sum(count**2 for count in let['pos'])
    else:
        for phrase in candidates:
            del candidates[phrase][prevguess]
            for c in candidates[phrase]:
                lethash[c]['count'] += candidates[phrase][c]
                lethash[c]['phrases'] += 1

    letters.sort(key=lambda let: let['count'], reverse=True)
    if use_entropy:
        letters.sort(key=lambda let: let['entropy'])
    letters.sort(key=lambda let: let['phrases'], reverse=True)

    guess = letters[0]['l']
    unguessed -= set(guess)
    prevguess = guess

    print("Guessing:", guess)
    return guess

