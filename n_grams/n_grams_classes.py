from collections import namedtuple

# definisco la classe token, come sottoclasse della tupla, con gli attributi: forma, lemma e pos
Token = namedtuple('Token', ['forma', 'lemma', 'pos'])


class Corpus:
    # oggetto che rappresenta un corpus di documenti, con il metodo get_feature_dicts si possono estrarre i dizionari di feature di ngrammi
    __slots__ = ('docslist', 'resultslist')
    # docslist è la lista di oggetti document
    # resultslist è la lista di risultati


    def __init__(self, docslist: list, resultslist: list) -> None:
        if len(docslist) != len(resultslist):
            raise Exception
        self.docslist = docslist
        self.resultslist = resultslist

    def get_feature_dicts(self, element: str, t_type: str, n_ngram: int) -> list:
        if element == 'lessico':
            return [document.get_word_ngrams(t_type, n_ngram) for document in self.docslist]
        if element == 'carattere':
            return [document.get_char_pref_suff_ngrams(n_ngram) for document in self.docslist]




class Document:
    # oggetto che rappresenta il documento, i suoi metodi permettono di estrarre i dizionari di feature di ngrammi
    __slots__ = 'sentenceslist'
    # sentenceslist è la lista delle frasi del documento, ogni frase sarà un oggetto sentence


    def __init__(self, lineslist: list) -> None:
        sentenceslist = []  # conterrà la lista delle frasi
        tmp_frase = []  # lista d'appoggio
        # iteriamo sulle righe del file conll-u
        for line in lineslist:
            if line[0].isdigit():  # se la riga inizia con un numero significa che contiene una parola
                splitted_line = line.strip().split('\t')
                if '-' not in splitted_line[0]:  # se l'id della parola non contiene un trattino la memorizziamo
                    tmp_frase.append(Token(forma=splitted_line[1],
                                           lemma=splitted_line[2],
                                           pos=splitted_line[3]))
            if line == '\n':  # se la riga è vuota significa che la frase è finita
                sentenceslist.append(Sentence(tmp_frase))
                tmp_frase = []
        self.sentenceslist = sentenceslist

    def get_word_ngrams(self, t_type: str, n_ngram: int) -> dict:
        # estrae gli ngrammi di forma, lemma o pos del documento
        wordcount = 0
        featuredict = {}
        if t_type == 'forma':
            t_label = 'f'
        if t_type == 'lemma':
            t_label = 'l'
        if t_type == 'pos':
            t_label = 'p'
        for sentence in self.sentenceslist:
            word_list = sentence.get_wordlist(t_type)
            wordcount += len(word_list)

            for i in range(0, len(word_list) - n_ngram + 1):
                ngramma = word_list[i: i + n_ngram] # usiamo il list slicing per selezionare l'ngramma
                nomefeature = f'{t_label.upper()}_{n_ngram}_' + '_'.join(ngramma)
                featuredict[nomefeature] = featuredict.get(nomefeature, 0) + 1 # se la feature è presente nel dizionario allora il conteggio aumenta di 1, se non è presente allora viene aggiunta

        return {featurename: float(value)/float(wordcount) for featurename, value in featuredict.items()}  # normalizzo dividendo per il numero di token totale del documento e restituisco il dizionario di feature

    def get_char_ngrams(self, n_ngram: int) -> dict:
        # estrae gli ngrammi di carattere del documento
        featuredict = {}
        charcount = 0
        for sentence in self.sentenceslist:
            word_list = sentence.get_wordlist('forma')
            char_list = ' '.join(word_list)
            charcount += len(char_list)

            for i in range(0, len(char_list) - n_ngram + 1):
                ngramma = char_list[i: i + n_ngram] # usiamo il list slicing per prendere l'ngramma, ricorda che la fine è esclusa
                nomefeature = f'{n_ngram}_' + '_'.join(ngramma)
                featuredict[nomefeature] = featuredict.get(nomefeature, 0) + 1

        return {featurename: float(value)/float(charcount) for featurename, value in featuredict.items()}


    def get_char_pref_suff_ngrams(self, n_ngram: int) -> dict:
        # estrae gli ngrammi di prefissi e suffissi del documento
        featuredict = {}
        charcount = 0
        for sentence in self.sentenceslist:
            word_list = sentence.get_wordlist('forma')
            char_list = ' ' + ' '.join(word_list)  # metto anche uno spazio prima, così sarà preso il prefisso della prima parola.
            charcount += len(char_list)

            for i in range(1, len(char_list) - n_ngram + 1):  # il range comincia da 1 perchè devo considerare lo spazio che ho aggiunto prima
                ngramma = char_list[i: i + n_ngram] # usiamo il list slicing per prendere l'ngramma, la fine è esclusa
                flag = ' ' not in ngramma
                try:
                    if flag and char_list[i-1] == ' ':
                        nomefeature = f'p{n_ngram}_' + ''.join(ngramma)
                        featuredict[nomefeature] = featuredict.get(nomefeature, 0) + 1

                    elif flag and char_list[i + n_ngram] == ' ':
                        nomefeature = f's{n_ngram}_' + ''.join(ngramma)
                        featuredict[nomefeature] = featuredict.get(nomefeature, 0) + 1
                except IndexError:
                    pass

        return {featurename: float(value)/float(charcount) for featurename, value in featuredict.items()}


class Sentence:
    __slots__ = 'tokenslist'
    # tokenslist è la lista dei token della frase

    def __init__(self, tokenslist: list):
        self.tokenslist = tokenslist

    def __repr__(self):
        return str(self.tokenslist)

    def get_wordlist(self, t_type: str):  # mi serve per ottenere la lista delle parole, o dei lemmi, o dei pos
        return [getattr(token, t_type) for token in self.tokenslist]  # getattr mi permette di prendere l'attributo dandogli il nome come una stringa
