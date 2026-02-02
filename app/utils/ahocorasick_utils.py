import ahocorasick


def build_actree(wordlist):
    actree = ahocorasick.Automaton()
    for index, word in enumerate(wordlist):
        actree.add_word(word[0], (word[0], word[1]))
    actree.make_automaton()
    return actree
