import math
from statistics import median


class CalculateSimilarity:

    @staticmethod
    def sortDict(myDict, lenDict):
        sortDict = {}
        if lenDict is not None:
            sortDict.update(dict(sorted(
                myDict.items(), key=lambda x: x[1], reverse=True)[:lenDict]))
        else:
            return myDict
        return sortDict

    @staticmethod
    def appendAndSum(simList1, simList2, simpFr1, simpFr2):
        simList1.append(simpFr1)
        simList2.append(simpFr2)

    @staticmethod
    def evEdv(dic1, dic2, optDict=None, N=None):
        simpleFr1 = CalculateSimilarity.sortDict(dic1, N)
        simpleFr2 = CalculateSimilarity.sortDict(dic2, N)
        simList1 = []
        simList2 = []
        for val in simpleFr1:
            if val in simpleFr2:
                CalculateSimilarity.appendAndSum(simList1, simList2,
                                                 simpleFr1[val], simpleFr2[val])
        if len(simpleFr1) <= len(simpleFr2):
            return (len(simList1) / len(simpleFr2) * 100), math.fabs(median(simList1) - median(simList2))
        else:
            return (len(simList1) / len(simpleFr1) * 100), math.fabs(median(simList1) - median(simList2))

    @staticmethod
    def xiSqr(dict1, dict2):
        lenD1 = len(dict1)
        lenD2 = len(dict2)
        sumT = 0
        for it in dict1:
            if it in dict2:
                sumT += (1 / (dict1[it] + dict2[it]) *
                         pow((dict1[it] / lenD1 - dict2[it] / lenD2), 2))
        return lenD2 * lenD2 * sumT

    @staticmethod
    def cosFith(dict1, dict2):
        cosChis = 0
        cosZn1 = 0
        cosZn2 = 0
        for it in dict1:
            if it in dict2:
                cosChis += dict1[it] * dict2[it]
                cosZn1 += pow(dict1[it], 2)
                cosZn2 += pow(dict2[it], 2)
        return (cosChis / (math.sqrt(cosZn1) * math.sqrt(cosZn2)))

    @staticmethod
    def jakrdSimWithoutFric(dict1, dict2):
        lenD1 = len(dict1)
        lenD2 = len(dict2)
        sumT = 0
        for it in dict1:
            if it in dict2:
                sumT += 1
        return (sumT / ((lenD1 + lenD2) - sumT))

    @staticmethod
    def jakardWithFric(dict1, dict2):
        fr1 = 0
        fr2 = 0
        sumFr = 0
        for it in dict1:
            fr1 += dict1[it]
            if it in dict2:
                sumFr += dict2[it] + dict1[it]
        for it in dict2:
            fr2 += dict2[it]
        return (sumFr / ((fr1 + fr2) - sumFr)) * 100

    @staticmethod
    def evMet(list1, list2):
        sumT = 0
        for i in range(len(list1)):
            sumT += pow((list1[i] - list2[i]), 2)
        return math.sqrt(sumT)

    @staticmethod
    def compFitch(a1, a2):
        return math.fabs(a1 - a2)

    @staticmethod
    def makeCompDict(dict1, dict2, dict3, N=None):
        simpleFr1 = CalculateSimilarity.sortDict(dict1, N)
        simpleFr2 = CalculateSimilarity.sortDict(dict2, N)
        simpleFr3 = CalculateSimilarity.sortDict(dict3, N)
        opDict = {}
        for val in simpleFr1:
            if (val in simpleFr2
                    and val in simpleFr3):
                if (math.fabs((simpleFr1[val] - simpleFr2[val]) * 1000) < 1
                        and math.fabs((simpleFr2[val] - simpleFr3[val]) * 1000) < 1):
                    opDict[val] = simpleFr2[val]
        return opDict
