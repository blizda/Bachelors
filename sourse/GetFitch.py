import math

class GetFitch:
    def __init__(self, textStrTegget, textStrNotTeggit):
        self.__sentArr = textStrNotTeggit
        self.__textStr = ' '.join(textStrNotTeggit)
        self.__textStrTeggit = ' '.join(textStrTegget)
        self.__ent = None
        self.__fitch = None
        self.__surpris = None
        self.__redab = None
        self.__way_to_lems_dic = 'lems.txt'
        self.__list_of_lems = self.__get_lems__(self.__way_to_lems_dic)

    def __get_lems__(self, way_to_lems_dic):
        lemList = []
        with open(way_to_lems_dic, 'r') as lems_dic:
            for line in lems_dic:
                lemList.extend(line.split())
        return lemList

    def __surprisal__(self, textStr):
        list_of_words_in_text = {}
        bigram_list = {}
        words_in_text = 0
        str_of_text = textStr.split()
        words_in_text += len(str_of_text)
        surprisebl = 0
        for i in range(len(str_of_text)):
            if i > 0:
                if (str_of_text[i - 1] + ' ' + str_of_text[i]) in bigram_list:
                    bigram_list[str_of_text[i - 1] + ' ' + str_of_text[i]] \
                        = bigram_list.get(str_of_text[i - 1] + ' ' + str_of_text[i]) + 1
                else:
                    bigram_list[str_of_text[i - 1] + ' ' + str_of_text[i]] = 1
            if str_of_text[i] in list_of_words_in_text:
                list_of_words_in_text[str_of_text[i]] = \
                    list_of_words_in_text.get(str_of_text[i]) + 1
            else:
                list_of_words_in_text[str_of_text[i]] = 1
        for key in bigram_list.keys():
            sovm = bigram_list[key] / words_in_text
            cont_tok = key.split()
            context = list_of_words_in_text[cont_tok[0]] / words_in_text
            surprisebl += math.log2(1 / (sovm / context))
        return surprisebl / words_in_text

    def __entrop__(self, textStr):
        list_of_words_in_text = {}
        pit_mass = []
        str_of_text = textStr.split()
        words_in_text = len(str_of_text)
        entropy = 0
        for i in range(len(str_of_text)):
            if str_of_text[i] in list_of_words_in_text:
                list_of_words_in_text[str_of_text[i]] = list_of_words_in_text.get(str_of_text[i]) + 1
            else:
                list_of_words_in_text[str_of_text[i]] = 1
        for key in list_of_words_in_text.keys():
            p_i = list_of_words_in_text[key] / words_in_text
            pit_mass.append(p_i)
            entropy += list_of_words_in_text[key] * (p_i * math.log(p_i))
        return (-1) * entropy

    def __readabilyte__(self, textStr):
        words_in_text = 0
        col_slog = 0
        num_sentans = 0
        glas = ['а','у','о','ы','и','э','я','ю','ё','е']
        str_of_text = ' '.join(textStr)
        num_sentans += len(textStr)
        for r in range(len(glas)):
            col_slog += str_of_text.count(glas[r])
        words_in_text += len(str_of_text.split())
        readab = (((words_in_text - num_sentans) / num_sentans) * 0.39) \
                 + (col_slog / (words_in_text - num_sentans)) - 15.59
        if readab < 0:
            return (-1) / readab
        return readab

    def __all_fetches__(self, texStr):
        words_in_text = 0
        kol_lex = 0
        fich = {}
        chasti_rechi = {'NOUN': 0, 'ADJF': 0, 'COMP': 0,
                        'VERB': 0, 'INFN': 0, 'PRTF': 0,
                        'PRTS': 0, 'GRND': 0, 'NUMR': 0,
                        'ADVB': 0, 'NPRO': 0, 'PRED': 0,
                        'PREP': 0, 'CONJ': 0, 'ADJS': 0,
                        'PRCL': 0, 'INTJ': 0}
        list_of_words_in_text = {}
        kol_per_lex = 0
        str_of_text = texStr.split()
        words_in_text += len(str_of_text)
        for i in range(len(str_of_text)):
            minArr = str_of_text[i].split('_')
            str_of_text[i] = minArr[0]
            razb = minArr[1]
            if razb in chasti_rechi:
                chasti_rechi[razb] = chasti_rechi.get(razb) + 1
            else:
                chasti_rechi[razb] = 1
            if str_of_text[i] in list_of_words_in_text:
                list_of_words_in_text[str_of_text[i]] = list_of_words_in_text.get(str_of_text[i]) + 1
            else:
                list_of_words_in_text[str_of_text[i]] = 1
        fich['analit'] = (chasti_rechi.get('PREP') + chasti_rechi.get('CONJ')
                          + chasti_rechi.get('PRCL')) / words_in_text
        fich['glagol'] = (chasti_rechi.get('VERB') + chasti_rechi.get('INFN')
                          + chasti_rechi.get('PRTF') + chasti_rechi.get('PRTS')
                          + chasti_rechi.get('GRND')) / words_in_text
        fich['substat'] = (chasti_rechi.get('NOUN')) / words_in_text
        fich['adjekt'] = (chasti_rechi.get('ADJF') + chasti_rechi.get('ADJS')) / words_in_text
        fich['mestoim'] = chasti_rechi.get('NPRO') / words_in_text
        fich['autosem'] = (words_in_text - (chasti_rechi.get('PREP') + chasti_rechi.get('CONJ')
                                            + chasti_rechi.get('PRCL')) - chasti_rechi.get('NPRO')) / words_in_text
        for key in list_of_words_in_text.keys():
            if (self.__list_of_lems.count(key) == 1):
                kol_per_lex += 1
            kol_lex += 1
        fich['lex_dev'] = kol_lex / words_in_text
        fich['quant_first_lex'] = kol_per_lex / words_in_text
        fich['neznam'] = (chasti_rechi.get('PREP') + chasti_rechi.get('CONJ')
                          + chasti_rechi.get('PRCL') + chasti_rechi.get('NPRO')) / words_in_text
        fich['imen_lex'] = (chasti_rechi.get('NOUN') + chasti_rechi.get('ADJF')
                            + chasti_rechi.get('ADJS')) / words_in_text
        return fich

    @property
    def surprisable(self):
        if self.__surpris is None:
            self.__surpris = self.__surprisal__(self.__textStr)
        return self.__surpris

    @property
    def redab(self):
        if self.__redab is None:
            self.__redab = self.__readabilyte__(self.__textStr)
        return self.__redab

    @property
    def ent(self):
        if self.__ent is None:
            self.__ent = self.__entrop__(self.__textStr)
        return self.__ent

    @property
    def anality(self):
        if self.__fitch is None:
            self.__fitch = self.__all_fetches__(self.__textStrTeggit)
        return self.__fitch['analit']

    @property
    def glagolity(self):
        if self.__fitch is None:
            self.__fitch = self.__all_fetches__(self.__textStrTeggit)
        return self.__fitch['glagol']

    @property
    def substativ(self):
        if self.__fitch is None:
            self.__fitch = self.__all_fetches__(self.__textStrTeggit)
        return self.__fitch['substat']

    @property
    def adjekt(self):
        if self.__fitch is None:
            self.__fitch = self.__all_fetches__(self.__textStrTeggit)
        return self.__fitch['adjekt']

    @property
    def mestoim(self):
        if self.__fitch is None:
            self.__fitch = self.__all_fetches__(self.__textStrTeggit)
        return self.__fitch['mestoim']

    @property
    def autosem(self):
        if self.__fitch is None:
            self.__fitch = self.__all_fetches__(self.__textStrTeggit)
        return self.__fitch['autosem']

    @property
    def lex_dev(self):
        if self.__fitch is None:
            self.__fitch = self.__all_fetches__(self.__textStrTeggit)
        return self.__fitch['lex_dev']

    @property
    def qvont_first_lex(self):
        if self.__fitch is None:
            self.__fitch = self.__all_fetches__(self.__textStrTeggit)
        return self.__fitch['quant_first_lex']

    @property
    def neznam(self):
        if self.__fitch is None:
            self.__fitch = self.__all_fetches__(self.__textStrTeggit)
        return self.__fitch['neznam']

    @property
    def imen_lex(self):
        if self.__fitch is None:
            self.__fitch = self.__all_fetches__(self.__textStrTeggit)
        return self.__fitch['imen_lex']

    @property
    def fitch(self):
        if self.__fitch is None:
            self.__fitch = self.__all_fetches__(self.__textStrTeggit)
        allFitch = {}
        allFitch.update(self.__fitch)
        allFitch['ent'] = self.ent
        allFitch['redab'] = self.redab
        allFitch['surprisable'] = self.surprisable
        return allFitch